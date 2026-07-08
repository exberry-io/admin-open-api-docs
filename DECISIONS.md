# Decision Log — Exberry API Documentation

Format: decision → rationale → considerations/trade-offs accepted. Numbered for reference.

## 1. Scalar for REST docs rendering
**Decision:** Scalar (open source) on GitHub Pages.
**Why:** free, modern UI, interactive try-it client, single-file embed, no vendor lock-in (one `<script>` tag to swap).
**Trade-off:** self-hosted branding instead of Scalar's hosted platform (whose custom branding is paid).

## 2. OpenAPI 3.0.3 generated from Postman (migration period)
**Decision:** Python generator converts the Postman collection; Postman remains source of truth until the flip.
**Why:** preserves the team's current workflow while producing a machine-readable spec; migration is incremental.
**Trade-off:** the generator encodes ~10 versions of parser heuristics for the docs' markdown conventions (3 table header styles, 2 nesting styles, 4 enum documentation styles). This complexity is the standing argument for Phase 3.

## 3. Shared models in components (`$ref` everywhere)
**Decision:** one named component per resource (Instrument, Calendar, MP, …), referenced from requests AND responses; `id` marked `readOnly` instead of separate request/response models.
**Why:** single source of truth per entity; clean SDK generation; Models section in Scalar; ~2,000 fewer duplicated lines.
**Trade-off:** response wrappers stay inline (only entity-shaped nodes are `$ref`'d, detected by ≥70 % property overlap).

## 4. Not every enum becomes a model
**Decision:** components only for resource models + the three instrument classification enums (Category / SubCategory / UnderlyingAssets). All other enums inline on their fields.
**Why:** components are justified by reuse, domain-vocabulary status, or centrality — not by being an enum. Over-hoisting turns the Models sidebar and generated SDKs into a junk drawer.
**Rule:** promote an enum only when observed reuse appears (≥2 reference sites), not preemptively.

## 5. Enum value meanings: `x-enumDescriptions` + description bullets where needed
**Decision:** structured `x-enumDescriptions` map on enums; separator `VALUE: meaning`; for array-item enums (where Scalar does not render the extension, e.g. `permissions`) the meanings are additionally listed as markdown bullets in the property description.
**Why:** structured for tools/AI, visible for humans; Scalar renders the extension on directly-displayed string schemas only.
**Note:** a global toggle `ENUM_MEANINGS_IN_DESCRIPTION` in the generator can force bullets everywhere.

## 6. Mutual exclusivity via `x-mutually-exclusive` (not `allOf/not`)
**Decision:** pairs like `dailyMaxPriceAbsolute` / `dailyMaxPricePercentage` are declared in a vendor extension; prose stays in field descriptions.
**Why:** the JSON-Schema-correct `allOf: [{not: {required: […]}}]` renders as a mess in Scalar ("Not object / Empty object").
**Trade-off accepted:** no automatic client-side validation of the rule; the server enforces it anyway.

## 7. Open-set enums are NOT closed
**Decision:** when docs list values but reference an open set ("Trade Types on Trade Entry"), no `enum` is emitted.
**Why:** a wrong restrictive enum makes validators reject valid requests — worse than no enum.

## 8. Optionality is structural; prose markers removed
**Decision:** `required` arrays / `required:false` carry optionality; `` `Optional` `` markers are stripped from descriptions. Conditionally-mandatory fields ("Mandatory if …") are NOT in `required` (OpenAPI 3.0 can't express conditions); the condition stays in the description.
**Injection rule:** documented-but-not-exampled fields are injected into schemas only if optional and from the endpoint's own folder — a mandatory field missing from the example is treated as a docs bug, not silently added.

## 9. Standard error responses shared; examples trimmed
**Decision:** 400/401/403/404/500 live once in `components/responses` ($ref'd by all 62 ops); example arrays capped at 2 items; field tables stripped from operation descriptions once their content is in schemas (error-code tables kept).
**Why:** removed ~40 % of file size with zero information loss (the one exception found — Get Instruments filters — was promoted to proper query parameters instead).

## 10. Text amendments via `spec/text-overrides.yaml` (successor of spec_overrides.json)
**Decision:** description/summary edits are made in a YAML overlay (block scalars: real
multi-line text, comments, line-level diffs) and applied into `docs/openapi.json` by a small
idempotent helper script; both are committed together and CI fails if they drift.
Structural changes are edited directly in the JSON.
**Why:** text edits are the frequent, multi-author operation and deserve the safest editing
surface; JSON's single-line strings make them error-prone. Structural edits are rare and
tool-assisted, so JSON is acceptable there.
**Trade-off:** two files instead of one — mitigated by the CI drift check.

## 11. Flat tags, no folder hierarchy
**Decision:** one tag per top-level Postman folder; `x-tagGroups` tried and rolled back.
**Why:** the two-level ceiling of OpenAPI grouping made parent/child rendering awkward for this API's shape; flat with tag descriptions reads better. Reversible any time.

## 12. RESOLVED — source format after the flip: JSON canonical + YAML text overlay
**Decision:** `docs/openapi.json` stays the single canonical, published spec (stable URL,
machine/AI entry point). YAML enters only where it earns its keep: `spec/text-overrides.yaml`
as the editing surface for descriptions (see #10).
**Why:** the pain of JSON is concentrated in long-string text edits, and the overlay solves
exactly that without a full-format migration, format-conversion tooling, or breaking the
published URL. Full-YAML remains available later if structural editing frequency ever grows.
**Reversibility:** high — the overlay can be folded in and dropped at any time.

## 13. New clean repository — WITHOUT the generator
**Decision (planned):** start a fresh repo for production; archive `Admin-API-Test`.
The Postman→OpenAPI generator and the Postman export do NOT enter the new repo — the
conversion is a one-time local action; generator + final export are archived privately
for provenance.
**Why:** test-phase history and migration tooling don't belong in the long-lived repo;
clean history makes oasdiff-per-commit meaningful from day one, and the repo's file set
states clearly what the source of truth is (the spec, nothing upstream of it).

## 14. WebSocket APIs: AsyncAPI 3.0
**Decision:** AsyncAPI 3.0 for Trading/Market Data (request-reply support fits the sid-correlated RPC style); GitBook remains the narrative front door; reference sections generated from specs.
**Why:** same spec-first benefits as OpenAPI for the REST side; only serious standard for event-driven APIs.

## Operational lessons (keep honoring)
- Every `open()` in tooling: `encoding='utf-8'` (Windows cp1252 default bit us); `ensure_ascii=False` on output.
- GitHub Pages: after a failed deploy, trigger a **fresh run** — never "Re-run all jobs" (duplicate-artifact error).
- One canonical script name in the repo; version suffixes only in downloads.
- When the generated artifact's size jumps unexpectedly, investigate before shipping — a +500-line surprise caught a real regression once.
