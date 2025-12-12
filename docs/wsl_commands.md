# WSL Development Commands

## Run Demo Bot
```bash
wsl -d Ubuntu -- bash -c "source ~/.local/bin/env && cd /mnt/c/Users/User/Projects/MedVoice && uv run python -m backend.app.demo_bot"
```

## Run App
```bash
wsl -d Ubuntu -- bash -c "source ~/.local/bin/env && cd /mnt/c/Users/User/Projects/MedVoice && uv run python -m backend.app.main"
```

## Interactive Shell
```bash
wsl -d Ubuntu
cd /mnt/c/Users/User/Projects/MedVoice
source ~/.local/bin/env
```

## Add Dependencies
```bash
uv add <package>
```

## Sync Dependencies
```bash
uv sync
```
