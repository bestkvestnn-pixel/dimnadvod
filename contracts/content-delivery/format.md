# Content lock format proposal

`content-lock.schema.yaml` defines the future JSON lock in
`test-app/.content/content-lock.json`. No consumed lock is created by this
foundation. The existing contract remains normative; its three paired
instructions were checked without requiring edits.

`source_revision` is a full immutable commit SHA, never `main`, a timestamp,
or the pre-foundation baseline. That revision must include source, schemas and
the projection tool so the package can be reproduced. `projection` identifies
the audience, slice and observer. Canonical entity IDs cross unchanged.

`package_hash` is `sha256:` followed by the SHA-256 of a UTF-8, LF-terminated
manifest. Each line is `<sha256-of-file-bytes>  <relative-posix-path>\n`, sorted
by path, covering every delivered projection and asset. Forbid duplicate paths,
absolute paths, `..`, backslashes and line breaks in paths. Exclude the lock
itself and the manifest from this list to avoid recursive hashes. Metadata-only
changes alter their file hash, not unchanged binary hashes. Tool outputs must be
deterministic and omit wall-clock generation timestamps.

Delivery will validate schemas/refs/assets, spoiler boundaries and old-save
compatibility, stage an immutable package, run targeted consumer tests, and
atomically select that package by updating the lock last. Failure leaves the
previous lock/package pairing active. No consumer, packager, runtime migration,
or atomic publication implementation is introduced in this foundation.

Unproved existence/temporal eligibility, unresolved applicable chronology,
unapproved branch rules and missing assets block an affected package. An unknown
exact creation date is acceptable when source-backed bounds or package facts
establish eligibility; never fabricate precision. In all cases,
passing the TEST probe does not clear them. A rename with unchanged ID updates
paths/index references; removal requires inbound dependency review and runtime
compatibility policy, never automatic reuse of the deleted ID.
