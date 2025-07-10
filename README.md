# Spare

## Installation

Via pipx

```bash
pipx install git+https://github.com/mattpotok/spare.git
```

## Configuration

Create a `~/.config/spare/config.toml` file with a list of profiles using the available providers listed below.

```
[profiles]

[profiles.a-google-drive-profile]
credentials_path = "/a/path/to/Google/credentials.json"
destination = "/a/Google/Drive/directory"
provider = "google-drive"
sources = [
    "/a/file/to/backup.txt",
    "/a/directory/to/backup/",
]
versions = N  # A non-zero number where negative means infinite versions
```
