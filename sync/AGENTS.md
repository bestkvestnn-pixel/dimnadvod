# AGENTS.md — Cross-Repository Synchronization

## Authority

This is the normative synchronization contract between:

- `bestkvestnn-pixel/dimnadvod` — AUTHOR / CANON / KNOWLEDGE SOURCE.
- `bestkvestnn-pixel/test-app` — PLAYER / RUNTIME APPLICATION.

Content dependency is one-way:

> **dimnadvod → test-app**

The app may contain generated copies of authored data, but it MUST NOT become an independent source of canon.

## Ownership classes

Every synchronized file belongs to exactly one class:

- **SOURCE** — author-maintained canonical data in `dimnadvod`.
- **GENERATED** — machine-generated application data derived from SOURCE.
- **RUNTIME** — player/session state owned by `test-app`.

Never mix ownership between these classes.

## Incremental synchronization

Synchronization MUST be incremental by default.

Normal flow:

```text
LAST SUCCESSFUL BASELINE
        ↓
COMPARE SOURCE REVISION
        ↓
LIST CHANGED PATHS ONLY
        ↓
READ CHANGED INSTRUCTIONS FIRST
        ↓
READ CHANGED SOURCE FILES
        ↓
RESOLVE ONLY REQUIRED DEPENDENCIES
        ↓
GENERATE ONLY AFFECTED OUTPUTS
        ↓
VALIDATE
        ↓
PUBLISH
        ↓
UPDATE SYNC MANIFEST LAST
```

Do not reread both repositories in full unless no reliable baseline exists, the dependency index is invalid, or the user explicitly requests a full audit/rebuild.

## Instruction changes

If the delta contains root/local `AGENTS.md`, templates, schemas, dictionaries, export rules, or validators, read those changes before processing data under their scope.

A changed instruction does not automatically require mass migration. Determine the actual affected scope first.

## Change classes

Classify changed source paths as:

- added
- modified
- deleted
- renamed/moved
- instruction/schema changed
- binary asset changed

Use repository compare/diff, saved revisions, manifests, or hashes instead of manually rereading every file.

## Dependency resolution

After identifying changed SOURCE paths, load only dependencies required to rebuild valid affected outputs.

Dependency expansion must be driven by stable IDs, indexes, manifests, or explicit export dependency rules.

Do not load unrelated characters, chapters, materials, or assets.

## Generated boundary

Generated authored data in `test-app` must live in a clearly designated generated area.

Generated files:
- are replaceable by regeneration;
- MUST NOT be manually edited as canon;
- should record source revision/schema metadata when practical.

Manual changes inside generated data are drift, not reverse canon edits.

## Application-owned data

`test-app` owns application code and runtime/session state.

Do not reverse-sync into canon:
- UI implementation;
- CSS/components;
- local-storage mechanics;
- test fixtures;
- debug data;
- player progress;
- seen/unlocked state;
- player-entered answers;
- application preferences.

If the app requires a new canonical field, treat that as a schema-change proposal. Canon changes only after explicit author approval.

## Runtime protection

Content synchronization MUST NOT reset or overwrite normal player/session state.

If new generated content requires a runtime migration:
1. define an explicit migration;
2. preserve user state whenever possible;
3. migrate only affected fields.

## IDs, renames, deletions

Stable entity IDs are the identity anchor.

- A source file rename with the same ID is not a new entity.
- A source deletion must remove/update only affected generated references.
- Synchronization must leave no dangling generated IDs.

## Binary assets

For images, PDF, audio, video, and other large files:
- compare SHA/hash/version first;
- transfer only new or changed binaries;
- do not recopy unchanged files;
- a metadata-only change must not force binary retransmission.

## Conflict classes

### Source conflict
The same canonical SOURCE changed independently on competing source branches/copies.

Do not overwrite automatically. Resolve using source authority rules.

### Generated drift
A GENERATED file was manually modified in `test-app`.

Do not import it into canon. Regenerate it or move the intended authored change to SOURCE after explicit approval.

### Runtime incompatibility
New generated content conflicts with existing session state.

Resolve through explicit runtime migration.

### Schema mismatch
Exporter and app expect incompatible schema versions.

Stop publication until compatibility is resolved. Do not guess semantics.

## Atomic publication

Preferred order:

1. generate affected outputs;
2. validate them;
3. validate cross-file references;
4. copy changed assets;
5. publish changed generated files;
6. update the synchronization manifest **last**.

If validation fails, do not advance the synchronization baseline.

## Synchronization manifest

The generated side must maintain one machine-readable current sync state containing at least:

```yaml
source_repository: bestkvestnn-pixel/dimnadvod
source_revision: <commit SHA>
export_schema_version: <version>
sync_status: success
```

It may also include target revision, exporter version, artifact hashes, changed paths, migration version, timestamp, and error/conflict state.

The manifest is synchronization metadata, not canon.

## Minimal-write rule

If an affected output regenerates to identical content:
- do not rewrite it;
- do not create a noisy commit;
- do not mark it changed merely because the generator ran.

## Full rebuild

A full rebuild is allowed only when justified by:
- initial bootstrap;
- global export-schema change;
- missing/corrupt dependency index;
- unknown baseline;
- globally changed exporter semantics;
- unbounded impact;
- explicit user request.

Even then, avoid rewriting byte-identical outputs where practical.

## Test data

Temporary fixtures and prototype data in `test-app` must be isolated from synchronized generated content and clearly marked test-only.

Test data must never masquerade as generated canon.

## Completion criteria

Synchronization is complete only when:
1. source delta was identified;
2. changed instructions were processed first;
3. affected source files were read;
4. required dependencies were resolved;
5. only affected outputs were regenerated;
6. generated references validate;
7. required assets exist;
8. runtime state was preserved;
9. manifest records the exact processed source revision;
10. baseline advances only after successful validation.

> **One authored source. Multiple generated views. Runtime state stays runtime.**
