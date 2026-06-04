#!/usr/bin/env python3
"""Generate a playable sample round + a tick-synced commentary track for the
cs2-demo-viewer, so we can SEE caster commentary overlap with ticks.

Inputs:
  - the commentary pilot's window JSONL (real auto-captions from the actual
    Spirit vs Falcons PGL Astana GF), produced by chimera-demo-pipeline
    pipeline/commentary_pilot.py.

Outputs (written into public/viewer-data/sample-match/):
  - round_01.json   : synthetic but playable frames (no awpy/demo locally) so
                      the timeline scrubs.
  - commentary.json : REAL caster lines, their VOD-second timestamps LINEARLY
                      mapped onto the round tick span. This is a DEMONSTRATION
                      alignment (uniform stretch), NOT the anchor-based
                      alignment from the pod step -- flagged in the file meta so
                      nobody mistakes it for ground truth. The point is to show
                      the viewer MECHANIC: lines light up in sync with ticks.

Run:  python3 scripts/gen_sample_commentary.py \
          /home/soone/chimera-demo-pipeline/data/commentary_pilot_k9E4wwLKXE0.jsonl
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "public" / "viewer-data" / "sample-match"

# Round tick layout (64-tick frames). Kept consistent with meta.json's kill@5200.
START_TICK = 2000
FREEZE_END = 2400
END_TICK = 12000
FRAME_STEP = 64
WIN_TICKS = 15.0  # not used directly; windows carry their own span

# A small synthetic dust2 movement so the map actually animates. Coordinates are
# in the same world space the existing meta.json kill uses (~ -2400..1900 X).
PLAYERS = [
    ("Alice", "CT", (-450, -1900), (-520, -1750)),
    ("Bob",   "CT", (-100, -2100), (-260, -1650)),
    ("Carol", "CT", (200, -1500),  (-50, -1500)),
    ("Dan",   "CT", (-900, -1400), (-700, -1550)),
    ("Erin",  "CT", (-300, -1000), (-400, -1500)),
    ("Frank", "T",  (-300, 1800),  (-280, -1500)),
    ("Gina",  "T",  (-700, 1600),  (-650, -1300)),
    ("Hank",  "T",  (100, 1700),   (-100, -1400)),
    ("Ivy",   "T",  (600, 1500),   (300, -1200)),
    ("Jack",  "T",  (-1100, 1400), (-900, -1100)),
]
# (victim, tick) — a few deaths so the round has shape
DEATHS = {"Dave": 5200, "Frank": 6800, "Erin": 8200, "Gina": 9600}


def lerp(a, b, t):
    return a + (b - a) * t


def build_frames():
    frames = []
    n = (END_TICK - START_TICK) // FRAME_STEP
    for i in range(n + 1):
        tick = START_TICK + i * FRAME_STEP
        t = i / n
        players = []
        for name, side, p0, p1 in PLAYERS:
            alive = not (name in DEATHS and tick >= DEATHS[name])
            players.append({
                "name": name, "side": side, "alive": alive,
                "hp": 100 if alive else 0,
                "X": round(lerp(p0[0], p1[0], t), 1),
                "Y": round(lerp(p0[1], p1[1], t), 1),
                "yaw": 0.0,
            })
        frames.append({"tick": tick, "players": players})
    return frames


def pick_span(windows, target_sec=240.0):
    """Pick the contiguous time span (target_sec long) with the most tactical
    windows, so the demo slice is commentary-rich."""
    tac = [w for w in windows if w.get("bucket") == "tactical"]
    if not tac:
        tac = windows
    best_start, best_count = windows[0]["t_start"], -1
    starts = sorted({w["t_start"] for w in windows})
    for s in starts:
        cnt = sum(1 for w in tac if s <= w["t_start"] < s + target_sec)
        if cnt > best_count:
            best_count, best_start = cnt, s
    span = [w for w in windows
            if best_start <= w["t_start"] < best_start + target_sec]
    span.sort(key=lambda w: w["t_start"])
    return span, best_start, best_count


def main():
    jsonl = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "/home/soone/chimera-demo-pipeline/data/commentary_pilot_k9E4wwLKXE0.jsonl")
    windows = []
    for line in jsonl.read_text().splitlines():
        d = json.loads(line)
        if "_meta" in d:
            continue
        windows.append(d)

    span, span_start, ntac = pick_span(windows)
    vod0 = span[0]["t_start"]
    vod1 = span[-1]["t_end"]
    vspan = (vod1 - vod0) or 1.0
    playable = END_TICK - FREEZE_END

    commentary = []
    for w in span:
        f0 = (w["t_start"] - vod0) / vspan
        f1 = (w["t_end"] - vod0) / vspan
        commentary.append({
            "round_num": 1,
            "tick_start": int(FREEZE_END + f0 * playable),
            "tick_end": int(FREEZE_END + f1 * playable),
            "bucket": w["bucket"],
            "specific_hits": w.get("specific_hits", []),
            "t_vod": round(w["t_start"], 1),
            "text": w["text"].strip(),
        })

    OUT.mkdir(parents=True, exist_ok=True)
    round_obj = {
        "round_num": 1, "start_tick": START_TICK, "end_tick": END_TICK,
        "freeze_end": FREEZE_END, "winner": "ct",
        "reason": "ct_win_elimination",
        "bomb_plant_tick": None, "bomb_site": None,
        "frames": build_frames(),
    }
    (OUT / "round_01.json").write_text(json.dumps(round_obj))
    (OUT / "commentary.json").write_text(json.dumps({
        "_meta": {
            "source_vod": "k9E4wwLKXE0",
            "source": "Spirit vs Falcons PGL Astana 2026 GF auto-captions",
            "alignment": "DEMONSTRATION ONLY -- VOD seconds linearly mapped onto "
                         "round ticks (uniform stretch). NOT anchor-based; the "
                         "real alignment (kill/round cross-correlation, "
                         "asymmetric lead/lag) comes from the pod step.",
            "span_vod_sec": [round(vod0, 1), round(vod1, 1)],
            "n_lines": len(commentary),
            "n_tactical_in_span": ntac,
        },
        "lines": commentary,
    }, indent=2))
    print(f"wrote {OUT/'round_01.json'} ({len(round_obj['frames'])} frames)")
    print(f"wrote {OUT/'commentary.json'} ({len(commentary)} lines, "
          f"{ntac} tactical, VOD span {vod0:.0f}-{vod1:.0f}s)")


if __name__ == "__main__":
    main()
