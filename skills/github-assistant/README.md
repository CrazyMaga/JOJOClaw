# OpenClaw GitHub Skill

A skill that lets your AI assistant query and manage GitHub repositories.

## Features

- 馃搵 **List Repos** 鈥?View your repositories with filters
- 馃搳 **Get Repo Details** 鈥?Stars, forks, language, last updated
- 馃攧 **Check CI Status** 鈥?Monitor CI/CD pipelines
- 馃摑 **Create Issues** 鈥?Open issues from conversation
- 馃搧 **Create Repos** 鈥?Create new repositories
- 馃攳 **Search Repos** 鈥?Find repos by name/query
- 馃搳 **Recent Activity** 鈥?View recent commits

## Prerequisites

- OpenClaw gateway running
- Node.js 18+
- GitHub account with a Personal Access Token (PAT)

## Setup

### 1. Generate a GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `openclaw-github-skill`
4. Scopes (permissions):
   - `repo` 鈥?Full control of private repositories
   - `public_repo` 鈥?Limited access to public repositories only
   - `read:user` 鈥?Read user profile data (optional)
5. Copy the token

### 2. Configure Credentials

**Option A: Environment Variables (Recommended for local use)**

Set before starting OpenClaw:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
export GITHUB_USERNAME="your_github_username"
```

**Option B: OpenClaw Config**

Add to `~/.openclaw/openclaw.json`:

```json
{
  "github": {
    "token": "ghp_your_token_here",
    "username": "your_username"
  }
}
```

### 3. Restart OpenClaw

```bash
openclaw gateway restart
```

## Usage

```
You: List my Python repositories
Bot: [lists your Python repositories]

You: Check CI status on my-project
Bot: [shows CI/CD status]

You: Create an issue in my-project about the login bug
Bot: [creates the issue and returns the link]

You: What's the recent activity on my-project?
Bot: [shows recent commits]

You: Search my repos for "trading"
Bot: [shows matching repositories]
```

## Directory Structure

```
openclaw-github-skill/
鈹溾攢鈹€ SKILL.md       # Skill documentation for OpenClaw
鈹溾攢鈹€ README.md      # This file
鈹溾攢鈹€ index.js       # Skill implementation
鈹斺攢鈹€ package.json   # NPM package metadata
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `list_repos` | List repositories (filter by type, language, sort) |
| `get_repo` | Get detailed repo info (stars, forks, etc.) |
| `check_ci_status` | CI/CD status |
| `create_issue` | Create a new issue |
| `create_repo` | Create a new repository |
| `search_repos` | Search your repositories |
| `get_recent_activity` | View recent commits |

## Security

鈿狅笍 **IMPORTANT: Protect Your GitHub Token!**

**Do:**
- 鉁?Use environment variables or OpenClaw config
- 鉁?Use minimal required scopes (`repo` or `public_repo`)
- 鉁?Rotate tokens if compromised

**Don't:**
- 鉂?Commit tokens to git
- 鉂?Share tokens in code or public repos
- 鉂?Store tokens in unprotected files

**Best Practices:**
- For local development: Environment variables are acceptable
- For shared machines: Use OpenClaw config or a secrets manager
- For production: Use your platform's credential store

## Rate Limits

- **Unauthenticated requests:** 60/hour
- **Authenticated requests:** 5,000/hour

The skill automatically uses your credentials for authentication.

## Requirements

- OpenClaw 2024+
- Node.js 18+
- GitHub Personal Access Token with appropriate scopes

## Contributing

Contributions welcome! To contribute:

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Acknowledgments

Built for the OpenClaw ecosystem.
