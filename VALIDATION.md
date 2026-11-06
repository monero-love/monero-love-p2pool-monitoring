# Packaging validation

Checked on 2026-11-06 UTC.

## Completed

- Source hashes match the recorded source files and download members.
- The source article returned HTTP 200. Both series download bundles matched the live public downloads byte for byte.
- All included JSON and YAML files parsed successfully. Included Python files passed AST parsing.
- Reviewed files for credentials and private infrastructure values. Credential fields contain placeholders, while tests use synthetic values. Localhost, reserved documentation addresses and the article's public Monero Love node are retained where relevant.
- All 7 bundled collector unit tests passed, including malformed input, private-field omission and atomic output handling.

## Limits

No P2Pool instance or monitoring deployment was started. Service-account permissions and API schemas need destination-host checks.

These checks cover packaging and the stated test scope. They do not establish that the examples will work unchanged on a different operating system or service version. See README.md and the source article for installation assumptions.

## Screenshot addition

Added 8 existing public images. All image files decoded successfully, matched their published source bytes and were visually reviewed. Relative README and gallery image links were checked. Source URLs, original dimensions and hashes are recorded in `docs/screenshots/manifest.json`. This change adds documentation and assets only.
