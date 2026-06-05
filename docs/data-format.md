# Data Format

The viewer loads JSON data from `public/viewer-data/` and radar images from `public/maps/`.

## Directory Structure

```
public/
├── viewer-data/
│   ├── index.json                          # List of available demos
│   ├── {demo-stem}/
│   │   ├── meta.json                       # Demo metadata
│   │   ├── round_01.json                   # Per-round frame data
│   │   ├── round_02.json
│   │   ├── ...
│   │   └── commentary.json                 # Optional caster-commentary track (dormant)
│   └── {another-demo}/
│       └── ...
└── maps/
    ├── map-data.json                       # Coordinate transforms
    ├── de_mirage.png                       # Radar images (upper level)
    ├── de_mirage_lower.png                 # Radar images (lower level)
    └── ...
```

## index.json

Array of demo entries. Used by the demo selector dropdown.

```json
[
  {
    "stem": "furia-vs-vitality-m1-mirage",
    "map_name": "de_mirage",
    "rounds": 25
  }
]
```

## meta.json

Per-demo metadata including round info, kills, damages, shots, and bomb events.

```json
{
  "stem": "furia-vs-vitality-m1-mirage",
  "map_name": "de_mirage",
  "header": {
    "map_name": "de_mirage",
    "server_name": "...",
    "tickrate": 64
  },
  "rounds": [
    {
      "round_num": 1,
      "start": 1234,
      "end": 5678,
      "freeze_end": 2000,
      "winner": "ct",
      "reason": "ct_killed",
      "bomb_plant": null,
      "bomb_site": "not_planted"
    }
  ],
  "kills": [
    {
      "tick": 3456,
      "round_num": 1,
      "attacker_name": "ZywOo",
      "attacker_side": "ct",
      "attacker_X": -1200.5,
      "attacker_Y": 300.2,
      "attacker_Z": -100.0,
      "victim_name": "KSCERATO",
      "victim_side": "t",
      "victim_X": -900.0,
      "victim_Y": 400.1,
      "victim_Z": -100.0,
      "weapon": "ak47",
      "headshot": true
    }
  ],
  "damages": [
    {
      "tick": 3450,
      "round_num": 1,
      "attacker_name": "ZywOo",
      "attacker_side": "ct",
      "attacker_X": -1200.5,
      "attacker_Y": 300.2,
      "attacker_Z": -100.0,
      "victim_name": "KSCERATO",
      "victim_side": "t",
      "victim_X": -900.0,
      "victim_Y": 400.1,
      "victim_Z": -100.0,
      "weapon": "ak47",
      "dmg_health": 111,
      "dmg_health_real": 100,
      "hitgroup": 1
    }
  ],
  "shots": [
    {
      "tick": 3449,
      "round_num": 1,
      "player_name": "ZywOo",
      "player_side": "ct",
      "player_X": -1200.5,
      "player_Y": 300.2,
      "player_Z": -100.0,
      "weapon": "ak47",
      "yaw": 45.3
    }
  ],
  "bomb": [
    {
      "tick": 4000,
      "round_num": 2,
      "event": "plant",
      "player_name": "KSCERATO",
      "site": "A"
    }
  ]
}
```

## round_XX.json

Per-round frame data with downsampled player positions at each tick.

```json
{
  "round_num": 1,
  "start_tick": 1234,
  "end_tick": 5678,
  "freeze_end": 2000,
  "winner": "ct",
  "reason": "ct_killed",
  "bomb_plant_tick": null,
  "bomb_site": null,
  "frames": [
    {
      "tick": 2000,
      "players": [
        {
          "name": "ZywOo",
          "side": "CT",
          "x": -1200.5,
          "y": 300.2,
          "z": -100.0,
          "yaw": 45.3,
          "hp": 100,
          "alive": true
        },
        {
          "name": "KSCERATO",
          "side": "T",
          "x": -900.0,
          "y": 400.1,
          "z": -100.0,
          "yaw": 180.0,
          "hp": 100,
          "alive": true
        }
      ]
    }
  ]
}
```

Per-player frame fields (`PlayerFrame`): `name`, `side` (`"CT"`/`"T"`), `x`, `y`, `z`, `hp`, `alive`, and optional `yaw`.

### Extending PlayerFrame for rollout visualization (planned)

