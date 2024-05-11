import unittest

from __tasklib__ import _build_system_distro, _parse_task_args, _resolve_deps


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
        tasks = [{"task1": {"deps": ["task2"]}},
                 {"task2": {"deps": ["task1"]}}]
        with self.assertRaises(ValueError):
            _resolve_deps(["task1", "task2"], tasks)


class TestSystemDistro(unittest.TestCase):
    def test_manjaro(self):
        contents = """NAME="Manjaro Linux"
PRETTY_NAME="Manjaro Linux"
ID=manjaro
ID_LIKE=arch
BUILD_ID=rolling
ANSI_COLOR="32;1;24;144;200"
HOME_URL="https://manjaro.org/"
DOCUMENTATION_URL="https://wiki.manjaro.org/"
SUPPORT_URL="https://forum.manjaro.org/"
BUG_REPORT_URL="https://docs.manjaro.org/reporting-bugs/"
PRIVACY_POLICY_URL="https://manjaro.org/privacy-policy/"
LOGO=manjarolinux
        """
        self.assertEqual(_build_system_distro(contents), "arch")

    def test_alpine(self):
        contents = """NAME="Alpine Linux"
ID=alpine
VERSION_ID=3.18.5
PRETTY_NAME="Alpine Linux v3.18"
HOME_URL="https://alpinelinux.org/"
BUG_REPORT_URL="https://gitlab.alpinelinux.org/alpine/aports/-/issues"
        """
        self.assertEqual(_build_system_distro(contents), "alpine")

    def test_ubuntu(self):
        contents = """PRETTY_NAME="Ubuntu 22.04.3 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.3 LTS (Jammy Jellyfish)"
VERSION_CODENAME=jammy
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
        """
        self.assertEqual(_build_system_distro(contents), "debian")


class TestParseTaskArgs(unittest.TestCase):
    def test_parse_no_arguments(self):
        task_args = "task[]"
        result = _parse_task_args(task_args)
        self.assertEqual(result, {})

    def test_parse_single_argument(self):
        task_args = "task[arg1=value1]"
        result = _parse_task_args(task_args)
        self.assertEqual(result, {"arg1": "value1"})

    def test_parse_multiple_arguments(self):
        task_args = "task[arg1=value1, arg2=value2, arg3=value3]"
        result = _parse_task_args(task_args)
        self.assertEqual(
            result, {"arg1": "value1", "arg2": "value2", "arg3": "value3"})

    def test_parse_with_spaces(self):
        task_args = "task[ arg1 = value1 , arg2 = value2 ]"
        result = _parse_task_args(task_args)
        self.assertEqual(result, {"arg1": "value1", "arg2": "value2"})

    def test_parse_empty_argument(self):
        task_args = "task[arg1=]"
        result = _parse_task_args(task_args)
        self.assertEqual(result, {"arg1": ""})


if __name__ == "__main__":
    unittest.main()
