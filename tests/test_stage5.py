import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from vfs import VirtualFileSystem


class TestStage5(unittest.TestCase):

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
            archive.writestr(
                "level1/file1.txt",
                "Test file"
            )

        self.vfs = VirtualFileSystem(
            self.zip_path
        )
        self.vfs.load()

    def tearDown(self):
        self.zip_path.unlink()

    def test_chmod_file(self):
        self.vfs.chmod(
            "/level1/file1.txt",
            "600"
        )

        self.assertEqual(
            self.vfs.get_permissions(
                "/level1/file1.txt"
            ),
            "600"
        )

    def test_chmod_directory(self):
        self.vfs.chmod(
            "/level1",
            "700"
        )

        self.assertEqual(
            self.vfs.get_permissions(
                "/level1"
            ),
            "700"
        )

    def test_invalid_mode(self):
        with self.assertRaises(
            ValueError
        ):
            self.vfs.chmod(
                "/level1/file1.txt",
                "999"
            )

    def test_missing_file(self):
        with self.assertRaises(
            FileNotFoundError
        ):
            self.vfs.chmod(
                "/missing.txt",
                "600"
            )

    def test_chmod_only_in_memory(self):
        before = self.zip_path.read_bytes()

        self.vfs.chmod(
            "/level1/file1.txt",
            "600"
        )

        after = self.zip_path.read_bytes()

        self.assertEqual(
            before,
            after
        )

        new_vfs = VirtualFileSystem(
            self.zip_path
        )
        new_vfs.load()

        self.assertEqual(
            new_vfs.get_permissions(
                "/level1/file1.txt"
            ),
            "644"
        )


if __name__ == "__main__":
    unittest.main()
    