To overlay world-model rollouts, a `PlayerFrame` can carry **optional** predicted-position fields alongside the real (ground-truth) ones:

```json
{
  "name": "ZywOo",
  "side": "CT",
  "x": -1200.5,        // actual position (ground truth from the demo)
  "y": 300.2,
  "z": -100.0,
  "predicted_x": -1180.0,   // optional: world-model prediction for this tick
  "predicted_y": 312.0,     // optional
  "hp": 100,
  "alive": true
}
```

When `predicted_x` / `predicted_y` are present the renderer can draw a ghost dot at the predicted location next to the real dot; when absent (every normal demo) nothing changes. These fields do **not** exist in current exports — they are the proposed extension for the rollout-viz direction, not a shipped schema.

## commentary.json (optional, dormant)

A caster-commentary track for a demo, synced to the timeline. Belongs to the parked language phase — most demos won't have one; the viewer renders fine without it. The bundled `sample-match` (Spirit vs Falcons, dust2) has a real aligned track.

```json
{
  "_meta": {
    "source_vod": "TQwIfQqwP_M",
    "source": "StarLadder Major Budapest 2025 — spirit-vs-falcons-m2-dust2 auto-captions",
    "alignment": "REAL: kills↔name-mentions cross-correlation. offset=10274s, confidence=4.6sigma, 46/187 (25%) kills anchored. Tick ranges are absolute demo ticks.",
    "n_lines": 128
  },
  "lines": [
    {
      "round_num": 1,
      "tick_start": 816,
      "tick_end": 2736,
      "bucket": "offtopic",
      "specific_hits": [],
      "structurally_flat": true,
      "text": "..."
    }
  ]
}
```

- `_meta` (optional): provenance. Only `source` and `alignment` are read by the UI; `source_vod` / `n_lines` are informational. The `alignment` string records that timing came from a real kills↔name-mentions cross-correlation (global offset solid at 4.6σ; per-line timing good to a few seconds, limited by ~25% ASR name recall — not frame-exact).
- `lines[]`: each entry has `round_num`, absolute `tick_start` / `tick_end`, a `bucket` (`tactical` | `vague` | `offtopic` | `silence`), `text`, and optional `specific_hits` (string tags) and `t_vod` (seconds into the source VOD). `structurally_flat` may also appear in the data; it is not consumed by the viewer.

## maps/

### Radar images

PNG files named `{map_name}.png` (upper level) and `{map_name}_lower.png` (lower level, e.g. for de_nuke). Source: [awpy](https://github.com/pnxenopoulos/awpy) map data.

### map-data.json

Coordinate transformation metadata for converting game coordinates (X, Y) to radar pixel coordinates. Keyed by map name. Sourced from [awpy](https://github.com/pnxenopoulos/awpy)'s `MAP_DATA`.

```json
{
  "de_mirage": {
    "pos_x": -3230,
    "pos_y": 1713,
    "scale": 5.0,
    "lower_level_max_units": -1000000.0
  },
  "de_nuke": {
    "pos_x": -3453,
    "pos_y": 2887,
    "scale": 7.0,
    "lower_level_max_units": -495.0
  }
}
```

| Field | Meaning |
|-------|---------|
| `pos_x`, `pos_y` | Game-coordinate origin of the radar image (top-left). |
| `scale` | Game units per radar pixel. |
| `lower_level_max_units` | Z threshold for the lower-level radar image. A player with `z < lower_level_max_units` is drawn on `{map}_lower.png`. Single-level maps use a sentinel `-1000000.0` (nothing is ever below it). |

**Coordinate conversion:**

```
pixel_x = (game_x - pos_x) / scale
pixel_y = (pos_y - game_y) / scale
```

For multi-level maps (e.g. de_nuke, de_train), a player or event is rendered on the lower radar image when its `z < lower_level_max_units`; the viewer treats any map with `lower_level_max_units > -999999` as having a lower level.

## Generating data

Use [cs2-tools](https://github.com/skkwowee/cs2-tools) to generate viewer data from CS2 demo files:

```bash
# Parse .dem files into Parquet + metadata JSONs
cs2-parse-demos data/demos/ --output data/processed/demos

# Export viewer-ready JSON
cs2-export-viewer --input data/processed/demos --output public/viewer-data --maps-output public/maps
```
