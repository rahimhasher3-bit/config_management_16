import os
import sys
import unittest
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

import emulator


class TestEmulator(unittest.TestCase):

    def test_parse_ls(self):
        self.assertEqual(
            emulator.parse_command("ls folder"),
            ["ls", "folder"]
        )

    def test_environment_variable(self):
        os.environ["TEST_VAR"] = "test_value"

        self.assertEqual(
            emulator.parse_command("cd $TEST_VAR"),
            ["cd", "test_value"]
        )

    def test_exit(self):
        self.assertFalse(
            emulator.execute_command(["exit"])
        )


if __name__ == "__main__":
    unittest.main()