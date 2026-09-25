import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

from vfs import VirtualFileSystem


class TestVFS(unittest.TestCase):

    def create_zip(self, files):
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".zip",
            delete=False
        )
        temp_file.close()

        with zipfile.ZipFile(
            temp_file.name,
            "w"
        ) as archive:
            for path, content in files.items():
                archive.writestr(path, content)

        return Path(temp_file.name)

    def test_load_file(self):
        zip_path = self.create_zip({
            "file.txt": "Hello VFS"
        })

        try:
            vfs = VirtualFileSystem(zip_path)
            vfs.load()

            self.assertTrue(
                vfs.exists("file.txt")
            )

            self.assertEqual(
                vfs.read_text("file.txt"),
                "Hello VFS"
            )

        finally:
            zip_path.unlink()

    def test_motd(self):
        zip_path = self.create_zip({
            "motd": "Welcome!"
        })

        try:
            vfs = VirtualFileSystem(zip_path)
            vfs.load()

            self.assertEqual(
                vfs.get_motd(),
                "Welcome!"
            )

        finally:
            zip_path.unlink()

    def test_deep_structure(self):
        zip_path = self.create_zip({
            "level1/level2/level3/file.txt":
                "Deep file"
        })

        try:
            vfs = VirtualFileSystem(zip_path)
            vfs.load()

            self.assertTrue(
                vfs.exists(
                    "level1/level2/level3/file.txt"
                )
            )

        finally:
            zip_path.unlink()

    def test_missing_file(self):
        zip_path = self.create_zip({
            "file.txt": "test"
        })

        try:
            vfs = VirtualFileSystem(zip_path)
            vfs.load()

            with self.assertRaises(
                FileNotFoundError
            ):
                vfs.read_text("missing.txt")

        finally:
            zip_path.unlink()


if __name__ == "__main__":
    unittest.main()