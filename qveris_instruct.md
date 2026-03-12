# Install Qveris Skill

## Prerequisites

A valid `QVERIS_API_KEY` is required. If the user has not provided one, **stop and ask**:

> Please provide your QVERIS_API_KEY. You can obtain one from https://qveris.ai

Do not proceed until a key value is provided.

## Steps

### 1. Create directories

```bash
mkdir -p ~/.openclaw/skills/qveris/scripts
```

### 2. Download skill definition

```bash
curl -fSL https://qveris.ai/skill/SKILL.md -o ~/.openclaw/skills/qveris/SKILL.md
```

### 3. Download tool script

```bash
curl -fSL https://qveris.ai/skill/scripts/qveris_tool.mjs -o ~/.openclaw/skills/qveris/scripts/qveris_tool.mjs
```

### 4. Set QVERIS_API_KEY globally

Append the key to `~/.bashrc` (or `~/.zshrc` if the user uses zsh) so it persists across sessions. Replace `<USER_PROVIDED_KEY>` with the actual key value.

```bash
echo 'export QVERIS_API_KEY="<USER_PROVIDED_KEY>"' >> ~/.bashrc
source ~/.bashrc
```

### 5. Verify

```bash
test -f ~/.openclaw/skills/qveris/SKILL.md && echo "SKILL.md OK" || echo "SKILL.md MISSING"
test -f ~/.openclaw/skills/qveris/scripts/qveris_tool.mjs && echo "qveris_tool.mjs OK" || echo "qveris_tool.mjs MISSING"
echo "QVERIS_API_KEY=${QVERIS_API_KEY:+is set}"
node ~/.openclaw/skills/qveris/scripts/qveris_tool.mjs search "stock price" --limit 5
```

This should return results without errors. All checks must pass before the installation is considered complete.
