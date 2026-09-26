"""Behavioral checks for the isolated foundation probe."""

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("foundation", ROOT / "tools/foundation.py")
foundation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(foundation)


def fixture():
    return {"scope": "TEST", "schema_version": 1, "entities": [
        {"id": "char-anna", "type": "character", "name": "Anna"},
        {"id": "group-players", "type": "group", "name": "Players"},
        {"id": "event-death", "type": "event", "name": "SECRET WORLD EVENT", "at": "2025-09-03",
         "changes": [{"target_ref": "char-anna", "key": "life_status", "value": "dead"}]},
        {"id": "doc-confession", "type": "material", "name": "Confession", "created_at": "2026-03-20",
         "facts": {"kind": "confession"},
         "claims": {"account": "Claim from confession"}, "asset": {"status": "not_created"},
         "availability": {"from_chapter_ref": "chapter-two", "audience_ref": "group-players"},
         "disclosures": [{"observer_ref": "group-players", "assertion": {"owner_ref": "doc-confession", "key": "claims.account"}, "status": "reported"}]},
        {"id": "chapter-one", "type": "chapter", "name": "One", "ordinal": 1, "input_slice_ref": "slice-one"},
        {"id": "chapter-two", "type": "chapter", "name": "Two", "ordinal": 2, "input_slice_ref": "slice-two"},
        {"id": "slice-one", "type": "slice", "name": "One", "at": "2026-02-23T10:00", "observer_ref": "group-players", "chapter_ref": "chapter-one"},
        {"id": "slice-two", "type": "slice", "name": "Two", "at": "2026-03-21", "observer_ref": "group-players", "chapter_ref": "chapter-two"},
    ]}


