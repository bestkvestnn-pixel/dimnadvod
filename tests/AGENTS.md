# Foundation tests

Fixtures are TEST, not migrated SOURCE. The migration probe uses the format in
`../source/AGENTS.md` and vocabulary in `../schemas/foundation.yaml`, with
`scope: TEST`, `schema_version`, and `entities` as its outer wrapper.

Keep evidence-backed examples separate from synthetic negative test cases.
Reference evidence keys from `../migration/baseline.yaml`; mark provisional IDs
and modeled runtime actions in fixture comments/report. Never infer authority
switch, completed asset import, or successful application delivery from tests.
Generated fixture indexes/projections remain under `generated/` with TEST scope.

Test behavior that can fail: precision boundaries, knowledge vs world truth,
availability vs opened state, hidden payload exclusion, invalid references,
duplicate owners, and deterministic no-op output. Do not create an app or a
parallel authored story model here.
