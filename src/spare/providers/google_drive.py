import os.path
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy, copytree, make_archive
from tempfile import TemporaryDirectory

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from spare.common import DATA_DIR_PATH

# TODO create a new directory

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


@dataclass
class File:
    id: str
    name: str
    parents: list[str]


class GoogleDriveService:
    _FILE_FIELDS = "id, name, parents"
    _SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    _TOKEN_FILE_PATH = DATA_DIR_PATH / "token.json"

    def __init__(self, credentials_path: Path):
        creds = self._get_creds(credentials_path)
        self._service = build("drive", "v3", credentials=creds)

    @classmethod
    def _get_creds(cls, credentials_path: Path):
        creds = None
        if os.path.exists(cls._TOKEN_FILE_PATH):
            creds = Credentials.from_authorized_user_file(
                cls._TOKEN_FILE_PATH, cls._SCOPES
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), cls._SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(cls._TOKEN_FILE_PATH, "w") as token:
                token.write(creds.to_json())

        return creds

    def create_folder(self, name: str, parent_id: str) -> File:
        body = {
            "mimeType": "application/vnd.google-apps.folder",
            "name": name,
            "parents": [parent_id],
        }

        try:
            response = (
                self._service.files()
                .create(body=body, fields=self._FILE_FIELDS)
                .execute()
            )
            return File(**response)
        except HttpError as error:
            print(f"Unable to create a folder '{name}': {error}")
            raise error

    def create_folder_hierarchy(self, path: Path) -> File | None:
        parent_id = "root"
        parts = path.parts
        if path.is_absolute() and len(parts) > 0:
            parts = parts[1:]

        try:
            folder = None
            for part in parts:
                folder = self.get_folder(part, parent_id)
                if not folder:
                    folder = self.create_folder(part, parent_id)

                parent_id = folder.id

            return folder
        except HttpError as error:
            print(f"Unable to create a folder hierarchy '{path}': {error}")
            raise error

    def get_files(self, parent_id: str | None = None):
        query = "trashed = false"
        if parent_id is not None:
            query += f" and '{parent_id}' in parents"

        files: list[File] = []
        page_token = ""
        while page_token is not None:
            response = (
                self._service.files()
                .list(
                    pageSize=100,
                    pageToken=page_token,
                    q=query,
                    fields=f"nextPageToken, files({self._FILE_FIELDS})",
                )
                .execute()
            )
            page_token = response.get("nextPageToken")
            files.extend([File(**file) for file in response.get("files", [])])

        return files

    def get_folder(self, name: str, parent_id: str = "root") -> File | None:
        query = (
            "mimeType = 'application/vnd.google-apps.folder'"
            f" and name = '{name}'"
            " and trashed = false"
        )

        if parent_id:
            query += f" and '{parent_id}' in parents"

        response = (
            self._service.files()
            .list(q=query, fields=f"files({self._FILE_FIELDS})")
            .execute()
        )

        files = response.get("files", [])
        if not files:
            return None

        return File(**files[0])

    def remove_file(self, file_id: str):
        self._service.files().delete(fileId=file_id).execute()

    def upload_file(self, file_path: Path, mimetype: str, parent_id: str = "root"):
        file_metadata = {"name": file_path.name, "parents": [parent_id]}
        media = MediaFileUpload(file_path, mimetype=mimetype, resumable=True)
        file = (
            self._service.files()
            .create(body=file_metadata, media_body=media, fields=self._FILE_FIELDS)
            .execute()
        )

        return file


def backup(paths: list[str], versions: int, folder_path: Path, credentials_path: Path):
    # TODO check for 0 version much sooner in the code
    if versions == 0:
        # TODO log a message
        return

    service = GoogleDriveService(credentials_path)
    folder = service.create_folder_hierarchy(folder_path)
    if not folder:
        # TODO log a message
        return

    with TemporaryDirectory() as tmp_dir:
        dir_path = Path(tmp_dir)
        archive_path = create_archive(dir_path, paths)
        service.upload_file(archive_path, "application/zip", folder.id)

    if versions <= 1:
        return

    files = service.get_files(folder.id)

    def sort_by_datetime(file) -> datetime:
        return datetime.fromisoformat(file.name.removesuffix(".zip"))

    files.sort(key=sort_by_datetime, reverse=True)

    for file in files[versions:]:
        service.remove_file(file.id)


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
