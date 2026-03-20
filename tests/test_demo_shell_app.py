import importlib.util
from pathlib import Path
import unittest


APP_PATH = Path(__file__).resolve().parents[1] / "demo_shell" / "app.py"
spec = importlib.util.spec_from_file_location("demo_shell_app", APP_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class DemoShellAppTest(unittest.TestCase):
    def test_build_console_from_report_exposes_four_surfaces(self) -> None:
        report = module._safe_json(Path(__file__).resolve().parents[1] / "examples" / "sample_report_redacted.json")
        console = module._build_console_from_report(report, mint_hint="", judge_mode=False, source_label="sample")
        self.assertEqual(console["executive_decision"]["action"], "BLOCK")
        self.assertEqual(set(console["evidence_surfaces"].keys()), {"funding", "control", "permission", "issuer"})
        self.assertGreater(console["what_if"]["aggregate_score"], 0.0)
        self.assertTrue(any(toggle["available"] for toggle in console["what_if"]["toggles"]))
        self.assertIn("hard_evidence_brief", console)
        self.assertIn("decision_trace", console)
        self.assertIn("watchlist", console)

    def test_review_store_roundtrip(self) -> None:
        original_file = module.REVIEW_STATE_FILE
        original_dir = module.REVIEW_STATE_DIR
        temp_dir = Path(__file__).resolve().parent / ".tmp_review_state"
        temp_file = temp_dir / "case_reviews.json"
        module.REVIEW_STATE_DIR = temp_dir
        module.REVIEW_STATE_FILE = temp_file
        try:
            saved = module._update_case_review(
                "Mint111",
                "BLOCK",
                80.0,
                {"status": "UNDER_REVIEW", "priority": "HIGH", "reviewer": "qa", "note": "needs further diligence"},
            )
            loaded = module._get_case_review("Mint111", "BLOCK", 80.0)
            self.assertEqual(saved["status"], "UNDER_REVIEW")
            self.assertEqual(loaded["reviewer"], "qa")
            self.assertGreaterEqual(len(loaded["audit"]), 1)
        finally:
            module.REVIEW_STATE_FILE = original_file
            module.REVIEW_STATE_DIR = original_dir
            if temp_file.exists():
                temp_file.unlink()
            if temp_dir.exists():
                temp_dir.rmdir()

    def test_extended_endpoints(self) -> None:
        client = module.APP.test_client()
        temp_dir = Path(__file__).resolve().parent / ".tmp_state_full"
        review_file = temp_dir / "case_reviews.json"
        watchlist_file = temp_dir / "watchlist_state.json"
        original_dir = module.REVIEW_STATE_DIR
        original_review = module.REVIEW_STATE_FILE
        original_watch = module.WATCHLIST_STATE_FILE
        module.REVIEW_STATE_DIR = temp_dir
        module.REVIEW_STATE_FILE = review_file
        module.WATCHLIST_STATE_FILE = watchlist_file
        try:
            analyze = client.post("/api/analyze", json={"mint": "Mint11111111111111111111111111111111"})
            self.assertIn(analyze.status_code, {502, 503})
            payload = analyze.get_json()
            self.assertTrue(isinstance(payload.get("console_view"), dict))

            console = payload["console_view"]
            sim = client.post(
                "/api/simulate",
                json={"console": console, "selected_toggle_ids": [console["what_if"]["toggles"][0]["id"]]},
            )
            self.assertEqual(sim.status_code, 200)
            self.assertTrue(sim.get_json().get("simulation"))

            watch = client.post("/api/watchlist", json={"mint": console["meta"]["mint_raw"], "tracked": True})
            self.assertEqual(watch.status_code, 200)
            self.assertTrue(watch.get_json()["watchlist"]["tracked"])

            recheck = client.post(
                "/api/recheck",
                json={
                    "mint": console["meta"]["mint_raw"],
                    "action": console["executive_decision"]["action"],
                    "risk_score": console["executive_decision"]["risk_score"],
                    "confidence_pct": console["executive_decision"]["confidence_pct"],
                    "summary": console["executive_decision"]["summary"],
                },
            )
            self.assertEqual(recheck.status_code, 200)
            self.assertGreaterEqual(len(recheck.get_json()["watchlist"]["history"]), 1)

            export = client.post("/api/export-case", json={"console": console})
            self.assertEqual(export.status_code, 200)
            self.assertTrue(export.get_json()["export"]["action"])
        finally:
            module.REVIEW_STATE_DIR = original_dir
            module.REVIEW_STATE_FILE = original_review
            module.WATCHLIST_STATE_FILE = original_watch
            if review_file.exists():
                review_file.unlink()
            if watchlist_file.exists():
                watchlist_file.unlink()
            if temp_dir.exists():
                temp_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
