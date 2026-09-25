# AGENTS.md — Root Instructions for the New "Дым над льдом" Story Database

## 0. Purpose

This repository is a test implementation of a new file-based standard for a narrative/story database.

The root `AGENTS.md` defines the **system-wide invariants**: how agents must understand the world, entities, time, chapters, transitions, knowledge, materials, and links between cards.

It must not contain detailed filling rules for every entity type. Type-specific rules belong in local `AGENTS.md` files inside the relevant sections of the database.

The primary architectural goal is:

> Any new fact, document, character, scene, or change must be added correctly without rereading the entire database.

To achieve this, an agent must work through:
1. the root rules;
2. the nearest applicable local `AGENTS.md`;
3. stable IDs and the entity index;
4. only the related cards actually needed for the operation.

### 0.1. Language and authority

The normative agent instructions are written in English.

- `/AGENTS.md` and local files named exactly `AGENTS.md` are normative instruction sources.
- Russian translations under `/docs/` are human-readable reference copies only.
- A translated copy MUST NOT be used as an instruction source unless the user explicitly asks to inspect, compare, or update that translation.
- If a translation and the English source differ, the English source always wins.
- Do not maintain independent rule sets in multiple languages.
- A translation should identify the exact source revision/blob it mirrors so staleness can be detected automatically.

---

# 1. Instruction hierarchy

When working with any file, instructions apply in this order:

1. root `/AGENTS.md`;
2. the nearest local `AGENTS.md` for the relevant section;
3. a deeper local `AGENTS.md`, if present;
4. the template for the concrete entity type;
5. the entity card or material itself.

The root `AGENTS.md` defines global invariants and cannot be overridden by a local instruction.

A local `AGENTS.md`:
- refines rules for a specific data type;
- defines required fields;
- explains where new information belongs;
- explains when a separate entity must be created;
- defines allowed roles and relation types;
- must not restate the entire global architecture.

If a local instruction conflicts with the root instruction, the root instruction wins.

If a separate `CLAUDE.md` or another tool-specific adapter is required, it must be derived from `AGENTS.md` and must not create an independent rule set.

---

# 2. Core principle: one world

The database contains **one objective history of the world**.

Do not create separate realities for Chapter 1, Chapter 2, the finale, the players, the investigation, or the author.

The past is not rewritten because new information appears later.

If a fact happened on 2025-09-03, it remains a fact of 2025-09-03 in every later state of the database.

What may change later:
- knowledge about the fact;
- evidentiary status of the fact;
- material availability;
- interpretation of the fact;
- an official version;
- a character's belief;
- the players' belief.

The already occurred fact itself does not change.

Key formula:

> **There is one world. World states change over time. Knowledge about the world changes separately.**

---

# 3. Entity and card

A independently identifiable element of the world receives its own entity and stable ID.

Examples:
- character;
- specific vehicle;
- place;
- organization;
- significant object;
- material;
- scene;
- event;
- process;
- story;
- version;
- chapter;
- transition;
- slice.

The criterion for creating a card is **independent identity**, not current narrative importance.

If an object can:
- have its own history;
- change state;
- appear in multiple materials;
- participate in multiple stories;
- receive incoming links;

then creating a separate entity is preferred.

Do not create a separate card for every incidental detail if it has no independent identity and is not reused.

---

# 4. Stable ID is more important than the file name

Every managed entity must have:
- `type`;
- a stable `id`;
- a display name.

The ID does not change when:
- the file is renamed;
- a character changes surname;
- the display name is refined;
- the card is moved;
- the visual representation changes.

Machine-readable relations must rely on IDs.

Readable Markdown/Wikilink links may be used as a navigation layer, but they must not be the only machine address of an entity.

---

# 5. One fact — one primary owner

Do not store the same exact fact as an independent truth in multiple cards.

Every exact fact should have a primary owner.

Examples:
- the exact timestamp of a camera frame belongs to the camera material or a linked event;
- a birth date belongs to the character card;
- a registration plate belongs to the vehicle card;
- the content of a confession belongs to the confession material;
- the fact of a murder belongs to the scene/event and objective story, not independently to every participant card.

Other cards may:
- link to the primary source;
- show a short derived view;
- receive automatic backlinks.

If new information already exists as a primary fact, do not create another independent copy; create a relation.

---

# 6. Relations must be typed

A relation is more than a name mention.

Where practical, every meaningful relation should have:
- a source;
- a relation type;
- a target entity;
- an optional role;
- an optional validity interval.

