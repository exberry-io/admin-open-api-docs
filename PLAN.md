# Exberry API Documentation — Plan

Status: **agreed plan, not yet executed**. Nothing changes until we pick a flag day.

## Where we are today (baseline)

- **Source of truth:** Postman collection (`Exberry Admin API`, v1.58.0)
- **Pipeline:** `spec/postman_to_openapi_generator.py` (v9) converts the Postman export →
  `docs/openapi.json` (OpenAPI 3.0.3, 62 operations, 15 components incl. CandleAdjustment entity)
- **Amendments:** `spec/spec_overrides.json` (info / tags / operations / schema descriptions)
- **CI:** GitHub Actions — validate (swagger-cli) → changelog (oasdiff) → deploy to GitHub Pages
- **Rendering:** Scalar (branded `docs/index.html`), live at GitHub Pages
- **WS APIs:** AsyncAPI 3.0 spec exists for Trading API (createSession / placeOrder / executionReports), not yet rendered/deployed

## Phase 0 — One-time local conversion (NOT in the repo)

The Postman→OpenAPI generator is a migration tool, not permanent infrastructure. It stays
**local only**:

1. Locally: final Postman cleanup (see Phase 2 list) → export → run the generator one last
   time → the resulting `openapi.json` is the artifact that seeds the new repo
2. Keep the generator + final export in a private archive (zip/drive) for provenance —
   they do not enter the new repository

## Phase 1 — New clean repository

Start fresh rather than carrying `Admin-API-Test` history (test commits, CI experiments, stale files).

1. Create repo (suggested name: `exberry-api-docs`; decide public vs private — GitHub Pages
   on the free plan requires **public**)
2. Copy in the curated file set only — note: **no generator, no Postman export**:
   ```
   docs/index.html            docs/openapi.json        ← canonical spec (from Phase 0)
   spec/text-overrides.yaml   spec/apply_text_overrides.py
   .github/workflows/deploy-docs.yml
   README.md  PLAN.md  DECISIONS.md  MAINTENANCE.md
   ```
3. Repo settings: Pages → Source = **GitHub Actions**; branch protection on `main`
   (require PR + 1 review); optionally CODEOWNERS for `docs/` and `spec/`
4. First push → verify CI green → verify live site → update any links pointing at the old repo
5. Archive `Admin-API-Test` (Settings → Archive) with a README pointer to the new repo

## Phase 2 — The flip (happens together with Phase 1)

Because the generator never enters the new repo, the new repo IS the flip: from its first
commit, `docs/openapi.json` is the source of truth.

1. Final cleanup in Postman before the Phase-0 conversion:
   - remove the stray `Test` query param on `POST /api/operations/mass-cancel`
   - (optional) unify API Key endpoint naming; strip inline `NEW/CHANGED` markers
2. Announce to everyone who edits the collection:
   **after the flip, edits in Postman do not reach the docs**

## Phase 3 — Editing model in the new repo

Two kinds of change, two editing surfaces:

1. **Text edits (frequent, low-risk)** — `spec/text-overrides.yaml`:
   descriptions/summaries edited in YAML (block scalars: real multi-line text, comments
   allowed, clean line-level diffs). A small helper `spec/apply_text_overrides.py`
   patches the texts into `docs/openapi.json`; both files are committed together.
   Contract of the overlay (same targets the JSON overrides had):
   ```yaml
   info:
     description: |
       Exberry Admin API allows managing exchange static data...
   tags:
     Authentication: |
       Authenticate with the email and password provided by the Exberry team...
   operations:
     Get_Token:              # operationId
       summary: Get Token
       description: |
         Exchanges email + password for a JWT bearer token.
   schema_descriptions:
     Instrument.properties.symbol: |
       Unique instrument symbol. Max length 16.
   ```
   The YAML is the *editing surface*; `docs/openapi.json` remains the single canonical,
   published file (stable URL, machine/AI entry point). The helper is idempotent —
   re-running it is always safe. CI verifies the overlay is applied (re-runs the helper
   and fails if `openapi.json` changes), so the two files can never drift.

2. **Structural edits (rare)** — new endpoints, fields, enums: edited directly in
   `docs/openapi.json` via PR, following the checklists in MAINTENANCE.md.

3. CI: apply-overlay check → validate → oasdiff as PR review gate → deploy
4. Versioning: bump `info.version` in the same PR as the change; oasdiff output = changelog
5. (Optional) generate a Postman collection FROM the spec (`openapi-to-postmanv2`) for
   anyone who tests manually

## Phase 4 — Extensions (after the flip is stable)

- Render the Trading API AsyncAPI spec as a second page on the same Pages site
- Extend AsyncAPI coverage (cancelOrder, massCancel, replaceOrder, market data)
- Custom domain (e.g. `apidocs.exberry.io`) — CNAME file + one DNS record
- Link reference pages from the GitBook portal (GitBook stays the narrative front door)

## Exit criteria per phase

- P0 done when: final local generation produced from cleaned Postman; generator archived privately
- P1 done when: new repo live (no generator inside), CI green, old repo archived
- P2 done when: flip announced; Postman edits stop reaching docs
- P3 done when: first text edit shipped via text-overrides.yaml AND first structural PR
  merged with the oasdiff gate demonstrated
- P4: each item independently shippable
