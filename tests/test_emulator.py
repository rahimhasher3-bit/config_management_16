import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
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
        self.assertEqual(
            emulator.execute_command(["exit"]),
            "exit"
        )

    def test_vfs_name(self):
        self.assertEqual(
            emulator.get_vfs_name("test_vfs.zip"),
            "test_vfs"
        )

    def test_unknown_command(self):
        self.assertEqual(
            emulator.execute_command(["hello"]),
            "error"
        )

    def test_startup_script_stops_on_error(self):
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False
        ) as file:
            file.write("ls\n")
            file.write("hello\n")
            file.write("ls after_error\n")
            script_path = file.name

        try:
            output = io.StringIO()

            with redirect_stdout(output):
                result = emulator.run_startup_script(
                    script_path,
                    "test_vfs"
                )

            text = output.getvalue()

            self.assertEqual(result, "error")
            self.assertIn("hello", text)
            self.assertIn(
                "Стартовый скрипт остановлен.",
                text
            )
            self.assertNotIn("ls after_error", text)

        finally:
            os.remove(script_path)


if __name__ == "__main__":
    unittest.main()