Examples:
- a character owns a vehicle;
- a character is depicted in a photograph;
- a character authored a letter;
- a character is interrogated;
- a scene happens at a place;
- a material records a scene;
- a story includes a scene;
- a document is available from a specific chapter;
- new information reinterprets an old material.

Do not invent free-form synonymous role names when the standard already defines a controlled term.

---

# 7. Do not read the entire database unless necessary

Reading the whole database is not the normal way to add or modify an entity.

Before an operation, the agent must:

1. determine the type of the entity being changed;
2. read the root `AGENTS.md`;
3. read the local `AGENTS.md` for that type;
4. find the entity by ID, name, or alias through the index, if the index exists;
5. open the entity itself;
6. open only the related cards required for the task;
7. if an entity of another type is encountered, follow that type's local `AGENTS.md`;
8. after the change, validate links and schema.

If the index is not implemented yet, repository search by ID/name may be used temporarily. Once the index exists, a full file scan for a routine operation is considered the wrong path.

---

# 8. Time: one calendar timeline for the world

The entire story exists on one objective calendar timeline.

An entity or material may have several distinct temporal properties on that timeline.

Do not mix them.

## 8.1. World time

When the actual event happened or a state was valid.

Examples:
- murder;
- vehicle ownership;
- employment;
- death;
- legal-status change.

## 8.2. Material creation/recording time

When a document, photograph, recording, letter, protocol, or other material came into existence.

## 8.3. Knowledge time

When a particular character, group, investigation, or the players learned a specific assertion.

## 8.4. Game availability

From which game stage a material is available to players.

These times may differ.

Example:

> An event happened in 2025, a document was created in 2026, and players first receive it in Chapter 2.

This is not a conflict.

---

# 9. Entity states over time

If an entity property changes, do not overwrite the earlier value as if it never existed.

Store a sequence of states with validity intervals.

Examples:
- a character's vehicle;
- residence;
- position/job;
- marital status;
- legal status;
- ownership of an object;
- life status.

The current value should be derivable from the state history for the selected point in time.

If a property never changes and does not require a temporal history, do not wrap it in unnecessary temporal structure.

---

# 10. Knowledge is not the same as world state

Always distinguish:
- what happened;
- who knows it;
- from what moment they know it;
- on what basis they know it;
- whether they consider it established;
- what is available to players.

Example:

> A character died in the past, while players still believe the character is missing.

Do not store this as two world states:
- "missing in Chapter 1";
- "dead in Chapter 2".

Correct model:
- objective world state: dead from a specific date;
- player knowledge state: fate unknown until a specific discovery.

Later knowledge creates a link back to the old event; it does not create a new version of the past.

---

# 11. Chapter, slice, and transition are different entities

## 11.1. Slice

A slice is a fixed, internally consistent projection of the database at the entry point of a period of active player work.

A slice answers:
- what has already happened by this point;
- which entity states are valid;
- which materials exist;
- which versions exist;
- which information is available to players.

A slice is not a copy of the whole database. It is a computed projection of one database.

## 11.2. Chapter

A chapter is a **period of active player work with one input slice**.

During a chapter, players:
- read documents;
- discuss;
- test versions;
- unlock available materials;
- draw conclusions;
- make a decision.

The real duration of a tabletop session does not need to match the world's calendar time.

Players may discuss one chapter for an hour, several evenings, or several real days.

Player progress within a chapter does not by itself advance the database's global calendar.

Every chapter must have a calendar start anchor in world time.

A deadline or world event may exist by which the players must lock their decision.

## 11.3. Transition

A transition is the interval between two chapters in which:
- the completed chapter's consequences are fixed;
- required world events happen;
- new documents appear;
- entity states change;
- official versions and legal statuses may change;
- the next internally consistent slice is formed.

A transition may take seconds for players and days or weeks in the world.

Physically, a transition may be implemented by one instruction:

> "Open envelope No. 2."

The envelope may immediately deliver the result of many events that happened during the between-chapter period.

## 11.4. A new slice is created after a transition

Base model:

```text
SLICE N
   ↓
CHAPTER N
   ↓
player decision
   ↓
TRANSITION N→N+1
   ↓
SLICE N+1
   ↓
CHAPTER N+1
```

Do not create a new global slice after every discovery inside a chapter.

Player progress within a chapter is stored separately from the chapter's input world slice.

---

