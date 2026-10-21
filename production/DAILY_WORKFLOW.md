# Daily mirror workflow

Use the official AI-model-latest-radio Site source as the canonical production input. Read its latest saved version and source commit first; copy actual dated source files from that commit rather than reconstructing them from a rendered page. Do not alter the existing Site or the separate ai-business-news repository.

## Issue and research semantics

- Create one issue per Asia/Tokyo confirmation cutoff. The model-series issue date is the confirmation date, not the earliest vendor publication date. Preserve vendor publication dates exactly as shown; do not convert date-only announcements to JST.
- Record the cutoff, official source URLs, publisher dates, checked date, and scope limitations. Attribute product claims to the provider and distinguish them from independent evaluation. Do not infer global absence from a bounded search.
- Preserve prior dated editions. If the same confirmation date already exists, compare its source/research input first: identical inputs are a no-op; materially updated official information updates that same date rather than creating a duplicate.

## Files to mirror

Keep the existing repository structure and latest README conventions. For each confirmed issue, mirror the actual files available in the canonical source commit:

- `editions/YYYY-MM-DD.md`, `.html`, `-script.md`, and `-script.json`
- dated official-source research in `production/YYYY-MM-DD-research.md` and `.json`
- a sanitized `production/YYYY-MM-DD-manifest.json`
- relevant production code/assets needed to explain or reproduce the issue

Do not include `.openai/hosting.json`, personal/local filesystem paths, internal records, account identifiers, access tokens, credentials, secret URLs, private runtime details, or error logs. Keep audio binaries out of GitHub unless explicitly requested; record the publicly verified MP3 URL and SHA-256, and retain clear pending/failed status if no current issue audio was published. Never substitute an older audio file.

## Commit and verification

Prepare all changed paths together in one Git tree and one commit based on the latest `main`. Advance `main` with a non-force compare-and-swap against the exact previously read head SHA. If it changed, re-read and reconcile instead of overwriting. Read back every changed file and verify its content, the resulting commit, and public repository visibility before reporting completion. Keep the confirmation-date semantics above distinct from any other news series.
