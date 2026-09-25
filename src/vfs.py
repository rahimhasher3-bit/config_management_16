import base64
import zipfile
from pathlib import Path


class VirtualFileSystem:
    def __init__(self, zip_path):
        self.zip_path = Path(zip_path)
        self.name = self.zip_path.stem
        self.files = {}

    def load(self):
        if not self.zip_path.exists():
            raise FileNotFoundError(
                f"VFS не найдена: {self.zip_path}"
            )

        if not zipfile.is_zipfile(self.zip_path):
            raise ValueError(
                f"Неверный формат VFS: {self.zip_path}"
            )

        self.files.clear()

        with zipfile.ZipFile(self.zip_path, "r") as archive:
            for item in archive.infolist():

                if item.is_dir():
                    continue

                data = archive.read(item.filename)

                encoded_data = base64.b64encode(
                    data
                ).decode("ascii")

                self.files[item.filename] = encoded_data

    def exists(self, path):
        return path in self.files

    def read_bytes(self, path):
        if path not in self.files:
            raise FileNotFoundError(
                f"Файл не найден в VFS: {path}"
            )

        return base64.b64decode(
            self.files[path]
        )

    def read_text(self, path, encoding="utf-8"):
        data = self.read_bytes(path)
        return data.decode(encoding)

    def get_motd(self):
        if "motd" not in self.files:
            return None

        try:
            return self.read_text("motd")
        except UnicodeDecodeError:
            return None