# AGENTS.md — Canonical Content Delivery and Paired-Repository Contract

## 0. Authority

This file is the normative cross-repository contract for the paired repositories:

- [bestkvestnn-pixel/dimnadvod](https://github.com/bestkvestnn-pixel/dimnadvod) — canonical content / knowledge repository;
- [bestkvestnn-pixel/test-app](https://github.com/bestkvestnn-pixel/test-app) — interface repository.

The repository-local root instructions remain authoritative inside their own repositories:

- [dimnadvod/AGENTS.md](https://github.com/bestkvestnn-pixel/dimnadvod/blob/main/AGENTS.md)
- [test-app/AGENTS.md](https://github.com/bestkvestnn-pixel/test-app/blob/main/AGENTS.md)

This contract defines the boundary between them.

If a local root instruction conflicts with this contract on a cross-repository matter, stop the cross-repository operation and treat the instruction set as inconsistent. Do not guess which copy was intended.

---

# 1. Fundamental architecture

There is **one authored content database**, not two synchronized story databases.

`dimnadvod` is the only canonical store for:
- world facts;
- entities and stable IDs;
- events, scenes, processes, and temporal states;
- knowledge and interpretations;
- chapters, transitions, slices, and availability rules;
- authored materials and source assets;
- export schemas and projection rules.

`test-app` is an interface repository. It may contain:
- Player App;
- Author Studio;
- application code;
- runtime/session state;
- generated projections and caches;
- tests and fixtures.

It MUST NOT maintain an independent authored copy of the story database.

Core formula:

```text
ONE CANONICAL CONTENT STORE
        │
        ├── author reads/writes
        │
        └── versioned projections
                 ↓
          INTERFACE REPOSITORY
```

---

# 2. Data-flow directions are different operations

Do not model the relationship as `DB A ⇄ DB B`.

There are two distinct flows.

## 2.1. Content delivery

```text
dimnadvod
   ↓ derive/export
versioned content package
   ↓
test-app
```

This is one-way authored-content delivery.

## 2.2. Authoring command

An author-facing UI in `test-app` may initiate an approved canonical change:

```text
Author Studio
   ↓ author command
apply dimnadvod instructions
   ↓
dimnadvod canonical write
```

This is NOT reverse synchronization.

The command must be applied directly to the canonical repository under its root and applicable local `AGENTS.md` rules.

Never stage an authored truth in a second application database and later merge it back as if both sides were peers.

---

# 3. Ownership classes

Every relevant artifact belongs to one ownership class.

## 3.1. SOURCE

Author-maintained canonical content in `dimnadvod`.

SOURCE is the only authored truth.

## 3.2. DERIVED

Generated projections, packages, indexes, JSON, SQLite, search indexes, or app-ready data derived from SOURCE.

DERIVED artifacts:
- are disposable;
- can be regenerated;
- MUST NOT be edited as canon;
- should identify their source revision and schema version.

## 3.3. APP CODE

Interface implementation owned by `test-app`.

Examples:
- components;
- routes;
- styles;
- rendering;
- storage mechanics;
- client adapters.

APP CODE is not canon.

## 3.4. RUNTIME

State of a particular play session.

Examples:
- opened/seen materials;
- current UI progress;
- submitted answers;
- session flags;
- preferences;
- local saves.

RUNTIME is not authored story truth.

## 3.5. TEST

Fixtures, prototypes, debug data, and temporary experiments.

TEST data must be physically and semantically isolated from production-derived content.

---

# 4. State ownership: never duplicate the hard part

The canonical temporal/knowledge model exists only in `dimnadvod`.

Do not independently author in `test-app`:
- Chapter 1 character state;
- Chapter 2 character state;
- world-state copies;
- player-knowledge copies;
- availability copies;
- alternative timelines representing later discovery.

The canonical source stores the underlying changes:
- events/scenes;
- temporal state changes;
- knowledge changes;
- availability rules;
- interpretations.

Chapter/player views are derived projections.

Conceptual flow:

```text
EVENTS / SCENES
      ↓
WORLD STATE
      ↓
KNOWLEDGE + AVAILABILITY
      ↓
SLICE / QUERY COORDINATE
      ↓
PLAYER PROJECTION
      ↓
test-app
      ↓
SESSION RUNTIME
```

The application may cache the resulting projection, but the cache is DERIVED.

RUNTIME may record that a player has opened a material; it must not redefine whether the material canonically exists or under which conditions it becomes available.

---

# 5. Stable IDs cross the repository boundary unchanged

Canonical entity IDs defined in `dimnadvod` must remain unchanged in derived packages and application consumers.

Do not create convenience aliases as replacement identities.

Example:

```text
char-sergey-akunin
```

must not silently become:

```text
sergey
```

when referring to the same canonical person.

If another independently identifiable entity exists, give it its own ID and link it explicitly.

Example:

```yaml
id: social-sergey-akunin
owner_ref: char-sergey-akunin
```

Source file paths, display names, handles, and UI labels are not identity anchors.

---

# 6. Versioned content dependency

`test-app` should be able to identify exactly which canonical content revision it consumes.

The target design is a machine-readable lock/manifest equivalent to:

```json
{
  "source_repository": "bestkvestnn-pixel/dimnadvod",
  "source_revision": "<commit SHA>",
  "schema_version": 1,
  "package_hash": "<hash>"
}
```

The exact filename and implementation may evolve, but the invariant is mandatory:

> A built/tested interface version must be reproducibly tied to an exact canonical content revision.

Generated caches are not the dependency declaration; the lock/manifest is.

---

# 7. Incremental delivery by default

Content delivery MUST start from a known baseline and compute a delta.

Normal sequence:

```text
KNOWN CONTENT REVISION
        ↓
COMPARE WITH CURRENT CANON REVISION
        ↓
LIST CHANGED SOURCE PATHS
        ↓
READ CHANGED INSTRUCTIONS/SCHEMAS FIRST
        ↓
READ CHANGED SOURCE CONTENT
        ↓
EXPAND ONLY REQUIRED DEPENDENCIES
        ↓
RECOMPUTE ONLY AFFECTED PROJECTIONS
        ↓
VALIDATE
        ↓
PUBLISH
        ↓
UPDATE CONTENT LOCK/MANIFEST LAST
```

Do not reread or rebuild everything for a routine local change.

A full scan/rebuild is justified only when:
- no trustworthy baseline exists;
- dependency/index state is missing or corrupt;
- a global schema/projection rule changed;
- impact cannot be bounded safely;
- the user explicitly requests a full audit/rebuild.

---

# 8. Instruction-first rule

If a delta changes any applicable:
- root `AGENTS.md`;
- local `AGENTS.md`;
- template;
- schema;
- role dictionary;
- index rule;
- export/projection rule;
- validator;

read and apply the changed instruction before processing data under its scope.

A rule-text change does not automatically require mass migration. Determine actual impact first.

---

# 9. Paired instruction maintenance

The paired instruction set consists of:

1. [dimnadvod/AGENTS.md](https://github.com/bestkvestnn-pixel/dimnadvod/blob/main/AGENTS.md)
2. [test-app/AGENTS.md](https://github.com/bestkvestnn-pixel/test-app/blob/main/AGENTS.md)
3. this contract: `dimnadvod/contracts/content-delivery/AGENTS.md`

When a change affects a shared architectural boundary, the same operation MUST check all three files for required updates.

Shared-boundary topics include:
- repository roles;
- canonical ownership;
- content delivery direction;
- Author Studio canonical writes;
- stable ID rules across repositories;
- state/projection ownership;
- content revision locking;
- generated/runtime boundaries;
- cross-repository update protocol.

Do not mechanically make all three files identical.

Instead:
- update this contract for shared rules;
- update each root only where its local responsibilities or references changed;
- leave unrelated local rules untouched.

If only one file can be updated, explicitly mark the paired instruction set as requiring follow-up before the next cross-repository delivery. Do not silently leave contradictory instructions.

---

# 10. Application-created authored material

If a photo, document, text, or other material is created while working inside `test-app`, first classify its intended role.

## Test/runtime-only

If it is only:
- a UI fixture;
- visual prototype;
- debug artifact;
- temporary mock;

keep it in TEST/APP scope. It does not enter canon.

## Intended canonical material

If the author decides it is part of the game world or authored material set:

1. treat the UI action as an authoring command;
2. read `dimnadvod/AGENTS.md`;
3. read the applicable local source instruction, such as Materials `AGENTS.md`;
4. resolve referenced entities through stable IDs/index;
5. create/update the canonical material and source asset in `dimnadvod`;
6. validate the canonical change;
7. derive the relevant application projection;
8. update the consumed content revision.

Do not first establish the material as authored truth inside an application-owned database.

---

# 11. Generated data boundary

Derived application content should live in a clearly identified generated/cache boundary.

It may be committed or uncommitted depending on implementation, but its authority does not change.

A manually edited derived file is **generated drift**, not a canonical edit.

If derived content is wrong:
1. classify whether the owner is SOURCE, projection/export logic, or UI rendering;
2. fix the owning layer;
3. regenerate only affected outputs.

---

# 12. Runtime protection

Content updates MUST NOT casually overwrite session state.

When compatible, preserve:
- unlocked materials;
- seen state;
- answers;
- progress;
- preferences;
- saves.

If a new content/schema version requires migration:
1. define an explicit migration;
2. scope it narrowly;
3. preserve user data whenever possible;
4. test old-save compatibility.

Do not reset the entire runtime merely because canonical content changed.

---

# 13. Deletions and renames

Stable IDs are the identity anchor.

- A source path rename with unchanged ID is not a new entity.
- A deleted SOURCE entity must remove/update only affected derived references.
- Delivery must leave no dangling canonical IDs.
- A renamed display label must not require runtime identity migration when ID is unchanged.

---

# 14. Binary assets

For images, PDF, audio, video, and other large assets:

1. compare SHA/hash/version first;
2. transfer only new or changed binaries;
3. do not recopy unchanged bytes;
4. metadata-only changes must not force binary retransmission;
5. source assets remain owned by `dimnadvod`; application delivery copies remain DERIVED.

---

# 15. Conflict classes

## 15.1. Canonical source conflict

Competing canonical edits occurred in `dimnadvod`.

Resolve using canonical ownership and instruction hierarchy. Do not use app data as a tie-breaker.

## 15.2. Generated drift

A derived application artifact was manually changed.

Do not import it into canon automatically.

## 15.3. Runtime incompatibility

New content is incompatible with saved session state.

Resolve through runtime migration.

## 15.4. Contract/instruction mismatch

The paired root instructions and this contract disagree on a shared boundary.

Stop cross-repository delivery until the instructions are reconciled.

## 15.5. Schema mismatch

Source projection schema and application consumer schema are incompatible.

Stop publication. Do not guess field meaning.

---

# 16. Atomic publication

Preferred order:

1. determine delta;
2. compute affected projections;
3. validate generated content;
4. validate canonical IDs/references;
5. stage/copy changed assets;
6. publish changed outputs;
7. run targeted consumer tests;
8. update content lock/manifest **last**.

If validation fails:
- do not advance the consumed canonical revision;
- do not claim successful delivery;
- preserve the last known valid app/content pairing when possible.

---

# 17. Minimal-write rule

If recomputation produces byte/content-identical output:
- do not rewrite it;
- do not create a noisy commit;
- do not refresh timestamps merely because the generator ran.

The same principle applies to instruction mirrors and indexes.

---

# 18. Completion criteria

A cross-repository content update is complete only when:

1. canonical delta is known;
2. changed instructions were read first;
3. affected SOURCE was read;
4. required dependencies were resolved;
5. only affected projections were recomputed;
6. IDs and references validate;
7. required assets exist;
8. runtime state was preserved or explicitly migrated;
9. targeted app tests pass;
10. content lock/manifest points to the exact canonical revision;
11. paired instructions remain mutually consistent.

---

# 19. Short formula

> **One canonical database.**

> **Two repositories with different responsibilities.**

> **Authoring commands may originate in an interface, but canonical writes land in dimnadvod.**

> **State is authored once and projected, not duplicated by chapter or repository.**

> **Generated content is disposable. Runtime state stays runtime.**

> **Shared instruction changes are checked across both roots and this contract.**