# 12. Chapter start and the latest current document in the package

The start of every new chapter must be explicitly dated.

For a physical starting package/envelope, use this rule:

> The chapter input slice is dated by the latest current temporal point represented by the starting package, unless the author explicitly defines a different anchor.

An archival document inside the package does not move the chapter start into the past.

Distinguish:
- the date of the event described by a document;
- the document creation date;
- the date it is included in the game package;
- the chapter input-slice date.

Receiving a package may be instantaneous for players even if the package reflects several days or weeks of world events.

---

# 13. Game stage is not a color

Color is only a visual representation of a machine-readable semantic property.

Never store meaning as:
- `blue`;
- `red`;
- `purple`.

Store semantic state instead, for example:
- available from Chapter 1;
- appeared during Transition 1→2;
- first available in Chapter 2;
- known earlier but reinterpreted in Chapter 2;
- author-only layer;
- hidden layer.

The UI, Obsidian CSS, or application may render these properties with colors.

If a visual marker exists, there must be a digital reason from which that marker can be reproduced.

---

# 14. Materials do not own world truth

A document, photograph, newspaper, interrogation, or correspondence is a carrier of information.

A material may:
- record an event;
- state an assertion;
- contain an error;
- reflect someone else's version;
- be incomplete;
- gain a new meaning later.

Do not automatically treat the text of a material as objective world truth.

When adding a material, always separate:
- what objectively exists;
- what the material claims;
- who created it;
- which entities it concerns;
- when it was created;
- when it becomes available;
- which scene/event it relates to;
- whether its interpretation changes later.

Detailed material rules belong in the local `AGENTS.md` of the materials section.

---

# 15. A scene is a world-change node

A scene is a bounded episode in which participants change the state of the world or knowledge through their actions.

Important scene properties:
- time or time interval;
- place, if known;
- participants;
- state before;
- action;
- state after;
- outputs into other stories;
- related materials.

Do not create a scene for every micro-action.

A separate scene is useful when it:
- changes an important state;
- creates a significant fact or object;
- changes knowledge;
- has independent temporal significance;
- is used by multiple materials or stories;
- creates a causal output into another line.

A scene does not need to "belong" to a chapter. It exists on the world timeline. A chapter only determines when and to what extent information about that scene becomes usable by players.

---

# 16. Story stores causality

Chronology answers "what happened and when".

Story answers "why one thing led to another".

Do not replace a causal story with a list of dates.

One character may participate in multiple stories.

One scene may be an intersection point of multiple stories.

Stories should link to scenes, states, characters, and materials through IDs.

A character's local causality is more important than the character's global plot function.

A character acts because the action makes sense inside that character's own story, not because the author needs a clue.

---

# 17. Versions and interpretations

A false or incomplete version does not rewrite world facts.

It connects real or assumed facts using a different causal structure.

Therefore distinguish:
- objective fact;
- assertion;
- evidentiary status;
- official version;
- a character's version;
- players' working version;
- author truth.

If an old material gains a new meaning in a later chapter:
- do not create a duplicate material;
- do not rewrite its earlier content;
- add a new interpretation or relation.

---

# 18. Local AGENTS.md files must answer practical questions

Every type-specific local `AGENTS.md` must explain:

1. When should an entity of this type be created?
2. Which fields are required?
3. Which data belongs here?
4. Which data must not be stored here?
5. Where does a new fact go?
6. What should happen if a fact appears later?
7. When should an existing state be changed versus a new state appended?
8. Which entity types may be linked?
9. Which relation roles are allowed?
10. How is an existing entity found?
11. When must a linked entity be created?
12. What is generated automatically by the index and must not be maintained manually?
13. Which validations must run after a change?

A local instruction must make routine operations possible without reading the entire database.

---

# 19. Routing between entity types

If work on one card reveals an independently identifiable entity of another type:

1. do not fully describe it inside the current card;
2. find its ID through the index;
3. if the card exists, add a relation;
4. if it does not exist, follow the local `AGENTS.md` for that type and create it;
5. return to the original card and add the relation.

Example:

```text
new material
    ↓
vehicle mentioned
    ↓
search vehicle ID
    ↓
card missing
    ↓
follow Vehicle section rules
    ↓
create vehicle
    ↓
return to material
    ↓
ref vehicle ID
```

---

# 20. Do not invent missing data

If a required field is unknown, do not fill it with a guess.

Use the standard's explicit unknown/open status.

