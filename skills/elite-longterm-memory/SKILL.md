---
name: elite-longterm-memory
version: 1.2.3
description: "Ultimate AI agent memory system for Cursor, Claude, ChatGPT & Copilot. WAL protocol + vector search + git-notes + cloud backup. Never lose context again. Vibe-coding ready."
author: NextFrontierBuilds
keywords: [memory, ai-agent, ai-coding, long-term-memory, vector-search, lancedb, git-notes, wal, persistent-context, claude, claude-code, gpt, chatgpt, cursor, copilot, github-copilot, openclaw, moltbot, vibe-coding, agentic, ai-tools, developer-tools, devtools, typescript, llm, automation]
metadata:
  openclaw:
    emoji: "馃"
    requires:
      env:
        - OPENAI_API_KEY
      plugins:
        - memory-lancedb
---

# Elite Longterm Memory 馃

**The ultimate memory system for AI agents.** Combines 6 proven approaches into one bulletproof architecture.

Never lose context. Never forget decisions. Never repeat mistakes.

## Architecture Overview

```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?                   ELITE LONGTERM MEMORY                        鈹?鈹溾攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?                                                                鈹?鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?            鈹?鈹? 鈹?  HOT RAM   鈹? 鈹? WARM STORE 鈹? 鈹? COLD STORE 鈹?            鈹?鈹? 鈹?            鈹? 鈹?            鈹? 鈹?            鈹?            鈹?鈹? 鈹?SESSION-    鈹? 鈹? LanceDB    鈹? 鈹? Git-Notes  鈹?            鈹?鈹? 鈹?STATE.md    鈹? 鈹? Vectors    鈹? 鈹? Knowledge  鈹?            鈹?鈹? 鈹?            鈹? 鈹?            鈹? 鈹? Graph      鈹?            鈹?鈹? 鈹?(survives   鈹? 鈹?(semantic   鈹? 鈹?(permanent  鈹?            鈹?鈹? 鈹? compaction)鈹? 鈹? search)    鈹? 鈹? decisions) 鈹?            鈹?鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?            鈹?鈹?        鈹?               鈹?               鈹?                    鈹?鈹?        鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                    鈹?鈹?                         鈻?                                     鈹?鈹?                 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                               鈹?鈹?                 鈹? MEMORY.md  鈹? 鈫?Curated long-term           鈹?鈹?                 鈹? + daily/   鈹?   (human-readable)            鈹?鈹?                 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                               鈹?鈹?                         鈹?                                     鈹?鈹?                         鈻?                                     鈹?鈹?                 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                               鈹?鈹?                 鈹?SuperMemory 鈹? 鈫?Cloud backup (optional)     鈹?鈹?                 鈹?   API      鈹?                               鈹?鈹?                 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                               鈹?鈹?                                                                鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

## The 5 Memory Layers

### Layer 1: HOT RAM (SESSION-STATE.md)
**From: bulletproof-memory**

Active working memory that survives compaction. Write-Ahead Log protocol.

```markdown
# SESSION-STATE.md 鈥?Active Working Memory

