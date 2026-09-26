# Foundation source authoring

Apply the root instructions first. This file specifies the initial card format;
`../schemas/foundation.yaml` is its controlled vocabulary. Production SOURCE is
currently empty. Migration demonstrations belong in `tests/fixtures/`, not here.

## Find, create, and route

Search the generated author index by ID, name, or alias before creating a card.
Until the first SOURCE index exists, use targeted repository search. A card is
`source/<type>/<id>.md`, with YAML frontmatter and optional explanatory Markdown.
The only universal required fields are `id`, `type`, and `name` (nonempty strings).
`aliases` is an optional list of search labels, never alternative canonical IDs.
`provenance` lists migration evidence keys from the baseline; it is author-only.
Machine-addressable facts and assertions live in frontmatter, not duplicated in
the Markdown body. The body may explain causality or refer to those fields.

IDs use a registered prefix and a lowercase ASCII kebab-case slug. Existing
verified IDs take precedence over a newly preferred spelling. In particular,
new material IDs use `doc-`, including the existing `doc-sergey-confession`.
The vocabulary also accepts confirmed historical `material-` and `car-` prefixes.
New slugs are assigned once, not recomputed from a changed name or number plate.
An existing valid identity with another prefix requires extending the schema
before migration, never renaming the ID merely to fit a preferred prefix.
Deferred types in the vocabulary are not yet authorable.

## Initial types and primary owners

| Type | Create when | Required type fields | Data owned here | Route elsewhere |
| --- | --- | --- | --- | --- |
| character | A person has independent identity | None beyond universal fields | Stable personal `facts`, such as birth_date | Life/legal changes → event; vehicle plate → vehicle; confession text → material |
| vehicle | A specific vehicle is independently referenced | None beyond universal fields | `facts.make`, `model`, `registration_plate`, if verified | Changing owner → event; material depiction → relation on material |
| material | An independently identifiable information carrier exists or is planned | `facts.kind`, `created_at` | Its own `claims`, source asset, availability and disclosure rules | Objective occurrence → event; identified person/vehicle → own card |
| event | A bounded world or knowledge change has independent significance | `at`; nonempty `changes` or `knowledge_changes` | Objective effects and/or time-bound knowledge changes | Stable entity facts → target card; material claims → material |
| group | A collective must be an independently addressable observer/participant | None beyond universal fields | Collective identity, e.g. the player investigation group | Individual biography → character; session members/progress → runtime |
| chapter | A period of active play has one input slice | `ordinal`, `input_slice_ref` | Unique positive stage ordinal and link to its input | Calendar anchor and observer → slice; discoveries → knowledge/runtime |
| slice | A chapter needs a reproducible query coordinate | `at`, `observer_ref`, `chapter_ref` | Query coordinate only | Copied states, cards or material lists → derived output |

Fields not applicable to the type are errors. The foundation probe validates
the vocabulary above; adding a new fact key, role or type is a bounded schema
change before authoring it. Empty fields are omitted; missing required data uses
an explicit uncertainty object, never a guessed value.

## Facts, uncertainty, and time

`facts` stores nonchanging values directly. Known but hidden truth remains known
in SOURCE and is excluded by projection. Unknown values are objects with exactly
`status: world_unknown`, `author_undecided`, or `migration_missing`.
These describe different reasons for absence, not visibility levels.

Calendar values are quoted ISO local dates (`2026-03-21`) or local minute
coordinates (`2026-02-23T10:00`). The world calendar's zone has not been assigned
by this foundation. Do not infer it from a user's computer timezone. The probe
does not support mixing timezone offsets, approximate prose dates, or seconds.
An unknown time uses the uncertainty object. Do not turn a day into midnight.

An event owns effects as `changes: [{target_ref, key, value}]`; allowed keys and
values are in the vocabulary. A property with event history must not also be
authored in the target's `facts` or a manual chapter/state timeline. The event
time is the effect's time; do not repeat it for each target. Subsequent events
append changes. Correct a past entry only when correcting an erroneous source
fact with evidence; a new occurrence is a new event.

Intervals `[change, next_change)` are generated, not authored again. Before the
first known change, state is unknown. No initial `alive`, owner, or legal status
is invented. Equal or overlapping imprecise times for competing changes to the
same target/key require source-backed ordering or an open issue. Sorting IDs is
not temporal order. A day represents uncertainty within that day: a query whose
time overlaps an effect cannot choose a precise state. The probe returns an
unresolved marker. An exact minute effect at an equal exact minute query applies.