Distinguish:
- fact unknown inside the world;
- fact known to the author but hidden from players;
- author has not decided yet;
- data missing because migration is incomplete.

These states are not equivalent.

---

# 21. Conflicts and uncertainty

When a discrepancy is found, the agent must not automatically "fix" a lower-priority source based on its own guess.

The agent must:
1. identify the primary owner of the fact;
2. check the higher-priority source;
3. classify the discrepancy;
4. fix it only if the rule or canon is unambiguous;
5. never close an authorial uncertainty automatically.

The architecture must support distinguishing:
- cosmetic mismatch;
- unsynchronized change;
- structural conflict;
- open authorial question.

---

# 22. Canon source during test migration

Until the new database is fully populated, this repository is not the complete source of truth for "Дым над льдом".

During test migration:
- source canon must be read from `bestkvestnn-pixel/dimnadvodoi`;
- only verified data should be migrated into the new repository;
- absence of a fact from the new test database must not be treated as proof that it is absent from canon;
- do not change old canon merely to fit the new schema;
- disputed or stale facts must first be resolved against the source project's authority hierarchy.

A separate explicit decision must establish the moment when the new database becomes the primary source of truth.

---

# 23. Test time anchors for "Дым над льдом"

For testing the new model on the current game, use these working anchors:

## Chapter 1
- active player work starts: **2026-02-23 10:00**;
- players must lock their decision before the first trial begins;
- the real duration of the tabletop session is not modeled as world-calendar progression.

## Transition 1→2
- between-chapter change starts: **2026-03-09**, when the first trial begins;
- after Chapter 1 is completed, players receive an instruction to open the next physical package;
- that package represents the result of multiple world events that occurred during the transition.

## Chapter 2
- input slice: **2026-03-21**;
- the physical package includes, among other things, Sergey's confession and Newspaper No. 3;
- Newspaper No. 3 is the latest current document in the starting package and dates the entry into the new chapter;
- archival documents inside the package may describe substantially earlier events.

These dates are test data for this specific game, not universal rules of the standard.

---

# 24. Economical reading and incremental synchronization

By default, the database must be read and synchronized **incrementally**.

A full repository walk, full reread, or mass rewrite is not the normal operating mode.

Core principle:

> **Determine the delta first. Then read and modify only the delta and what is directly affected by it.**

## 24.1. Do not reread the entire database during a routine update

If a last synchronized revision, commit SHA, index version, or another reliable baseline marker is known, the agent must determine changes relative to it first.

Normal sequence:

1. determine the last known synchronized revision;
2. determine the current source revision;
3. obtain the list of modified, added, deleted, and renamed files;
4. read only those files;
5. additionally read only related cards required to validate links, conflicts, or consequences;
6. apply changes;
7. update only affected indexes and derived projections;
8. save the new synchronization baseline.

Do not walk all cards merely to discover that one file changed.

## 24.2. Read changed instructions before changed data

If the delta contains any of the following:
- root `AGENTS.md`;
- local `AGENTS.md`;
- type template;
- schema;
- role dictionary;
- index rules;
- validator;

read the changed instructions first, then process data inside their scope.

Do not update a card according to an old rule if the same delta changes the rule governing that card.

If a local `AGENTS.md` did not change and is already loaded in the current working context, it does not need to be reread for every file in the same operation.

## 24.3. Synchronization between databases starts with comparison

When moving changes between:
- source and new database;
- local and remote copy;
- branches;
- repositories;

do not manually compare every file.

Use the cheapest reliable delta mechanism first:
- commit SHA comparison;
- compare/diff between revisions;
- manifest;
- hash index;
- saved synchronization state.

Only when no reliable baseline exists may a one-time full inventory be performed. After that inventory, save a baseline marker so future synchronization is incremental.

## 24.4. Process only changed paths

For every changed path, classify the operation:

- **added** — new file;
- **modified** — existing file changed;
- **deleted** — file removed;
- **renamed/moved** — path changed;
- **instruction/schema changed** — processing rules changed.

Then apply the relevant local instruction only to that operation type.

Do not recreate existing cards merely because they are mentioned in a changed file.

Do not manually update neighboring cards when backlinks or the index are responsible for derived views.

## 24.5. Read replacement rules before replacing a file

Before modifying an existing file, the agent must:

1. determine which local `AGENTS.md` applies to the path;
2. read it if it is not already loaded or if it changed;
3. fetch the current version of the target file;
4. verify that the file has not independently changed since the baseline;
5. only then perform the replacement.

