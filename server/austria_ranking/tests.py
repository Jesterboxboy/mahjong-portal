from django.test import SimpleTestCase

from austria_ranking.calculator import calculate_points


class CalculatePointsTest(SimpleTestCase):
    def test_official_examples(self):
        self.assertEqual(calculate_points(100, 1), 1000)
        self.assertEqual(calculate_points(100, 25), 757)
        self.assertEqual(calculate_points(100, 75), 252)
        self.assertEqual(calculate_points(100, 100), 0)
        self.assertEqual(calculate_points(3, 2), 500)
