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

## 15. Property display order: renderer defaults (required first, then alphabetical)
**Decision:** keep Scalar's default ordering — `orderRequiredPropertiesFirst: true`,
`orderSchemaPropertiesBy: 'alpha'`. No overrides in `docs/index.html`.
**Why:** an integrator's first question is "what must I send?" — grouping required
properties at the top answers it at a glance, and alphabetical order within each group
makes any specific field findable without knowing the source layout. The alternative
(`'preserve'`) would honor the hand-authored grouping in the source tables (e.g. `trigger`
next to its dependent `days`/`startTimes`), but that benefit is smaller than predictability.
**Consequences:** display order is independent of property order in `docs/openapi.json` —
no need to maintain deliberate ordering when adding fields; related-field context lives in
descriptions (e.g. "Mandatory if trigger = TimeBased"), not adjacency.
**Reversal:** two config lines in `docs/index.html` (`orderSchemaPropertiesBy: 'preserve'`,
`orderRequiredPropertiesFirst: false`) — pure rendering change, no spec impact.

## 16. Descriptions are verbatim from the Postman collection
**Decision:** the generator does NOT strip version markers (`NEW v1.x`, `CHANGED v1.x`,
`DEPRECATED v1.x`) or otherwise editorialize description text. Whatever the collection says
is what the spec says. Markers are curated **at the source**, in Postman.
**Why:** marker-stripping rules cannot distinguish a marker the team wants kept from one it
wants gone, and they silently diverge from the source. Editing in Postman puts that judgement
where it belongs and keeps the collection the single truth for prose. (Confirmed in the 1.59
pass: markers the team had cleaned disappeared; markers deliberately kept survived.)
**Exception:** field-level markers consumed as *flags* (`read-only`, `Optional`,
`DEPRECATED` on a field name) are removed from the rendered name/description, because their
meaning has moved into a schema keyword — see #8 and #17.

## 17. `readOnly` is derived from path parameters (plus explicit source markers)
**Decision:** two complementary mechanisms mark a property read-only:
1. an explicit `` `read-only` `` marker in the Postman field table (e.g. `secret`, `apiKey`,
   `ownerId`, `ownerType`);
2. automatic inference — a model property is read-only when its name matches a **path
   parameter of the endpoints that use that model** (e.g. `MpApiKey.mpId`, supplied via
   `/api/mps/{mpId}/api-keys`), plus the standing `id` rule.
Read-only properties are excluded from `required`.
**Why:** a value supplied through the URL is not part of the request body, so listing it in
the body's `required` asserts something false. The requirement is already expressed once and
correctly — on the path parameter (`required: true`). Deriving from the path shape rather
than a hand-placed marker means it cannot drift when endpoints move.
**Scoping matters:** inference is per-model, not global — `Account.mpId` stays writable and
required, because accounts live at `/api/accounts` where `mpId` is not a path parameter.
**Note:** `MpGroupApiKey.mpGroupId` is declared read-only explicitly, since the path
parameter (`groupId`) and the property (`mpGroupId`) differ in name.
**Considered and rejected:** keeping a read-only property in `required` (spec-legal — the
requirement then applies to responses only) because many renderers and generators ignore
that subtlety and still show a "required" badge on the request body.

## 18. Entity CRUD responses reference the model, by path — not by example overlap
**Decision:** for entity CRUD paths, the 200 response schema points at the model regardless
of how abbreviated the saved Postman example is: single entity → `$ref`; bare array →
`items: $ref`; list wrapper (`{entities: [], totalCount}`) → the array's `items: $ref`.
**Why:** the API returns the full entity on create/update/get (confirmed against the live
API), but many saved examples echo only 3–5 fields, so the earlier ≥70 %-overlap heuristic
declined to substitute the model and 24 responses were under-documented. Deciding by path
rather than by example makes the schema state the contract while examples stay illustrative.
Side effect: ~24 KB smaller spec (fewer duplicated inline schemas).
**Excluded — action sub-resources**, which return their own small payloads:
`POST …/{id}/archive` (empty object), `POST …/{id}/end-of-day` (`{id, lastEodDate}`),
`PUT …/candle-adjustments`.

## 19. `MpGroupApiKey` is a standalone model (documented exception to #3)
**Decision:** MP Group API keys are modeled as their own schema rather than an
`allOf` alias of `MpApiKey`. It carries only the applicable fields — `label`, `permissions`
(8-value group subset enum), `mpGroupId`, `apiKey`, `secret`, `ownerId`, `ownerType` — and
omits `mpId`, `accountId`, `allowedInstrumentGroupIds`, `cancelOnDisconncet`.
**Why:** OpenAPI 3.0 `allOf` can only add properties, never remove them, so an alias would
keep advertising four fields that do not apply to group keys.
**How the DRY benefit is retained:** the shared field definitions are **copied from
`MpApiKey` at generation time**, so constraint or description changes in Postman propagate
automatically. The `permissions` description is deliberately short and points to `MpApiKey`
for the full per-permission list.

## 20. API-key paths render after their parent entity's CRUD operations
**Decision:** generated path order places `…/api-keys` sub-resources after the parent
entity's own operations (for both MPs and MP Groups).
**Why:** depth-first traversal of the Postman folders emitted the `API Key` subfolder before
its parent's endpoints, so the docs opened with API-key operations before the entity itself.
Ordering is presentation-only — it does not affect the contract.

## Operational lessons (keep honoring)
- Every `open()` in tooling: `encoding='utf-8'` (Windows cp1252 default bit us); `ensure_ascii=False` on output.
- GitHub Pages: after a failed deploy, trigger a **fresh run** — never "Re-run all jobs" (duplicate-artifact error).
- One canonical script name in the repo; version suffixes only in downloads.
- When the generated artifact's size jumps unexpectedly, investigate before shipping — a +500-line surprise caught a real regression once.
- **Until the Phase-0 flip, every spec fix belongs in the generator, never only in `openapi.json`.** Hand edits are erased by the next run — this bit twice (the API-key naming, and the `statuses` enum).
- **Check the source before "fixing" the output.** If unexpected text appears in the spec, grep the collection for it first; several rounds were lost stripping a marker that a stale local copy — not the real source — contained.
- Keep exactly one collection export in the working directory. Two versions of the same file is how the wrong input gets read and the wrong conclusion drawn.