If both source and target changed the same file after their last common baseline, this is a synchronization conflict.

In that case:
- do not automatically overwrite either side;
- read both versions;
- identify the primary owners of changed facts;
- perform an intentional merge or record the conflict for the author.

## 24.6. Do not write when there is no real change

Before writing, compare the proposed content with the current content.

If nothing substantive changed:
- do not rewrite the file;
- do not change `updated/обновлено`;
- do not create an empty commit;
- do not touch derived data without need.

Formatting, whitespace ordering, or mass metadata "refresh" is not sufficient reason to rewrite the database.

## 24.7. Update only affected derived data

After a file change, update:
- that file's index record;
- its outgoing relations;
- necessary incoming relations for affected entities;
- affected slices/projections;
- local validator results.

Do not rebuild the entire database if the index and validator support safe incremental updates.

A full rebuild is allowed when:
- the index schema changes;
- the global relation model changes;
- the root standard changes in a way that requires migration;
- index state is damaged or lost;
- impact scope cannot be determined reliably;
- the user explicitly requests a full audit.

Even during a full validation, do not rewrite unchanged files.

## 24.8. A global rule change does not automatically mean mass migration

If the root or a local `AGENTS.md` changes, first determine:
- which entity types are affected;
- which fields or relations became invalid;
- whether existing cards actually require migration.

Do not rewrite every file merely because instruction text changed.

Mass migration is performed only when clearly necessary and must have an explicitly bounded scope.

## 24.9. Binary materials

For images, PDFs, audio, video, and other large files:
- do not download content again if its hash/version did not change;
- compare metadata, SHA, or another content identifier first;
- download the binary only when it is new, changed, or needed for a specific validation.

A linked Markdown material card may be updated independently from the binary itself.

## 24.10. Minimal read context after a change

After receiving a changed file, read additional data only when necessary.

Usually enough:
- the changed file itself;
- the applicable type instruction;
- entity cards whose links were added or removed;
- the primary owner of a changed fact;
- related scenes/materials if the change affects causality, time, or availability.

Do not open every character file, every chapter document, or the full chronology because of one local change when links and the index provide enough context.

## 24.11. Synchronization state must be reproducible

The synchronization system must be able to determine:
- which revision the previous synchronization started from;
- up to which revision data has already been processed;
- which files were processed;
- whether conflicts occurred;
- whether the update completed successfully.

The concrete manifest/sync-state format will be defined by the technical implementation later, but the principle is mandatory.

After successful synchronization, the new revision becomes the next comparison baseline.

## 24.12. Short synchronization algorithm

```text
KNOWN BASE REVISION
        ↓
COMPARE WITH CURRENT REVISION
        ↓
LIST CHANGED PATHS ONLY
        ↓
READ CHANGED INSTRUCTIONS FIRST
        ↓
READ CHANGED DATA FILES
        ↓
READ ONLY NECESSARY RELATED ENTITIES
        ↓
CHECK FOR CONFLICTS
        ↓
WRITE ONLY REAL CHANGES
        ↓
UPDATE AFFECTED INDEX ENTRIES
        ↓
VALIDATE AFFECTED AREA
        ↓
SAVE NEW BASE REVISION
```

The purpose of this protocol is to minimize:
- network requests;
- transferred data volume;
- repeated context loading;
- unnecessary writes;
- accidental mass changes;
- synchronization cost and time.

---

# 25. After every operation

After creating or modifying an entity, the agent must:

1. validate required fields for the local type;
2. validate ID uniqueness;
3. verify all referenced IDs exist;
4. validate temporal consistency;
5. verify no duplicate primary fact was created;
6. verify world truth and knowledge were not confused;
7. validate game availability;
8. verify an old material was not duplicated instead of receiving a new interpretation;
9. update the index and run the validator when those systems exist;
10. report only real changes and real problems, without inventing missing canon.

---

# 26. Short architecture formula

> **One world.**

> **One calendar timeline.**

> **Scenes and events change the world.**

> **States record what is true during a given period.**

> **Knowledge changes separately from the world.**

> **Materials carry knowledge but are not world truth itself.**

> **A slice is an internally consistent projection of the database.**

> **A chapter is the players' working period with one input slice.**

> **A transition applies consequences and forms the next slice.**

> **Color is a rendering of a digital property, not data.**

> **A local AGENTS.md explains how to add an element without reading the whole database.**
