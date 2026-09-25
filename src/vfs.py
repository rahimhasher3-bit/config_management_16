import base64
import posixpath
import zipfile
from pathlib import Path


class VirtualFileSystem:
    def __init__(self, zip_path):
        self.zip_path = Path(zip_path)
        self.name = self.zip_path.stem
        self.files = {}
        self.directories = {"/"}

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
        self.directories = {"/"}

        with zipfile.ZipFile(self.zip_path, "r") as archive:
            for item in archive.infolist():
                name = item.filename.replace("\\", "/").strip("/")

                if not name:
                    continue

                if item.is_dir():
                    self._add_directory(name)
                    continue

                data = archive.read(item.filename)

                encoded_data = base64.b64encode(
                    data
                ).decode("ascii")

                self.files[name] = encoded_data
                self._add_parent_directories(name)

    def _add_directory(self, path):
        parts = path.split("/")
        current = ""

        for part in parts:
            current += "/" + part
            self.directories.add(current)

    def _add_parent_directories(self, file_path):
        parts = file_path.split("/")[:-1]
        current = ""

        for part in parts:
            current += "/" + part
            self.directories.add(current)

    def normalize_path(self, path, cwd="/"):
        if not path:
            return cwd

        path = path.replace("\\", "/")

        if path.startswith("/"):
            full_path = path
        else:
            full_path = posixpath.join(cwd, path)

        full_path = posixpath.normpath(full_path)

        if not full_path.startswith("/"):
            full_path = "/" + full_path

        return full_path

    def is_dir(self, path, cwd="/"):
        normalized = self.normalize_path(path, cwd)
        return normalized in self.directories

    def exists(self, path, cwd="/"):
        normalized = self.normalize_path(path, cwd)
        internal_path = normalized.lstrip("/")

        return (
            internal_path in self.files
            or normalized in self.directories
        )

    def list_dir(self, path=".", cwd="/"):
        target = self.normalize_path(path, cwd)

        if target not in self.directories:
            raise NotADirectoryError(
                f"Каталог не найден: {path}"
            )

        prefix = target.lstrip("/")

        if prefix:
            prefix += "/"

        items = set()

        for directory in self.directories:
            directory_path = directory.lstrip("/")

            if not directory_path.startswith(prefix):
                continue

            remainder = directory_path[len(prefix):]

            if remainder and "/" not in remainder:
                items.add(remainder)

        for file_path in self.files:
            if not file_path.startswith(prefix):
                continue

            remainder = file_path[len(prefix):]

            if remainder:
                items.add(remainder.split("/")[0])

        return sorted(items)

    def change_dir(self, path, cwd="/"):
        target = self.normalize_path(path, cwd)

        if target not in self.directories:
            raise NotADirectoryError(
                f"Каталог не найден: {path}"
            )

        return target

    def read_bytes(self, path, cwd="/"):
        normalized = self.normalize_path(path, cwd)
        internal_path = normalized.lstrip("/")

        if internal_path not in self.files:
            raise FileNotFoundError(
                f"Файл не найден в VFS: {path}"
            )

        return base64.b64decode(
            self.files[internal_path]
        )

    def read_text(self, path, cwd="/", encoding="utf-8"):
        data = self.read_bytes(path, cwd)
        return data.decode(encoding)

    def get_motd(self):
        if "motd" not in self.files:
            return None

        try:
            return self.read_text("/motd")
        except UnicodeDecodeError:
            return None