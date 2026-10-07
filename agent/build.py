"""Build the Groundwork agent package.

Inlines instructions.md into declarativeAgent.json, checks Copilot's limits,
and zips appPackage/ into dist/groundwork-agent.zip for upload.

    python3 agent/build.py
"""
import json
import pathlib
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent
PKG = ROOT / "appPackage"
DIST = ROOT / "dist"

INSTRUCTION_LIMIT = 8000
STARTER_LIMIT = 6

STARTERS = [
    ("Turn an ask into a brief", "I've been asked to do something. Help me turn it into a one-page brief. Here's exactly what they said:"),
    ("Prep me for a meeting", "I'm meeting [person] about [topic]. Summarise what's been said about this in the last two weeks and list open decisions."),
    ("Debrief a meeting", "Here's the recap from my meeting. List decisions, every term used and what it means here, my actions, and disagreements with who raised them:"),
    ("Decode team terms", "Explain these terms as they're used in my team's docs and chats:"),
    ("Run my Friday review", "Run my Friday review. Ask me the three questions one at a time."),
    ("Draft my Connects wins", "Draft my wins from the last month for Connects: what moved, my part, and evidence links."),
]


def main() -> int:
    instructions = (ROOT / "instructions.md").read_text(encoding="utf-8").strip()
    if len(instructions) > INSTRUCTION_LIMIT:
        print(f"instructions.md is {len(instructions)} characters; Copilot allows {INSTRUCTION_LIMIT}.")
        return 1
    if len(STARTERS) > STARTER_LIMIT:
        print(f"{len(STARTERS)} conversation starters; keep to {STARTER_LIMIT}.")
        return 1

    agent = {
        "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.0/schema.json",
        "version": "v1.0",
        "name": "Groundwork",
        "description": "Ramp-up coach for new PMs: briefs, meeting debriefs, team terms, 1:1 prep, Friday reviews and Connects wins.",
        "instructions": instructions,
        "capabilities": [{"name": "OneDriveAndSharePoint"}],
        "conversation_starters": [{"title": t, "text": x} for t, x in STARTERS],
    }
    (PKG / "declarativeAgent.json").write_text(json.dumps(agent, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manifest = json.loads((PKG / "manifest.json").read_text(encoding="utf-8"))
    for icon in manifest["icons"].values():
        if not (PKG / icon).exists():
            print(f"Missing icon: {icon}")
            return 1

    DIST.mkdir(exist_ok=True)
    out = DIST / "groundwork-agent.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ["manifest.json", "declarativeAgent.json", *manifest["icons"].values()]:
            z.write(PKG / name, name)
    print(f"Built {out.relative_to(ROOT.parent)} ({len(instructions)} instruction characters, {len(STARTERS)} starters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
