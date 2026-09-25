import io
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

import emulator
from vfs import VirtualFileSystem


class TestStage4(unittest.TestCase):

    def setUp(self):
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".zip",
            delete=False
        )
        temp_file.close()

        self.zip_path = Path(temp_file.name)

        with zipfile.ZipFile(
            self.zip_path,
            "w"
        ) as archive:
            archive.writestr("motd", "Test VFS")
            archive.writestr(
                "level1/file1.txt",
                "File 1"
            )
            archive.writestr(
                "level1/level2/file2.txt",
                "File 2"
            )

        self.vfs = VirtualFileSystem(
            self.zip_path
        )
        self.vfs.load()

        self.state = {
            "cwd": "/"
        }

    def tearDown(self):
        self.zip_path.unlink()

    def test_ls_root(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = emulator.execute_command(
                ["ls"],
                self.vfs,
                self.state
            )

        self.assertEqual(result, "continue")
        self.assertIn("level1", output.getvalue())
        self.assertIn("motd", output.getvalue())

    def test_cd(self):
        result = emulator.execute_command(
            ["cd", "level1"],
            self.vfs,
            self.state
        )

        self.assertEqual(result, "continue")
        self.assertEqual(
            self.state["cwd"],
            "/level1"
        )

    def test_cd_parent(self):
        self.state["cwd"] = "/level1/level2"

        emulator.execute_command(
            ["cd", ".."],
            self.vfs,
            self.state
        )

        self.assertEqual(
            self.state["cwd"],
            "/level1"
        )

    def test_cd_error(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = emulator.execute_command(
                ["cd", "missing"],
                self.vfs,
                self.state
            )

        self.assertEqual(result, "error")

    def test_date(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = emulator.execute_command(
                ["date"],
                self.vfs,
                self.state
            )

        self.assertEqual(result, "continue")
        self.assertTrue(output.getvalue().strip())

    def test_cal(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = emulator.execute_command(
                ["cal", "9", "2026"],
                self.vfs,
                self.state
            )

        self.assertEqual(result, "continue")
        self.assertIn(
            "2026",
            output.getvalue()
        )


if __name__ == "__main__":
    unittest.main()