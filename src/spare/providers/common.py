import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy, copytree, make_archive
from typing import Any

from marshmallow import ValidationError, fields


@dataclass
class Profile(ABC):
    @classmethod
    @abstractmethod
    def from_profile(cls, profile: dict[str, Any]) -> Any:
        pass


class Provider(ABC):
    @classmethod
    @abstractmethod
    def backup(cls, profile: Any) -> None:
        pass


class PathField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return str(value) if value is not None else None

    def _deserialize(self, value, attr, data, **kwargs):
        return Path(value) if value is not None else None


def create_archive(dir_path: Path, paths: list[str]) -> Path:
    archive_dir_path = dir_path / "archive"
    archive_dir_path.mkdir()

    for path in paths:
        path = Path(path)
        if not path.exists():
            # TODO throw an error here instead
            continue

        if path.is_file():
            copy(path, archive_dir_path)
        elif path.is_dir():
            copytree(path, archive_dir_path / path.name)
        else:
            # TODO throw an error here
            continue

    # Figure out if the os.chdir is necessary
    os.chdir(dir_path)
    archive_name = datetime.now(timezone.utc).isoformat(timespec="seconds")
    make_archive(archive_name, "zip", archive_dir_path)

    archive_path = dir_path / f"{archive_name}.zip"
    return archive_path


def validate_file_path(path: Path) -> None:
    if not path.exists():
        raise ValidationError(f"Path '{path}' does not exist.")

    if not path.is_file():
        raise ValidationError(f"Path '{path}' is not a file.")


def validate_version(version: int) -> None:
    if version == 0:
        raise ValidationError("Version must be non-zero.")
