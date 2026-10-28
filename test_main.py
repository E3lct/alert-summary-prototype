import unittest

from main import count_alerts, load_events, local_summary


class SummaryTests(unittest.TestCase):
    def test_seven_days_excludes_older_events(self):
        facts = count_alerts(load_events(), 7)
        self.assertEqual(facts["total"], 4)
        self.assertEqual(facts["by_type"], {"fall": 2, "offline": 2})

    def test_one_day_includes_only_today(self):
        facts = count_alerts(load_events(), 1)
        self.assertEqual(facts["total"], 1)
        self.assertEqual(facts["by_type"], {"fall": 1})

    def test_no_matching_events(self):
        facts = count_alerts([], 7)
        self.assertEqual(facts["total"], 0)
        self.assertIn("没有告警", local_summary(facts))


if __name__ == "__main__":
    unittest.main()
