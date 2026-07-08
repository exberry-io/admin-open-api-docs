# API Docs — Day-to-Day Manual

How to keep the published OpenAPI docs live and correct in the new repository.
Source of truth: `docs/openapi.json`. Text editing surface: `spec/text-overrides.yaml`.
The Postman flow is retired — edits in Postman do NOT reach the docs.

---

## Task 1 — Fix or improve wording (the frequent case)

Edit `spec/text-overrides.yaml` — never the JSON — then apply and push:

```powershell
cd C:\Apps\exberry-api-docs

# 1. edit spec\text-overrides.yaml   (multi-line text, comments allowed)
# 2. apply the overlay into the spec:
python3 spec\apply_text_overrides.py

# 3. ship (commit BOTH files together):
git add spec\text-overrides.yaml docs\openapi.json
git commit -m "docs: improve <what> description"
git push
```

Overlay sections and targets:

| Section | Targets | Example key |
|---|---|---|
| `info` | API intro | `description` |
| `tags` | section intros | `Authentication` |
| `operations` | summary/description per operation | `Get_Token` (operationId) |
| `schema_descriptions` | one field's description | `Instrument.properties.symbol` |

Writing rules:
- Use `|` block scalars for multi-line text; each sentence on its own line diffs cleanly
- Descriptions are **Markdown**: blank line = paragraph, `- ` = bullets;
  a single line break alone does not render as one
- The apply script is idempotent — running it twice is always safe
- CI re-runs the script and **fails the build if you forgot to apply or to commit both files**

## Task 2 — Structural change (new endpoint / field / enum value)

Edit `docs/openapi.json` directly via a PR. Bump `info.version` in the same PR.

**New endpoint:** add under `paths` with `operationId`, `summary`, `tags` (existing tag),
request/response schemas (`$ref` a component if entity-shaped), one example, and the five
standard error `$ref`s — copy a neighboring operation as a template.

**New field on a model:** add under the component's `properties`; if mandatory, add to
`required`. Enums get `enum` + `x-enumDescriptions`. Stringified numbers get the standard
pattern (`^-?[0-9]+$` int, `format: decimal` + pattern for decimals). Epoch times get
`x-epoch-unit` + a "Unix epoch time in ..." note in the description.

**New enum value:** append to `enum` AND `x-enumDescriptions` (and to the description
bullets where present — e.g. `permissions`).

**Review:** the PR's CI runs oasdiff against `main` — read its output as part of review.
Removed fields / changed types are breaking changes and must be intentional.

## Task 3 — Release notes

The oasdiff output in each Action run IS the changelog (added / removed / changed
operations and fields). Copy it into release notes; no inline `NEW vX.Y` markers in
descriptions anymore.

---

## CI — what every push does

1. **Overlay drift check** — re-applies `text-overrides.yaml`; fails if `openapi.json` differs
2. **Validate** — a broken spec never deploys
3. **oasdiff vs previous** — changelog + breaking-change surfacing
4. **Deploy** — GitHub Pages, live ~1 minute later (hard-refresh when checking)

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Python was not found` | use `py` instead of `python3`, or install from python.org with "Add to PATH" |
| CI fails on overlay drift | you edited YAML but didn't run the apply script, or edited a text directly in the JSON — run `python3 spec\apply_text_overrides.py`, commit both |
| Overlay warning: path not found | the operationId / dotted schema path in the YAML doesn't exist in the spec — check spelling |
| Deploy fails: "Multiple artifacts" | never Re-run jobs; trigger a fresh run (Actions → Run workflow, or empty commit) |
| Deploy fails: "Get Pages site failed" | Settings → Pages → Source = GitHub Actions |
| Node deprecation warnings in CI | informational; bump `actions/*` versions when convenient |

## Rules of thumb

- `docs/openapi.json` is canonical and published; its URL is the machine/AI entry point — keep it stable
- Text goes through the YAML overlay; structure goes through PRs on the JSON; nothing else edits the spec
- Unexplained large growth of `openapi.json` in a diff = stop and investigate before shipping
- One canonical name per script/file in the repo; version suffixes only in downloads

## Quick reference

| Thing | Where |
|---|---|
| Live docs | `https://<org>.github.io/<repo>/` |
| Published spec | `.../openapi.json` |
| Text edits | `spec/text-overrides.yaml` + apply script |
| Branding (colors/logo) | `docs/index.html`, BRAND TOKENS block |
| CI definition | `.github/workflows/deploy-docs.yml` |
| Changelog | oasdiff output in each Action run |
| Decisions & rationale | `DECISIONS.md` · Plan: `PLAN.md` |
