# Spare

## Installation

Install via pipx

```bash
pipx install git+https://github.com/mattpotok/spare.git
```

Upgrade via pipX

```bash
pipx upgrade spare
```

## Configuration

Create a `~/.config/spare/config.toml` file with a list of profiles using the available providers listed below.

```toml
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

## Git Hooks

This repository uses custom Git hooks. To set them up:

1. Configure Git to use the custom hooks directory:

   ```bash
   git config core.hooksPath .githooks
   ```

2. Ensure the hooks are executable:

   ```bash
   chmod +x .githooks/*
   ```
