from argparse import ArgumentParser
from dataclasses import dataclass

import tomllib

from spare.common import CONFIG_DIR_PATH, CONFIG_FILE_PATH, DATA_DIR_PATH
from spare.providers.common import Profile, Provider
from spare.providers.google_drive import GoogleDriveProfile, GoogleDriveProvider


@dataclass
class Handler:
    profile: type[Profile]
    provider: type[Provider]


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
        raise KeyError(f"Profile '{args.profile}' does not exist")

    handlers: dict[str, Handler] = {
        "google-drive": Handler(GoogleDriveProfile, GoogleDriveProvider)
    }

    provider = profile.get("provider")
    if provider is None or provider not in handlers:
        raise ValueError(
            f"Invalid provider '{provider}', must be one of {list(handlers.keys())}"
        )

    handler = handlers[provider]
    profile = handler.profile.from_profile(profile)
    handler.provider.backup(profile)