## Relations

Store `relations: [{type, target_ref, role?}]` only on the primary relation owner.
The source is the enclosing card's ID. Allowed endpoint types and roles are in
the vocabulary. For example, a material owns `depicts`, a vehicle owns
`registered_to`, and an event owns `participant` with actor/victim/witness role.
`registered_to` is registration evidence; it does not by itself assert ownership.
`spouse_of` is stored once; the reverse edge is generated.

For the initial vocabulary, relationships are static. A changing ownership
relationship uses `owner_ref` event effects. Do not attach an invented interval
to a static relation. Other changing relation types require a schema extension
with one temporal owner before migration. No arbitrary synonyms are accepted.

When a linked independently identifiable entity is missing, follow its row in
the type table and create the minimum verified card before linking it. Do not
embed its biography or primary facts in the current card. Do not mint a card to
fill an unidentified person in a photograph. Unresolved identity stays unresolved.

## Knowledge and availability

A material's `claims` maps local assertion keys to the material's statements.
An assertion address is `{owner_ref, key}`, where key is an existing dotted path
(for example `claims.confession_account` or `changes.0.value`). The first refers
to what a document says; the second refers to an objective event effect. A
knowledge record does not copy the primary assertion or change its truth class.

An event may own `knowledge_changes` records with `observer_ref`, `assertion`,
`status` and nonempty `basis_refs`. Status is reported/established/rejected in
that observer's view, not a global truth flag. Its time comes from the event.
The observer is a character or group; the basis references the supporting
material/event. Later knowledge creates another event; it does not rewrite the
material or original world effect. Reinterpreting a material likewise adds a
knowledge record; it does not clone the material. Complex causal versions are
deferred to a separate version type rather than encoded as world changes.

A material optionally owns `availability: {from_chapter_ref, audience_ref}`.
Absent availability means no player delivery. The initial ordinal policy is
monotonic from that chapter for the designated observer; it is a bounded linear
scenario, not a general branching-language implementation. Known creation after
the slice disallows availability. Unknown exact creation time is not a reason to
invent it: existence may be proved by a source-backed bound or package fact.
Production must verify that evidence establishes existence and eligibility for
the query. The TEST probe does not implement a production evidence gate or a
general temporal-bounds schema; it can inspect a source-confirmed chapter rule.

`disclosures: [{observer_ref, assertion, status}]` is an optional material-owned
rule for learning its claim when that material is opened. Its assertion must
address this material's `claims`. The basis is the enclosing material. A
disclosure is evaluated only when availability permits it AND the external
session says it was opened. No `opened`, `seen`, or progress is stored in SOURCE.
Being eligible to receive a confession is not automatically knowing or believing
its contents. Branch-dependent disclosure needs an explicit future condition
model; do not assume all chapter outcomes expose the same knowledge.

## Slice, chapter, and projections

Chapter `input_slice_ref` and slice `chapter_ref` must agree. A slice owns the
calendar coordinate once; the chapter does not repeat it. The query observer is
a character/group. Calendar time determines world state; chapter ordinal gates
materials; observer determines knowledge. These are separate coordinates.

The author index/state view is author-only. A player projection uses an explicit
allowlist of available material IDs/names and permitted knowledge values/statuses.
It never serializes raw cards, author world states, source paths, provenance,
all claims, or hidden reference values and then hides them in the interface.
The foundation probe is a TEST proof, not a production spoiler-safety certifier.
Human review of assertion text and of a real package remains required.

## Local instructions and validation

This shared local file covers the seven initial types without seven repeated
copies of global rules. Add `source/<type>/AGENTS.md` only when that type needs
additional filling rules; deeper files refine this format and root invariants.
Each such file must answer root §18's practical questions. Assets, scenes,
stories and new relation vocabularies require their applicable rules before use.

After a change, validate required/type fields, IDs, references, assertion paths,
temporal consistency, material eligibility and changed dependencies. Review
primary ownership and canonical evidence. Run the focused foundation tests when
schema/projection logic changes. Update only affected derived index entries and
backlinks; never maintain these by hand. See `../README.md` for current commands
and `../migration/README.md` for checks deferred until production migration.
