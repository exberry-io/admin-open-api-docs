# Exberry Admin API — Documentation

Interactive API reference rendered by [Scalar](https://github.com/scalar/scalar) (MIT),
deployed to GitHub Pages by CI on every push to `main`.

**Source of truth: `docs/openapi.json`.** There is no upstream generator — the spec is
edited here, via pull requests. (The one-time Postman→OpenAPI migration tooling is
archived outside this repository.)

## Layout

```
docs/
  openapi.json                 the spec — canonical, published (stable URL)
  index.html                   branded Scalar page (BRAND TOKENS block for colors/logo)
spec/
  text-overrides.yaml          editing surface for descriptions (Markdown, multi-line)
  apply_text_overrides.py      applies the overlay into openapi.json (idempotent)
.github/workflows/
  deploy-docs.yml              drift check -> validate -> oasdiff -> deploy
PLAN.md · DECISIONS.md · MAINTENANCE.md
```

## Editing

- **Wording / descriptions** → edit `spec/text-overrides.yaml`, run
  `python3 spec/apply_text_overrides.py`, commit **both** files.
- **Structure** (endpoints, fields, enums) → edit `docs/openapi.json` via PR and bump
  `info.version`. Checklists in `MAINTENANCE.md`.

CI fails the build if the overlay and the spec drift, if the spec is invalid, and it
prints an oasdiff changelog (your release notes) on every push.

## Why things are the way they are

See `DECISIONS.md` — 14 recorded decisions with rationale (component architecture,
enum policy, vendor extensions, format choice, and the operational lessons).
