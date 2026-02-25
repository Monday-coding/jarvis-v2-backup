# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Search Engines

### DuckDuckGo (ddgr)
- **Tool:** `ddgr` - CLI for DuckDuckGo search
- **Version:** 2.2
- **Usage:** `ddgr -x -n <results> <query>`
- **Options:**
  - `-x`: exit after displaying results
  - `-n <number>`: show specific number of results (default 10)
  - `--news`: search news only
  - `--lite`: use lite version

### Brave Search
- **Note:** Requires API key, currently not configured
- **Config location:** `openclaw configure --section web`

## Other Tools

- **Camera names and locations**
- **SSH hosts and aliases**
- **Preferred voices for TTS**
- **Speaker/room names**
- **Device nicknames**
- **Anything environment-specific**

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