## Current Task
[What we're working on RIGHT NOW]

## Key Context
- User preference: ...
- Decision made: ...
- Blocker: ...

## Pending Actions
- [ ] ...
```

**Rule:** Write BEFORE responding. Triggered by user input, not agent memory.

### Layer 2: WARM STORE (LanceDB Vectors)
**From: lancedb-memory**

Semantic search across all memories. Auto-recall injects relevant context.

```bash
# Auto-recall (happens automatically)
memory_recall query="project status" limit=5

# Manual store
memory_store text="User prefers dark mode" category="preference" importance=0.9
```

### Layer 3: COLD STORE (Git-Notes Knowledge Graph)
**From: git-notes-memory**

Structured decisions, learnings, and context. Branch-aware.

```bash
# Store a decision (SILENT - never announce)
python3 memory.py -p $DIR remember '{"type":"decision","content":"Use React for frontend"}' -t tech -i h

# Retrieve context
python3 memory.py -p $DIR get "frontend"
```

### Layer 4: CURATED ARCHIVE (MEMORY.md + daily/)
**From: OpenClaw native**

Human-readable long-term memory. Daily logs + distilled wisdom.

```
workspace/
鈹溾攢鈹€ MEMORY.md              # Curated long-term (the good stuff)
鈹斺攢鈹€ memory/
    鈹溾攢鈹€ 2026-01-30.md      # Daily log
    鈹溾攢鈹€ 2026-01-29.md
    鈹斺攢鈹€ topics/            # Topic-specific files
```

### Layer 5: CLOUD BACKUP (SuperMemory) 鈥?Optional
**From: supermemory**

Cross-device sync. Chat with your knowledge base.

```bash
export SUPERMEMORY_API_KEY="your-key"
supermemory add "Important context"
supermemory search "what did we decide about..."
```

### Layer 6: AUTO-EXTRACTION (Mem0) 鈥?Recommended
**NEW: Automatic fact extraction**

Mem0 automatically extracts facts from conversations. 80% token reduction.

```bash
npm install mem0ai
export MEM0_API_KEY="your-key"
```

```javascript
const { MemoryClient } = require('mem0ai');
const client = new MemoryClient({ apiKey: process.env.MEM0_API_KEY });

// Conversations auto-extract facts
await client.add(messages, { user_id: "user123" });

// Retrieve relevant memories
const memories = await client.search(query, { user_id: "user123" });
```

Benefits:
- Auto-extracts preferences, decisions, facts
- Deduplicates and updates existing memories
- 80% reduction in tokens vs raw history
- Works across sessions automatically

## Quick Setup

### 1. Create SESSION-STATE.md (Hot RAM)

```bash
cat > SESSION-STATE.md << 'EOF'
# SESSION-STATE.md 鈥?Active Working Memory

This file is the agent's "RAM" 鈥?survives compaction, restarts, distractions.

## Current Task
[None]

## Key Context
[None yet]

## Pending Actions
- [ ] None

## Recent Decisions
[None yet]

---
*Last updated: [timestamp]*
EOF
```

### 2. Enable LanceDB (Warm Store)

In `~/.openclaw/openclaw.json`:

```json
{
  "memorySearch": {
    "enabled": true,
    "provider": "openai",
    "sources": ["memory"],
    "minScore": 0.3,
    "maxResults": 10
  },
  "plugins": {
    "entries": {
      "memory-lancedb": {
        "enabled": true,
        "config": {
          "autoCapture": false,
          "autoRecall": true,
          "captureCategories": ["preference", "decision", "fact"],
          "minImportance": 0.7
        }
      }
    }
  }
}
```

### 3. Initialize Git-Notes (Cold Store)

```bash
cd ~/clawd
git init  # if not already
python3 skills/git-notes-memory/memory.py -p . sync --start
```

### 4. Verify MEMORY.md Structure

```bash
# Ensure you have:
# - MEMORY.md in workspace root
# - memory/ folder for daily logs
mkdir -p memory
```

### 5. (Optional) Setup SuperMemory

```bash
export SUPERMEMORY_API_KEY="your-key"
# Add to ~/.zshrc for persistence
```

## Agent Instructions

### On Session Start
1. Read SESSION-STATE.md 鈥?this is your hot context
2. Run `memory_search` for relevant prior context
3. Check memory/YYYY-MM-DD.md for recent activity

### During Conversation
1. **User gives concrete detail?** 鈫?Write to SESSION-STATE.md BEFORE responding
2. **Important decision made?** 鈫?Store in Git-Notes (SILENTLY)
3. **Preference expressed?** 鈫?`memory_store` with importance=0.9

### On Session End
1. Update SESSION-STATE.md with final state
2. Move significant items to MEMORY.md if worth keeping long-term
3. Create/update daily log in memory/YYYY-MM-DD.md

### Memory Hygiene (Weekly)
1. Review SESSION-STATE.md 鈥?archive completed tasks
2. Check LanceDB for junk: `memory_recall query="*" limit=50`
3. Clear irrelevant vectors: `memory_forget id=<id>`
4. Consolidate daily logs into MEMORY.md

## The WAL Protocol (Critical)

**Write-Ahead Log:** Write state BEFORE responding, not after.

| Trigger | Action |
|---------|--------|
| User states preference | Write to SESSION-STATE.md 鈫?then respond |
| User makes decision | Write to SESSION-STATE.md 鈫?then respond |
| User gives deadline | Write to SESSION-STATE.md 鈫?then respond |
| User corrects you | Write to SESSION-STATE.md 鈫?then respond |

**Why?** If you respond first and crash/compact before saving, context is lost. WAL ensures durability.

## Example Workflow

```
User: "Let's use Tailwind for this project, not vanilla CSS"

Agent (internal):
1. Write to SESSION-STATE.md: "Decision: Use Tailwind, not vanilla CSS"
2. Store in Git-Notes: decision about CSS framework
3. memory_store: "User prefers Tailwind over vanilla CSS" importance=0.9
4. THEN respond: "Got it 鈥?Tailwind it is..."
```

## Maintenance Commands

```bash
# Audit vector memory
memory_recall query="*" limit=50

# Clear all vectors (nuclear option)
rm -rf ~/.openclaw/memory/lancedb/
openclaw gateway restart

# Export Git-Notes
python3 memory.py -p . export --format json > memories.json

# Check memory health
du -sh ~/.openclaw/memory/
wc -l MEMORY.md
ls -la memory/
```

## Why Memory Fails

Understanding the root causes helps you fix them:

| Failure Mode | Cause | Fix |
|--------------|-------|-----|
| Forgets everything | `memory_search` disabled | Enable + add OpenAI key |
| Files not loaded | Agent skips reading memory | Add to AGENTS.md rules |
| Facts not captured | No auto-extraction | Use Mem0 or manual logging |
| Sub-agents isolated | Don't inherit context | Pass context in task prompt |
| Repeats mistakes | Lessons not logged | Write to memory/lessons.md |

## Solutions (Ranked by Effort)

### 1. Quick Win: Enable memory_search

If you have an OpenAI key, enable semantic search:

```bash
openclaw configure --section web
```

This enables vector search over MEMORY.md + memory/*.md files.

### 2. Recommended: Mem0 Integration

Auto-extract facts from conversations. 80% token reduction.

```bash
npm install mem0ai
```

```javascript
const { MemoryClient } = require('mem0ai');

const client = new MemoryClient({ apiKey: process.env.MEM0_API_KEY });

// Auto-extract and store
await client.add([
  { role: "user", content: "I prefer Tailwind over vanilla CSS" }
], { user_id: "ty" });

// Retrieve relevant memories
const memories = await client.search("CSS preferences", { user_id: "ty" });
```

### 3. Better File Structure (No Dependencies)

```
memory/
鈹溾攢鈹€ projects/
鈹?  鈹溾攢鈹€ strykr.md
鈹?  鈹斺攢鈹€ taska.md
鈹溾攢鈹€ people/
鈹?  鈹斺攢鈹€ contacts.md
鈹溾攢鈹€ decisions/
鈹?  鈹斺攢鈹€ 2026-01.md
鈹溾攢鈹€ lessons/
鈹?  鈹斺攢鈹€ mistakes.md
鈹斺攢鈹€ preferences.md
```

Keep MEMORY.md as a summary (<5KB), link to detailed files.

## Immediate Fixes Checklist

| Problem | Fix |
|---------|-----|
| Forgets preferences | Add `## Preferences` section to MEMORY.md |
| Repeats mistakes | Log every mistake to `memory/lessons.md` |
| Sub-agents lack context | Include key context in spawn task prompt |
| Forgets recent work | Strict daily file discipline |
| Memory search not working | Check `OPENAI_API_KEY` is set |

## Troubleshooting

**Agent keeps forgetting mid-conversation:**
鈫?SESSION-STATE.md not being updated. Check WAL protocol.

**Irrelevant memories injected:**
鈫?Disable autoCapture, increase minImportance threshold.

**Memory too large, slow recall:**
鈫?Run hygiene: clear old vectors, archive daily logs.

**Git-Notes not persisting:**
鈫?Run `git notes push` to sync with remote.

**memory_search returns nothing:**
鈫?Check OpenAI API key: `echo $OPENAI_API_KEY`
鈫?Verify memorySearch enabled in openclaw.json

---

## Links

- bulletproof-memory: https://clawdhub.com/skills/bulletproof-memory
- lancedb-memory: https://clawdhub.com/skills/lancedb-memory
- git-notes-memory: https://clawdhub.com/skills/git-notes-memory
- memory-hygiene: https://clawdhub.com/skills/memory-hygiene
- supermemory: https://clawdhub.com/skills/supermemory

---

*Built by [@NextXFrontier](https://x.com/NextXFrontier) 鈥?Part of the Next Frontier AI toolkit*
