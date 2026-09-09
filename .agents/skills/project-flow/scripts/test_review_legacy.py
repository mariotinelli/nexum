"""Run with python -B -m unittest discover -s <skill>/scripts -p 'test_*.py'."""

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from catalog_contract import digest
from review_legacy import validate_relation_history, validate_review
from validate_scope_state import validate, validate_transition


STAMP = "2026-01-01T00:00:00Z"
SCRIPTS = Path(__file__).resolve().parent


def fixtures(root):
    (root / "sources").mkdir()
    content = "# Source: evidence\n\n- Source ID: `evidence`\n- Type: test\n- Origin: fixture\n- Original SHA-256: `" + "a" * 64 + "`\n- Extraction: static\n\n## Extracted content\n\nA complete capability.\n"
    (root / "sources/evidence.md").write_bytes(content.encode("utf-8"))
    source = dict(id="evidence", name="evidence", type="test", origin="fixture", status="normalized", decision_reconciliation="not-applicable", path="sources/evidence.md", original_sha256="a" * 64, hash_unavailable_reason=None, normalized_sha256=hashlib.sha256(content.encode()).hexdigest(), extraction_method="static", fully_read=True)
    items = [dict(id=i, type="Feature", name=i, human_objective=i, actors=["Member"], observable_result_or_deviation=i, evidence=["evidence"], dependencies=[] if i == "first" else ["first"], separation_reason=i, suggested_position=n, status="pending", candidate_ids=["candidate-" + i], lifecycle="active") for n, i in enumerate(("first", "second"), 1)]
    progress = [dict(catalog_item_id=i["id"], status="pending", issue_id=None, artifact_path=None, state_path=None, requirement_phase=None, functional_gaps=[], reconciliation_status="pending", started_at=None, completed_at=None) for i in items]
    old = dict(schema_version=2, run_id="00000000-0000-4000-8000-000000000001", internal_identity="00000000-0000-4000-8000-000000000002", mode="new-scope", phase="paused", completed_phases=["mode-confirmed", "inputs-normalized", "repository-analyzed", "catalog-proposed"], identity=dict(redmine_user_id=1, display_name="Reviewer", confirmed_at=STAMP), redmine=dict(project_id=1), sources=[source], source_allocation=[dict(source_id="evidence", ownership="scope-shared", item_ids=["first", "second"], path=source["path"])], repository=dict(stack=["test"], vocabulary=[], exclusions=["secrets"]), candidates=[dict(id=i["candidate_ids"][0], status="decided", catalog_item_ids=[i["id"]], rationale="fixture") for i in items], catalog=items, dependency_graph=[dict(item="second", blocked_by="first")], parallel_ready_groups=[["first"], ["second"]], suggested_order=["first", "second"], approvals=[], pauses=[dict(id="review", status="paused", kind="catalog-change", previous_phase="catalog-approved", resume_phase="catalog-approved", reason="explicit review", resume_condition="approval", paused_at=STAMP)], lock=dict(item_key="test", lock_id="00000000-0000-4000-8000-000000000003", path="docs/harness/.locks/" + hashlib.sha256(b"test").hexdigest() + ".lock.json", acquired_at=STAMP), item_progress=progress, continuation_decisions=[], catalog_changes=[], relations=[dict(stable_key="blocks:first:second", from_item_id="first", to_item_id="second", relation_type="blocks", from_issue_id=None, to_issue_id=None, status="planned", approval_id=None, reconciliation_status="pending", completed_at=None)], validations=[], final_summary=None)
    new = copy.deepcopy(old)
    new["schema_version"] = 3
    new["legacy_review"] = dict(previous_state=copy.deepcopy(old), reason="merge complete capability")
    confirmation = dict(statement="WEB for members", confirmed_by="Reviewer", confirmed_at=STAMP)
    new["title_convention"] = dict(surfaces=["WEB"], audiences=["MEMBER"], audience_mode="single", shared_public_rule="Members", confirmation=confirmation)
    for item in new["catalog"]:
        item["status"] = item["lifecycle"] = "retired"
    merged = {**copy.deepcopy(items[0]), "id": "combined", "name": "Combined", "candidate_ids": ["candidate-first", "candidate-second"]}
    new["catalog"].append(merged)
    for item in new["catalog"]:
        item["delivery"] = dict(surface="WEB", audiences=["MEMBER"], name=item["name"], title="[WEB] [MEMBER] " + item["name"], visible_delivery=item["name"], user_result=item["name"], included=["complete operation"], boundary_reason="cohesion")
    for entry in new["item_progress"]:
        entry["status"] = "retired"
    new["item_progress"].append({**copy.deepcopy(progress[0]), "catalog_item_id": "combined"})
    for candidate in new["candidates"]:
        candidate["catalog_item_ids"].append("combined")
    new["source_allocation"][0]["item_ids"].append("combined")
    new["relations"][0]["status"] = "retired"
    new["dependency_graph"] = []
    new["parallel_ready_groups"] = [["combined"]]
    new["suggested_order"] = ["combined"]
    new["dependency_reasons"] = []
    new["order_reasons"] = [dict(item="combined", basis="usage-lifecycle", rationale="complete journey", evidence=["evidence"])]
    new["input_inventory"] = dict(selection="selected-files", requested=["evidence"], entries=[dict(source_id="evidence", origin="fixture", role="behavioral", decision=None)], references=[])
    new["behaviors"] = [dict(id="operation", description="Complete operation", evidence=[dict(source_id="evidence", locator="Extracted content")], evidence_kind="demonstrated", audiences=["MEMBER"], disposition="covered", owner="combined", consumers=[], repository=dict(status="absent", evidence=["fixture"], proposed_change="new capability"), decision=None)]
    return old, new


