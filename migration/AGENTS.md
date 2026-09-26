# Migration bookkeeping

This directory contains evidence and progress bookkeeping, not a second set of
canonical entity cards. Apply root §22 and §24 and the user's source hierarchy.

Pin repository revisions and the exact paths/blob IDs actually inspected. A
pinned HEAD does not mean its contents were read, validated, or migrated. Keep
`inventory_only`, `read_for_probe`, `blocked`, and `migrated` statuses distinct.
Do not mark a whole source revision migrated after a bounded demonstration.

Record conflicts with primary owners and evidence. An unresolved authorial
decision must remain open. Technical omissions not yet investigated are not
automatically questions that require the author.

For a later batch, compare the pinned revision with the new revision, read
changed applicable instructions first, then changed relevant paths and required
dependencies. A partially reviewed file remains partial even if its Git blob is
pinned. Save new per-path outcomes after successful checks; advance a completed
batch baseline only when the entire declared batch succeeds. Never update a
consumer content lock here to imply unperformed delivery.
