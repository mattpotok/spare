import tomllib
from argparse import ArgumentParser
from pathlib import Path

from spare.common import CONFIG_DIR_PATH, CONFIG_FILE_PATH, DATA_DIR_PATH
from spare.providers import google_drive


def initialize():
    CONFIG_DIR_PATH.mkdir(exist_ok=True, parents=True)
    CONFIG_FILE_PATH.touch(exist_ok=True)

    DATA_DIR_PATH.mkdir(exist_ok=True, parents=True)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--profile", type=str, required=True)

    args = parser.parse_args()

    return args


def main():
    initialize()

    args = parse_args()

    with open(CONFIG_FILE_PATH, "rb") as file:
        config = tomllib.load(file)

    profiles = config.get("profiles", {})
    profile = profiles.get(args.profile, None)
    if not profile:
        # TODO log an error here
        raise ValueError(f"Invalid profile '{args.profile}'")

    if profile.get("provider") == "google-drive":
        credentials_path = Path(profile.get("credentials_path", ""))
        folder_path = Path(profile.get("folder", ""))
        paths = profile.get("paths", [])
        versions = profile.get("versions", -1)

        google_drive.backup(paths, versions, folder_path, credentials_path)
