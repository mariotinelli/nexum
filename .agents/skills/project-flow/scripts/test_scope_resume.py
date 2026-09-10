import copy
import json
import tempfile
import unittest
from pathlib import Path

from test_review_legacy import fixtures, STAMP
from validate_scope_state import validate, validate_transition


class ScopeResumeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.state, _ = fixtures(self.root)
        s = self.state
        s["completed_phases"].append("catalog-approved")
        s["catalog"][0]["status"] = "completed"
        s["item_progress"][0].update(status="completed", issue_id=1, artifact_path="feature.md", state_path="feature-state.json", requirement_phase="completed", reconciliation_status="completed", started_at=STAMP, completed_at=STAMP)
        s["relations"][0]["from_issue_id"] = 1
        s["approvals"] = [dict(id="catalog", kind="complete-catalog-and-order", subject_sha256="a" * 64, approved_by="Reviewer", approved_at=STAMP, status="valid")]
        s["continuation_decisions"] = [dict(after_item_id="first", decision="stop", decided_by="Reviewer", decided_at=STAMP)]
        s["pauses"] = [dict(id="stop", status="paused", kind="voluntary-stop", previous_phase="items-processing", resume_phase="items-processing", reason="stop", resume_condition="user continues", paused_at=STAMP)]

    def check(self, state, name):
        path = self.root / name
        path.write_text(json.dumps(state), encoding="utf-8")
        return validate(path)

    def resume(self):
        s = copy.deepcopy(self.state)
        s["phase"] = "items-processing"
        s["pauses"][-1].update(status="resumed", resumed_at="2026-01-02T00:00:00Z", resume_evidence="user continues")
        s["continuation_decisions"].append(dict(after_item_id="first", decision="continue", decided_by="Reviewer", decided_at="2026-01-02T00:00:00Z"))
        return s

    def test_resume_preserves_stop_and_can_start_next_item(self):
        old = self.check(self.state, "old.json")
        s = self.resume()
        current = self.check(s, "new.json")
        validate_transition(old, current)
        s["catalog"][1]["status"] = "in-progress"
        s["item_progress"][1]["status"] = "in-progress"
        self.check(s, "started.json")
        self.assertEqual(s["continuation_decisions"][0]["decision"], "stop")

    def test_duplicate_without_resume_is_rejected(self):
        s = self.resume()
        s["pauses"][-1]["status"] = "paused"
        with self.assertRaises(ValueError):
            self.check(s, "bad.json")

    def test_resume_without_new_decision_is_rejected(self):
        s = self.resume()
        s["continuation_decisions"].pop()
        with self.assertRaises(ValueError):
            self.check(s, "bad.json")

    def test_old_unrelated_pause_cannot_authorize_resume(self):
        s = self.resume()
        s["continuation_decisions"][0]["decided_at"] = "2026-01-03T00:00:00Z"
        with self.assertRaises(ValueError):
            self.check(s, "bad.json")

    def test_rewriting_original_stop_is_rejected(self):
        old = self.check(self.state, "old.json")
        s = self.resume()
        s["continuation_decisions"] = [s["continuation_decisions"][-1]]
        current = self.check(s, "new.json")
        with self.assertRaises(ValueError):
            validate_transition(old, current)
