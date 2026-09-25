# AGENTS.md — Compatibility Pointer for Cross-Repository Content Delivery

This path is retained for compatibility with earlier instructions and links.

The normative cross-repository contract has moved to:

[../contracts/content-delivery/AGENTS.md](../contracts/content-delivery/AGENTS.md)

Repository roots:

- [dimnadvod/AGENTS.md](../AGENTS.md)
- [test-app/AGENTS.md](https://github.com/bestkvestnn-pixel/test-app/blob/main/AGENTS.md)

## Rule

Do not maintain synchronization rules in this file.

Before any cross-repository content delivery, generated-content update, content-lock update, or Author Studio canonical write:

1. read the applicable repository root `AGENTS.md`;
2. read `contracts/content-delivery/AGENTS.md`;
3. read the counterpart repository root `AGENTS.md` when the operation crosses the repository boundary;
4. read only the changed local instructions/data required by the operation.

The architecture contains **one canonical authored database** in `dimnadvod`; `test-app` is an interface repository, not a second story database.
