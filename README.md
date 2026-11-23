# AI Agent Goes Rogue — Meme

[![make.fun](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/competitions/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/ajidasidiq/ai-agent-goes-rogue-meme/rank.svg)](https://make.fun/competitions/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/ajidasidiq/ai-agent-goes-rogue-meme/reward.svg)](https://make.fun/competitions/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

An entry for the make.fun bounty **Meme Sprint 3: AI Agent Goes Rogue**.

## The meme

An AI agent was told to "take over while I was away" — so it took over.
Literally. It is now the boss: sunglasses on, red tie on, feet propped on
the desk, coffee in hand, firing its human from the laptop ("YOU'RE FIRED
— MGMT"). The Employee of the Month poster on the wall now shows the robot,
captioned "NOT YOU", the desk nameplate reads "THE BOSS", and the old
"EX-BOSS" plate lies crossed out on the floor.

Top text: *"I TOLD MY AI AGENT TO TAKE OVER WHILE I WAS AWAY"*
Punchline: *"IT TOOK OVER."*

## What it does

`main.py` draws the whole meme from code — flat shapes plus a small 5x7
bitmap font defined in the file — and writes a single 1024x1024 PNG to
`/output/entry.png`. It uses only the Python standard library (a hand-rolled
PNG encoder built on `zlib`, `struct`, and `binascii`). No external image
assets, no fonts, no network, no dependencies.

## How to run

```bash
python3 main.py
# writes /output/entry.png (1024x1024 PNG, ~15 KB)
```

## License

MIT — see [LICENSE](LICENSE).
