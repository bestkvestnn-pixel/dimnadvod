"""Bounded TEST model probe; this is not a production content-delivery compiler."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]


class ValidationError(ValueError):
    pass


class SourceLoader(yaml.SafeLoader):
    """Keep calendar text exact and reject silently overwritten YAML keys."""


def _mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ValidationError(f"YAML key must be unique text: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


SourceLoader.add_constructor("tag:yaml.org,2002:map", _mapping)
SourceLoader.add_constructor("tag:yaml.org,2002:timestamp", lambda loader, node: node.value)


def load_yaml(path):
    return yaml.load(Path(path).read_text(encoding="utf-8"), Loader=SourceLoader)


def schema():
    return load_yaml(ROOT / "schemas/foundation.yaml")


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def fields(value, allowed, required=(), context="record"):
    require(isinstance(value, dict), f"{context}: expected mapping")
    require(set(value) <= set(allowed), f"{context}: unsupported fields {set(value) - set(allowed)}")
    require(set(required) <= set(value), f"{context}: missing fields {set(required) - set(value)}")


def text(value, context):
    require(isinstance(value, str) and bool(value.strip()), f"{context}: expected nonempty text")


def sequence(value, context):
    require(isinstance(value, list), f"{context}: expected list")
    return value


def unknown(value):
    return isinstance(value, dict) and set(value) == {"status"} and value["status"] in schema()["unknown_statuses"]


def time_bounds(value):
    """A day is an uncertainty interval; minute timestamps are comparable anchors."""
    if unknown(value):
        return None
    require(isinstance(value, str), "Time must be calendar text or an explicit unknown marker")
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            start = datetime.strptime(value, "%Y-%m-%d")
            return start, start + timedelta(days=1) - timedelta(microseconds=1)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", value):
            point = datetime.strptime(value, "%Y-%m-%dT%H:%M")
            return point, point
    except (ValueError, OverflowError) as exc:
        raise ValidationError(f"Invalid calendar date: {value}") from exc
    raise ValidationError(f"Unsupported time precision/format: {value!r}")


def timing(event_time, query_time):
    event, query = time_bounds(event_time), time_bounds(query_time)
    if event is None or query is None:
        return "unresolved"
    if event[1] < query[0] or event[0] == event[1] == query[0]:
        return "applies"
    if event[0] > query[1]:
        return "future"
    return "unresolved"


def references(value):
    if isinstance(value, dict):
        # An event's changing reference is encoded as key/value, not as a
        # direct field. Include it in dependency/index edges as well.
        if isinstance(value.get("key"), str) and value["key"].endswith("_ref") and isinstance(value.get("value"), str):
            yield value["value"]
        for key, item in value.items():
            if key.endswith("_ref"):
                yield item
            elif key.endswith("_refs"):
                yield from item if isinstance(item, list) else [item]
            else:
                yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)


def assertion_value(assertion, entities):
    fields(assertion, {"owner_ref", "key"}, {"owner_ref", "key"}, "assertion")
    owner, key = assertion["owner_ref"], assertion["key"]
    require(isinstance(owner, str) and owner in entities, f"Assertion owner does not exist: {owner!r}")
    text(key, "assertion key")
    # Restrict addresses to actual fact/claim payloads, never metadata or author notes.
    require(bool(re.fullmatch(r"(?:facts|claims)\.[a-z][a-z0-9_]*|changes\.\d+\.value", key)),
            f"Not an assertion payload address: {key}")
    value = entities[owner]
    try:
        for part in key.split("."):
            value = value[int(part)] if isinstance(value, list) and part.isdigit() else value[part]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValidationError(f"Unresolvable assertion: {owner}/{key}") from exc
    return value


COMMON = {"id", "type", "name", "aliases", "facts", "relations", "provenance"}
LOCAL = {
    "character": set(), "vehicle": set(), "group": set(),
    "material": {"claims", "created_at", "availability", "asset", "disclosures"},
    "event": {"at", "changes", "knowledge_changes"},
    "chapter": {"ordinal", "input_slice_ref"},
    "slice": {"at", "observer_ref", "chapter_ref"},
}


def validate(document, asset_root=ROOT):
    spec = schema()
    fields(document, {"scope", "schema_version", "entities"}, {"scope", "schema_version", "entities"}, "fixture")
    require(document["scope"] == "TEST", "Probe accepts TEST fixtures only")
    require(type(document["schema_version"]) is int and document["schema_version"] == spec["schema_version"], "Unsupported schema version")
    entities = {}
    for entity in sequence(document["entities"], "entities"):
        require(isinstance(entity, dict), "Entity must be a mapping")
        kind = entity.get("type")
        require(isinstance(kind, str) and kind in spec["types"], f"Unsupported entity type: {kind!r}")
        fields(entity, COMMON | LOCAL[kind], spec["required_entity_fields"], kind)
        entity_id = entity["id"]
        require(isinstance(entity_id, str) and bool(re.fullmatch(spec["id_pattern"], entity_id)), f"Invalid ID: {entity_id!r}")
        rule = spec["types"][kind]
        prefixes = [rule["prefix"], *rule.get("legacy_prefixes", [])]
        require(any(entity_id.startswith(prefix + "-") for prefix in prefixes), f"ID/type prefix mismatch: {entity_id}")
        require(entity_id not in entities, f"Duplicate ID: {entity_id}")
        text(entity["name"], entity_id + " name")
        entities[entity_id] = entity

    def ref(value, kinds=None):
        require(isinstance(value, str) and value in entities, f"Unresolved reference: {value!r}")
        require(kinds is None or entities[value]["type"] in kinds, f"Wrong reference type: {value}")

    def check_unknowns(value):
        if isinstance(value, dict):
            for key, child in value.items():
                require(isinstance(key, str), "Keys must be strings")
                require(not re.search(r"(?:^|_)ch\d+(?:_|$)", key, re.I), f"Chapter state copy is forbidden: {key}")
                if key == "status" and child in spec["unknown_statuses"]:
                    require(set(value) == {"status"}, "Unknown marker must not contain a guessed value")
                check_unknowns(child)
        elif isinstance(value, list):
            for child in value:
                check_unknowns(child)

    def knowledge(change, event=None):
        allowed = {"observer_ref", "assertion", "status"} | ({"basis_refs"} if event else set())
        fields(change, allowed, {"observer_ref", "assertion", "status"}, "knowledge")
        ref(change["observer_ref"], {"character", "group"})
        require(change["status"] in spec["knowledge_statuses"], "Unsupported knowledge status")
        assertion_value(change["assertion"], entities)
        bases = sequence(change.get("basis_refs", []), "basis_refs")
        for basis in bases:
            ref(basis, {"material", "event"})
        if event:
            require(bases, f"Knowledge event {event['id']} needs a basis")

    histories = defaultdict(list)
    knowledge_histories = defaultdict(list)
    ordinals = set()
    symmetric_relations = set()
    for entity_id, entity in entities.items():
        kind = entity["type"]
        check_unknowns(entity)
        for reference in references(entity):
            ref(reference)
        for alias in sequence(entity.get("aliases", []), "aliases"):
            text(alias, "alias")
        facts = entity.get("facts", {})
        fields(facts, spec["fact_keys"][kind], context=f"{entity_id} facts")
        for key, value in facts.items():
            require(isinstance(value, (str, int, float, bool)) or unknown(value), f"Invalid fact value: {key}")
            if key == "birth_date":
                require(unknown(value) or isinstance(value, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)), "Birth date requires day precision")
                time_bounds(value)
        if "provenance" in entity:
            entries = sequence(entity["provenance"], "provenance")
            require(entries, "Provenance cannot be empty when supplied")
            for entry in entries:
                fields(entry, {"source_key", "fields"}, {"source_key"}, "provenance entry")
                text(entry["source_key"], "provenance source_key")
                if "fields" in entry:
                    for field in sequence(entry["fields"], "provenance fields"):
                        text(field, "provenance field")
        relation_keys = set()
        for relation in sequence(entity.get("relations", []), "relations"):
            fields(relation, {"type", "target_ref", "role"}, {"type", "target_ref"}, "relation")
            text(relation["type"], "relation type")
            rule = spec["relations"].get(relation["type"])
            require(rule is not None and kind in rule["source"], "Unsupported relation/source type")
            ref(relation["target_ref"], set(rule["target"]))
            require("role" not in relation or relation["role"] in rule["roles"], "Unsupported relation role")
            signature = (relation["type"], relation["target_ref"], relation.get("role"))
            require(signature not in relation_keys, "Duplicate relation")
            relation_keys.add(signature)
            if relation["type"] == "spouse_of":
                pair = tuple(sorted((entity_id, relation["target_ref"])))
                require(entity_id != relation["target_ref"] and pair not in symmetric_relations, "Symmetric relation must have one primary owner")
                symmetric_relations.add(pair)
        if kind == "event":
            require("at" in entity, f"Event {entity_id} needs at")
            time_bounds(entity["at"])
            require(entity.get("changes") or entity.get("knowledge_changes"), "Event needs a nonempty world or knowledge change")
            local_keys = set()
            for change in sequence(entity.get("changes", []), "changes"):
                fields(change, {"target_ref", "key", "value"}, {"target_ref", "key", "value"}, "world change")
                ref(change["target_ref"])
                target = entities[change["target_ref"]]
                require(change["key"] in spec["state_keys"][target["type"]], "Unsupported changing property")
                require(change["key"] not in target.get("facts", {}), "Static fact duplicates event state")
                signature = (change["target_ref"], change["key"])
                require(signature not in local_keys, "Duplicate same-event property change")
                local_keys.add(signature)
                value = change["value"]
                if change["key"] == "owner_ref" and not unknown(value):
                    ref(value, {"character", "group"})
                elif not unknown(value):
                    require(value in spec["state_values"].get(change["key"], []), "Unsupported state value")
                histories[signature].append((entity["at"], entity_id, change))
            seen_knowledge = set()
            for change in sequence(entity.get("knowledge_changes", []), "knowledge_changes"):
                knowledge(change, entity)
                signature = (change["observer_ref"], change["assertion"]["owner_ref"], change["assertion"]["key"])
                require(signature not in seen_knowledge, "Duplicate same-event knowledge change")
                seen_knowledge.add(signature)
                knowledge_histories[signature].append((entity["at"], entity_id, change))
        elif kind == "material":
            require("created_at" in entity and "kind" in facts, f"Material {entity_id} needs created_at and facts.kind")
            time_bounds(entity["created_at"])
            claims = entity.get("claims", {})
            require(isinstance(claims, dict), "claims must be a mapping")
            for key, value in claims.items():
                require(bool(re.fullmatch(r"[a-z][a-z0-9_]*", key)), "Invalid claim key")
                text(value, "claim payload")
            if "availability" in entity:
                availability = entity["availability"]
                fields(availability, {"from_chapter_ref", "audience_ref"}, {"from_chapter_ref", "audience_ref"}, "availability")
                ref(availability["from_chapter_ref"], {"chapter"})
                ref(availability["audience_ref"], {"character", "group"})
            asset = entity.get("asset")
            if "asset" in entity and asset != {"status": "not_created"}:
                fields(asset, {"path", "sha256"}, {"path", "sha256"}, "asset")
                text(asset["path"], "asset path")
                require(isinstance(asset["sha256"], str) and bool(re.fullmatch(r"[0-9a-f]{64}", asset["sha256"])), "Invalid asset SHA256")
                root = Path(asset_root).resolve()
                path = (root / asset["path"]).resolve()
                require(not Path(asset["path"]).is_absolute() and path.is_relative_to(root), "Asset escapes source root")
                require(path.is_file(), f"Missing asset: {asset['path']}")
                require(hashlib.sha256(path.read_bytes()).hexdigest() == asset["sha256"], "Asset hash mismatch")
            seen_disclosures = set()
            for change in sequence(entity.get("disclosures", []), "disclosures"):
                knowledge(change)
                require(change["assertion"]["owner_ref"] == entity_id and change["assertion"]["key"].startswith("claims."), "Material disclosure must address its own claim")
                signature = (change["observer_ref"], change["assertion"]["key"])
                require(signature not in seen_disclosures, "Duplicate material disclosure")
                seen_disclosures.add(signature)
        elif kind == "chapter":
            require({"ordinal", "input_slice_ref"} <= set(entity), "Chapter needs ordinal and input slice")
            require(type(entity["ordinal"]) is int and entity["ordinal"] > 0 and entity["ordinal"] not in ordinals, "Chapter ordinal must be unique positive integer")
            ordinals.add(entity["ordinal"])
            ref(entity["input_slice_ref"], {"slice"})
            require(entities[entity["input_slice_ref"]].get("chapter_ref") == entity_id, "Chapter/slice backlink mismatch")
        elif kind == "slice":
            require({"at", "observer_ref", "chapter_ref"} <= set(entity), "Slice needs time, observer, chapter")
            require(not unknown(entity["at"]), "Slice requires a calendar anchor")
            time_bounds(entity["at"])
            ref(entity["observer_ref"], {"character", "group"})
            ref(entity["chapter_ref"], {"chapter"})
            require(entities[entity["chapter_ref"]].get("input_slice_ref") == entity_id, "Slice/chapter backlink mismatch")

    chapters = sorted((entity for entity in entities.values() if entity["type"] == "chapter"), key=lambda item: item["ordinal"])
    for previous, following in zip(chapters, chapters[1:]):
        before = time_bounds(entities[previous["input_slice_ref"]]["at"])
        after = time_bounds(entities[following["input_slice_ref"]]["at"])
        require(after[1] >= before[0], f"Chapter calendar order reversed: {previous['id']}, {following['id']}")

    for collection in (histories, knowledge_histories):
        for key, entries in collection.items():
            for index, first in enumerate(entries):
                for second in entries[index + 1:]:
                    left, right = time_bounds(first[0]), time_bounds(second[0])
                    require(left is not None and right is not None and (left[1] < right[0] or right[1] < left[0]),
                            f"Unordered competing changes for {key}: {first[1]}, {second[1]}")
    return entities


def _order(entity):
    bounds = time_bounds(entity["at"])
    return (bounds[0] if bounds else datetime.max, entity["id"])


def project(document, slice_id, opened_refs=(), asset_root=ROOT):
    entities = validate(document, asset_root)
    require(slice_id in entities and entities[slice_id]["type"] == "slice", "Projection requires a slice ID")
    coordinate = entities[slice_id]
    observer = coordinate["observer_ref"]
    ordinal = entities[coordinate["chapter_ref"]]["ordinal"]
    opened = set(opened_refs)
    require(all(item in entities and entities[item]["type"] == "material" for item in opened), "Runtime opened_refs must reference materials")
    states, knowledge, unresolved = defaultdict(dict), {}, []
    intervals, blocked_knowledge = defaultdict(lambda: defaultdict(list)), set()
    events = sorted((item for item in entities.values() if item["type"] == "event"), key=_order)
    for event in events:
        applies = timing(event["at"], coordinate["at"])
        for change in event.get("changes", []):
            target, key = change["target_ref"], change["key"]
            history = intervals[target][key]
            boundary = {"event_ref": event["id"], "at": event["at"]}
            if history:
                history[-1]["until"] = boundary
            history.append({"from": boundary, "until": None, "value": change["value"]})
            states[target].setdefault(key, {"status": "migration_missing", "reason": "before_first_change"})
            if applies == "applies":
                states[target][key] = change["value"]
            elif applies == "unresolved":
                states[target][key] = {"status": "unresolved", "reason": "time_precision"}
                unresolved.append({"event_ref": event["id"], "target_ref": target, "key": key})
        for change in event.get("knowledge_changes", []):
            if change["observer_ref"] != observer:
                continue
            address = (change["assertion"]["owner_ref"], change["assertion"]["key"])
            if applies == "applies":
                knowledge[address] = change
            elif applies == "unresolved":
                knowledge.pop(address, None)
                blocked_knowledge.add(address)
                unresolved.append({"event_ref": event["id"], "assertion": change["assertion"]})
    available = []
    for entity in sorted(entities.values(), key=lambda item: item["id"]):
        if entity["type"] != "material":
            continue
        rule = entity.get("availability")
        if rule is None:
            continue
        if rule["audience_ref"] != observer or entities[rule["from_chapter_ref"]]["ordinal"] > ordinal:
            continue
        # Authored package availability is explicit. An unknown creation timestamp
        # is not fabricated; a known future creation cannot enter this slice.
        existence = timing(entity["created_at"], coordinate["at"])
        if existence == "future":
            continue
        if existence == "unresolved" and not unknown(entity["created_at"]):
            unresolved.append({"material_ref": entity["id"], "reason": "creation_time_precision"})
            continue
        available.append({"id": entity["id"], "name": entity["name"]})
        if entity["id"] in opened:
            for change in entity.get("disclosures", []):
                if change["observer_ref"] == observer:
                    address = (change["assertion"]["owner_ref"], change["assertion"]["key"])
                    # Reading a carrier does not downgrade an established/rejected
                    # assessment already supplied by canonical knowledge history.
                    if address not in blocked_knowledge:
                        knowledge.setdefault(address, change)
    visible_ids = {item["id"] for item in available}
    player_knowledge = []
    for address, change in sorted(knowledge.items()):
        value = assertion_value(change["assertion"], entities)
        # Do not let a payload carry unapproved entity identities or nested refs.
        if not isinstance(value, (str, int, float, bool)):
            continue
        if isinstance(value, str) and value in entities and value not in visible_ids:
            continue
        player_knowledge.append({"value": value, "status": change["status"]})
    return {
        "author": {"states": dict(states), "intervals": {target: dict(keys) for target, keys in intervals.items()}, "unresolved": unresolved},
        "player": {"materials": available, "knowledge": player_knowledge},
    }


def build_probe(document, source_path="tests/fixtures/migration-probe.yaml", source_hash=None, opened_refs=(), asset_root=ROOT):
    entities = validate(document, asset_root)
    incoming = defaultdict(set)
    outgoing = {key: sorted(set(references(entity))) for key, entity in entities.items()}
    for key, refs in outgoing.items():
        for target in refs:
            incoming[target].add(key)
    index = {}
    for key, entity in sorted(entities.items()):
        content = json.dumps(entity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        index[key] = {"path": source_path, "entity_id": key, "type": entity["type"], "name": entity["name"], "aliases": entity.get("aliases", []),
                      "hash_algorithm": "sha256",
                      "hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                      "outgoing": outgoing[key], "incoming": sorted(incoming[key])}
    return {"ownership": "DERIVED", "scope": "TEST", "audience": "author", "schema_version": document["schema_version"],
            "source": {"path": source_path, "sha256": source_hash}, "index": index,
            "projections": {key: project(document, key, opened_refs, asset_root) for key, entity in sorted(entities.items()) if entity["type"] == "slice"}}


def write_if_changed(path, value):
    path = Path(path)
    output = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    if path.exists() and path.read_bytes() == output:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(output)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "probe"])
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--opened-ref", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        document = load_yaml(args.fixture)
        entities = validate(document)
        if args.command == "validate":
            print(f"Valid TEST fixture: {len(entities)} entities")
            return 0
        require(args.output is not None, "probe requires --output under generated/")
        output = args.output.resolve()
        require(output.is_relative_to(ROOT / "generated") and output.suffix == ".json", "Probe output must be generated/*.json")
        path = args.fixture.resolve()
        display_path = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.name
        result = build_probe(document, display_path, hashlib.sha256(path.read_bytes()).hexdigest(), args.opened_ref)
        changed = write_if_changed(output, result)
        print(f"{'Wrote' if changed else 'Unchanged'} DERIVED TEST probe: {args.output}")
        return 0
    except (ValidationError, yaml.YAMLError, OSError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
