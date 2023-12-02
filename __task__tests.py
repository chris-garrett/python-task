import unittest
from __task__ import _resolve_deps


class TestResolveDeps(unittest.TestCase):
    def test_no_dependencies(self):
        # Test when there are no dependencies
        tasks = [{"task1": {}}, {"task2": {}}, {"task3": {}}]
        result = _resolve_deps(["task1", "task2", "task3"], tasks)
        self.assertEqual(result, ["task1", "task2", "task3"])

    def test_simple_dependencies(self):
        # Test when there are simple dependencies
        tasks = [
            {"task1": {"deps": []}},
            {"task2": {"deps": ["task1"]}},
            {"task3": {"deps": ["task1", "task2", "task4"]}},
            {"task4": {"deps": ["task1"]}},
        ]
        result = _resolve_deps(["task2", "task3"], tasks)
        self.assertEqual(result, ["task1", "task2", "task4", "task3"])

    def test_circular_dependencies(self):
        # Test when there are circular dependencies (should raise an error)
        tasks = [{"task1": {"deps": ["task2"]}}, {"task2": {"deps": ["task1"]}}]
        with self.assertRaises(ValueError):
            _resolve_deps(["task1", "task2"], tasks)


if __name__ == "__main__":
    unittest.main()