def approve(state):
    state["catalog_changes"].append(dict(id="merge", kind="merge", affected_item_ids=["first", "second", "combined"], source_allocation_impact="combined", graph_impact="retire old edge", order_impact="one capability", preserved_issue_ids=[], artifact_paths=[], approved_by="Reviewer", approved_at=STAMP, names_impact="combined", audiences_impact="member", deliveries_impact="cohesive", coverage_impact="one owner"))
    state["approvals"].append(dict(id="new-approval", kind="complete-catalog-and-order", subject_sha256=digest(state), approved_by="Reviewer", approved_at=STAMP, status="valid"))


class LegacyReviewTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.old, self.new = fixtures(self.root)

    def write(self, name, state):
        path = self.root / name
        path.write_text(json.dumps(state), encoding="utf-8")
        return path

    def review(self, draft=True):
        previous = validate(self.write("old.json", self.old))
        current = validate(self.write("new.json", self.new))
        validate_review(previous, current, scope=True, draft=draft)

    def test_unapproved_merge_is_a_valid_draft(self):
        self.review()
        self.assertEqual(self.new["approvals"], [])

    def test_approved_merge_preserves_snapshot_and_retired_relation(self):
        approve(self.new)
        self.review(draft=False)
        self.assertEqual(self.old, self.new["legacy_review"]["previous_state"])

    def test_replacement_requires_approval_and_change_record(self):
        with self.assertRaisesRegex(ValueError, "attributed catalog change"):
            self.review(draft=False)
        approve(self.new)
        self.new["approvals"] = []
        with self.assertRaisesRegex(ValueError, "new complete catalog approval"):
            self.review(draft=False)

    def test_draft_cannot_claim_approval(self):
        approve(self.new)
        with self.assertRaisesRegex(ValueError, "must not contain valid approvals"):
            self.review()

    def test_revision_without_snapshot_still_rejects_changed_graph(self):
        del self.new["legacy_review"]
        with self.assertRaisesRegex(ValueError, "legacy review rewrote"):
            self.review()

    def test_enrichment_without_catalog_revision_remains_supported(self):
        candidate = copy.deepcopy(self.old)
        candidate["schema_version"] = 3
        candidate["approvals"] = [dict(id="new", kind="complete-catalog-and-order", status="valid")]
        validate_review(self.old, candidate, scope=True)

    def test_catalog_candidate_and_source_ids_cannot_disappear(self):
        for key in ("candidates", "source_allocation"):
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.new)
                candidate[key] = []
                with self.assertRaisesRegex(ValueError, "identities"):
                    validate_review(self.old, candidate, scope=True, draft=True)

    def test_retired_status_is_not_accepted_in_legacy_scope(self):
        self.old["relations"][0]["status"] = "retired"
        with self.assertRaisesRegex(ValueError, "invalid relation status"):
            validate(self.write("old.json", self.old))

    def test_exact_snapshot_is_required(self):
        self.new["legacy_review"]["previous_state"]["dependency_graph"] = []
        with self.assertRaisesRegex(ValueError, "exact previous state"):
            self.review()

    def test_losing_a_retired_item_is_rejected(self):
        self.new["catalog"].pop(0)
        with self.assertRaisesRegex(ValueError, "every item ID"):
            validate_review(self.old, self.new, scope=True, draft=True)

    def test_rewriting_retired_catalog_content_is_rejected(self):
        self.new["catalog"][0]["human_objective"] = "different history"
        with self.assertRaisesRegex(ValueError, "retired item"):
            validate_review(self.old, self.new, scope=True, draft=True)

    def test_identity_sources_and_prior_validations_are_preserved(self):
        for key in ("run_id", "identity", "sources", "validations"):
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.new)
                candidate[key] = None
                with self.assertRaises(ValueError):
                    validate_review(self.old, candidate, scope=True, draft=True)

    def test_issue_artifact_and_completed_progress_cannot_be_lost(self):
        fields = dict(issue_id=123, artifact_path="features/123-first", state_path="features/123-first/state.json", requirement_phase="completed", completed_at=STAMP)
        self.old["item_progress"][0].update(fields)
        self.new["legacy_review"]["previous_state"] = copy.deepcopy(self.old)
        self.new["item_progress"][0].update(fields)
        for key in fields:
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.new)
                candidate["item_progress"][0][key] = None
                with self.assertRaisesRegex(ValueError, "item progress"):
                    validate_review(self.old, candidate, scope=True, draft=True)

    def test_removing_relation_history_is_rejected(self):
        self.new["relations"] = []
        with self.assertRaisesRegex(ValueError, "relation history"):
            self.review()

    def test_changing_retired_relation_endpoints_is_rejected(self):
        self.new["relations"][0]["to_item_id"] = "combined"
        with self.assertRaisesRegex(ValueError, "relation history"):
            self.review()

    def test_published_or_approved_relations_cannot_be_retired(self):
        for fields in (dict(approval_id="approved"), dict(status="completed", completed_at=STAMP, reconciliation_status="completed")):
            with self.subTest(fields=fields):
                old = {**self.old["relations"][0], **fields}
                with self.assertRaisesRegex(ValueError, "relation history"):
                    validate_relation_history([old], [{**old, "status": "retired"}])

    def test_retired_relation_with_remote_completion_is_invalid(self):
        self.new["relations"][0]["completed_at"] = STAMP
        with self.assertRaisesRegex(ValueError, "only unpublished"):
            validate(self.write("new.json", self.new))

    def test_normal_relation_publication_remains_possible(self):
        old = self.old["relations"][0]
        published = {**old, "status": "completed", "from_issue_id": 123, "to_issue_id": 456, "approval_id": "approved", "reconciliation_status": "completed", "completed_at": STAMP}
        validate_relation_history([old], [published], allow_progress=True)
        with self.assertRaisesRegex(ValueError, "relation history"):
            validate_relation_history([published], [{**published, "from_issue_id": 789}], allow_progress=True)

    def test_normal_publication_preserves_existing_relation_approval(self):
        old = {**self.old["relations"][0], "approval_id": "approved-payload"}
        with self.assertRaisesRegex(ValueError, "relation history"):
            validate_relation_history([old], [{**old, "approval_id": "other-payload"}], allow_progress=True)

    def test_old_approval_must_be_preserved_and_invalidated(self):
        approval = dict(id="old", kind="complete-catalog-and-order", subject_sha256="b" * 64, approved_by="Reviewer", approved_at=STAMP, status="valid")
        self.old["approvals"] = [approval]
        self.new["legacy_review"]["previous_state"] = copy.deepcopy(self.old)
        with self.assertRaisesRegex(ValueError, "invalidate"):
            self.review()
        self.new["approvals"] = [{**approval, "status": "invalidated", "invalidated_reason": "explicit revision", "invalidated_at": STAMP}]
        self.review()

    def test_completed_phases_cannot_advance_during_review(self):
        self.new["completed_phases"].append("catalog-approved")
        with self.assertRaisesRegex(ValueError, "completed facts"):
            validate_review(self.old, self.new, scope=True, draft=True)

    def test_snapshot_is_immutable_after_migration(self):
        candidate = copy.deepcopy(self.new)
        candidate["legacy_review"]["reason"] = "rewritten"
        with self.assertRaisesRegex(ValueError, "snapshot"):
            validate_transition(self.new, candidate)

    def test_snapshot_and_retired_relations_are_part_of_approval_hash(self):
        for mutate in (lambda s: s["legacy_review"].update(reason="another reason"), lambda s: s["relations"][0].update(to_item_id="combined")):
            candidate = copy.deepcopy(self.new)
            mutate(candidate)
            self.assertNotEqual(digest(self.new), digest(candidate))

    def test_cli_draft_validation_does_not_mutate_or_approve(self):
        old = self.write("old.json", self.old)
        new = self.write("new.json", self.new)
        before = new.read_bytes()
        command = [sys.executable, "-B", str(SCRIPTS / "validate_scope_state.py"), str(new), "--previous", str(old), "--review-legacy"]
        result = subprocess.run(command + ["--draft"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("approval required", result.stdout)
        self.assertEqual(new.read_bytes(), before)
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)

    def test_cli_draft_requires_explicit_legacy_review(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "validate_scope_state.py"), str(self.write("new.json", self.new)), "--draft"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