class FoundationTests(unittest.TestCase):
    def test_real_probe_preserves_history_and_excludes_hidden_photo_identity(self):
        document = foundation.load_yaml(ROOT / "tests/fixtures/migration-probe.yaml")
        self.assertEqual(len(foundation.validate(document)), 12)
        first = foundation.project(document, "slice-chapter-1", ["doc-sergey-confession"])
        second = foundation.project(document, "slice-chapter-2", ["doc-sergey-confession"])
        unread = foundation.project(document, "slice-chapter-2")
        self.assertEqual(first["author"]["states"]["char-anna-akunina"]["life_status"], "dead")
        self.assertEqual(first["author"]["states"], second["author"]["states"])
        self.assertEqual(first["player"]["knowledge"], [])
        self.assertEqual(unread["player"]["knowledge"], [])
        self.assertEqual(len(second["player"]["knowledge"]), 1)
        self.assertEqual(second["player"]["knowledge"][0]["status"], "reported")
        for result in (first, second, unread):
            player = json.dumps(result["player"], ensure_ascii=False)
            self.assertNotIn("char-veronika-pronina", player)
            self.assertNotIn("relations", player)
            self.assertNotIn("provenance", player)
            self.assertIn("Фото Сергея с неизвестной", player)
        probe = foundation.build_probe(document)
        self.assertEqual(probe["audience"], "author")
        self.assertIn("doc-sergey-with-unknown-photo", probe["index"]["char-veronika-pronina"]["incoming"])

    def test_same_world_state_different_material_availability(self):
        document = fixture()
        first = foundation.project(document, "slice-one")
        second = foundation.project(document, "slice-two")
        self.assertEqual(first["author"]["states"], second["author"]["states"])
        self.assertEqual(first["author"]["states"]["char-anna"]["life_status"], "dead")
        self.assertEqual(first["player"], {"materials": [], "knowledge": []})
        self.assertEqual(second["player"]["materials"], [{"id": "doc-confession", "name": "Confession"}])
        self.assertEqual(second["player"]["knowledge"], [])

    def test_runtime_opening_requires_availability_and_does_not_change_world(self):
        document = fixture()
        early = foundation.project(document, "slice-one", ["doc-confession"])
        later = foundation.project(document, "slice-two", ["doc-confession"])
        self.assertEqual(early["player"]["knowledge"], [])
        self.assertEqual(later["player"]["knowledge"], [{"value": "Claim from confession", "status": "reported"}])
        self.assertEqual(early["author"]["states"], later["author"]["states"])

    def test_day_precision_does_not_mean_midnight_or_end_of_day(self):
        document = fixture()
        document["entities"][2]["at"] = "2026-03-21T15:00"
        projection = foundation.project(document, "slice-two")
        self.assertEqual(projection["author"]["states"]["char-anna"]["life_status"]["status"], "unresolved")
        self.assertEqual(foundation.timing("2026-03-20", "2026-03-21"), "applies")
        self.assertEqual(foundation.timing("2026-03-22", "2026-03-21"), "future")
        self.assertEqual(foundation.timing("2026-03-21T10:00", "2026-03-21T10:00"), "applies")

    def test_pre_event_state_is_unknown(self):
        document = fixture()
        document["entities"][2]["at"] = "2026-03-22"
        state = foundation.project(document, "slice-one")["author"]["states"]["char-anna"]["life_status"]
        self.assertEqual(state["status"], "migration_missing")
        self.assertEqual(state["reason"], "before_first_change")

    def test_intervals_come_from_successive_events(self):
        document = fixture()
        document["entities"].append({"id": "event-earlier", "type": "event", "name": "Earlier", "at": "2025-09-01",
            "changes": [{"target_ref": "char-anna", "key": "life_status", "value": "alive"}]})
        history = foundation.project(document, "slice-one")["author"]["intervals"]["char-anna"]["life_status"]
        self.assertEqual([entry["value"] for entry in history], ["alive", "dead"])
        self.assertEqual(history[0]["until"], history[1]["from"])
        self.assertIsNone(history[1]["until"])

    def test_absent_availability_defaults_to_hidden(self):
        document = fixture()
        del document["entities"][3]["availability"]
        del document["entities"][3]["asset"]
        self.assertEqual(foundation.project(document, "slice-two", ["doc-confession"])["player"], {"materials": [], "knowledge": []})

    def test_unknown_event_time_stays_unresolved(self):
        document = fixture()
        document["entities"][2]["at"] = {"status": "author_undecided"}
        state = foundation.project(document, "slice-one")["author"]["states"]["char-anna"]["life_status"]
        self.assertEqual(state["status"], "unresolved")

    def test_equal_or_overlapping_changes_are_rejected(self):
        for other_time in ("2025-09-03", "2025-09-03T12:00", {"status": "migration_missing"}):
            with self.subTest(other_time=other_time):
                document = fixture()
                event = copy.deepcopy(document["entities"][2])
                event.update(id="event-other", at=other_time)
                event["changes"][0]["value"] = "alive"
                document["entities"].append(event)
                with self.assertRaises(foundation.ValidationError):
                    foundation.validate(document)

    def test_invalid_identifiers_refs_fields_dates_and_duplicate_state_fail(self):
        mutations = [
            lambda d: d["entities"].append(copy.deepcopy(d["entities"][0])),
            lambda d: d["entities"][2]["changes"][0].update(target_ref="char-missing"),
            lambda d: d["entities"][0].update(facts={"life_status": "dead"}),
            lambda d: d["entities"][0].update(status_ch1="dead"),
            lambda d: d["entities"][2].update(at="2026-02-30"),
            lambda d: d["entities"][2].update(at="2026-03-21T10:00Z"),
            lambda d: d["entities"][2].update(at={"status": "probably"}),
            lambda d: d["entities"][3]["disclosures"][0]["assertion"].update(key="claims.missing"),
            lambda d: d["entities"][4].update(input_slice_ref="slice-two"),
            lambda d: d["entities"][5].update(ordinal=1),
            lambda d: d["entities"][0].update(type="person"),
            lambda d: d["entities"][0].update(id="person-anna"),
            lambda d: d["entities"][3].update(availabilty={}),
            lambda d: d["entities"][0].update(facts={"birth_date": "1980-01-01T10:00"}),
            lambda d: d["entities"][7].update(at="2026-01-01"),
            lambda d: d["entities"][0].update(relations=[{"type": [], "target_ref": "char-anna"}]),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                document = fixture()
                mutate(document)
                with self.assertRaises(foundation.ValidationError):
                    foundation.validate(document)

    def test_world_knowledge_separate_and_author_fields_never_leak(self):
        document = fixture()
        document["entities"].append({"id": "event-discovery", "type": "event", "name": "SECRET DISCOVERY", "at": "2026-03-20",
            "knowledge_changes": [{"observer_ref": "group-players", "assertion": {"owner_ref": "event-death", "key": "changes.0.value"}, "status": "established", "basis_refs": ["doc-confession"]}]})
        early = foundation.project(document, "slice-one")
        later = foundation.project(document, "slice-two")
        self.assertEqual(early["player"]["knowledge"], [])
        self.assertEqual(later["player"]["knowledge"], [{"value": "dead", "status": "established"}])
        output = json.dumps(later["player"])
        for secret in ("SECRET", "event-death", "event-discovery", "changes.0.value", "char-anna", "provenance", "states", "basis_refs"):
            self.assertNotIn(secret, output)

    def test_reference_payload_without_visibility_is_omitted(self):
        document = fixture()
        document["entities"].append({"id": "vehicle-example", "type": "vehicle", "name": "SECRET CAR"})
        document["entities"].append({"id": "event-owner", "type": "event", "name": "Owner", "at": "2025-01-01",
            "changes": [{"target_ref": "vehicle-example", "key": "owner_ref", "value": "char-anna"}],
            "knowledge_changes": [{"observer_ref": "group-players", "assertion": {"owner_ref": "event-owner", "key": "changes.0.value"}, "status": "reported", "basis_refs": ["event-owner"]}]})
        self.assertEqual(foundation.project(document, "slice-one")["player"]["knowledge"], [])
        probe = foundation.build_probe(document)
        self.assertIn("char-anna", probe["index"]["event-owner"]["outgoing"])
        self.assertIn("event-owner", probe["index"]["char-anna"]["incoming"])

    def test_index_is_separate_derived_test_metadata(self):
        probe = foundation.build_probe(fixture())
        self.assertEqual((probe["ownership"], probe["scope"]), ("DERIVED", "TEST"))
        self.assertIn("event-death", probe["index"]["char-anna"]["incoming"])
        self.assertIn("char-anna", probe["index"]["event-death"]["outgoing"])
        self.assertNotIn("index", probe["projections"]["slice-one"]["player"])

    def test_existing_legacy_ids_are_preserved(self):
        document = fixture()
        document["entities"].append({"id": "car-legacy", "type": "vehicle", "name": "Legacy car"})
        material = copy.deepcopy(document["entities"][3])
        material["id"] = "material-legacy"
        material.pop("disclosures")
        document["entities"].append(material)
        result = foundation.build_probe(document)
        self.assertIn("car-legacy", result["index"])
        self.assertIn("material-legacy", result["index"])
        self.assertNotIn("vehicle-legacy", result["index"])
        self.assertNotIn("doc-legacy", result["index"])

    def test_reverse_relation_is_not_second_primary_truth(self):
        document = fixture()
        document["entities"][0]["relations"] = [{"type": "spouse_of", "target_ref": "char-other"}]
        document["entities"].append({"id": "char-other", "type": "character", "name": "Other",
            "relations": [{"type": "spouse_of", "target_ref": "char-anna"}]})
        with self.assertRaises(foundation.ValidationError):
            foundation.validate(document)

    def test_output_is_deterministic_and_unchanged_file_is_not_rewritten(self):
        first = foundation.build_probe(fixture())
        second = foundation.build_probe(fixture())
        self.assertEqual(first, second)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "probe.json"
            self.assertTrue(foundation.write_if_changed(path, first))
            before = path.stat().st_mtime_ns
            self.assertFalse(foundation.write_if_changed(path, second))
            self.assertEqual(before, path.stat().st_mtime_ns)

    def test_yaml_duplicate_keys_and_automatic_date_coercion(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.yaml"
            path.write_text("at: 2026-03-21\n", encoding="utf-8")
            self.assertEqual(foundation.load_yaml(path)["at"], "2026-03-21")
            path.write_text("at: one\nat: two\n", encoding="utf-8")
            with self.assertRaises(foundation.ValidationError):
                foundation.load_yaml(path)

    def test_supplied_asset_hash_is_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            document = fixture()
            path = Path(folder) / "photo.bin"
            path.write_bytes(b"test asset")
            document["entities"][3]["asset"] = {"path": "photo.bin", "sha256": foundation.hashlib.sha256(path.read_bytes()).hexdigest()}
            foundation.validate(document, asset_root=folder)
            path.write_bytes(b"changed")
            with self.assertRaises(foundation.ValidationError):
                foundation.validate(document, asset_root=folder)


if __name__ == "__main__":
    unittest.main()
