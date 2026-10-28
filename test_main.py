import unittest

from main import count_alerts, load_events, local_summary, prompt_for


class SummaryTests(unittest.TestCase):
    def test_seven_days_excludes_older_events(self):
        facts = count_alerts(load_events(), 7)
        self.assertEqual(facts["total"], 4)
        self.assertEqual(facts["by_type"], {"fall": 2, "offline": 2})
        self.assertEqual(facts["selected_ids"], ["demo-001", "demo-002", "demo-003", "demo-004"])

    def test_one_day_includes_only_today(self):
        facts = count_alerts(load_events(), 1)
        self.assertEqual(facts["total"], 1)
        self.assertEqual(facts["by_type"], {"fall": 1})

    def test_no_matching_events(self):
        facts = count_alerts([], 7)
        self.assertEqual(facts["total"], 0)
        self.assertEqual(facts["selected_ids"], [])
        self.assertIn("没有告警", local_summary(facts))

    def test_prompt_uses_counted_facts_without_event_ids(self):
        facts = count_alerts(load_events(), 7)
        prompt = prompt_for(facts)
        self.assertIn("近7天", prompt)
        self.assertIn("4次", prompt)
        self.assertIn("跌倒2次、设备离线2次", prompt)
        self.assertNotIn("demo-001", prompt)


if __name__ == "__main__":
    unittest.main()
