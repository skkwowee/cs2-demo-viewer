# cs2-demo-viewer

Interactive browser-based viewer for Counter-Strike 2 demo replays. Renders player positions on radar maps with vision cones, kill lines, shot tracers, and timeline scrubbing.

Part of the [chimera](https://github.com/skkwowee/chimera) research project. Going forward its primary job is **visualizing world-model rollouts** — overlaying the world model's *predicted* future player positions against the *actual* demo positions on the radar, so we can eyeball how a next-state-prediction rollout drifts over its horizon (125 ms → 2 s). The existing demo-replay rendering is the substrate for that: a predicted position is just a second (ghost) dot per player, a ~10-line addition in `MapCanvas`. See [Visualizing rollouts](#visualizing-rollouts) and the optional predicted-position fields in [docs/data-format.md](docs/data-format.md).

## Features

- Radar canvas with player positions (T amber / CT blue)
- Wall-clipped vision cones via raycasting
- Kill lines and damage lines
- Shot tracers with trajectory visualization
- Multi-level map support (upper/lower for maps like de_nuke)
- Timeline slider with kill event markers
- Demo and round selection
- **Commentary track** (dormant) — a caster-commentary overlay synced to the timeline. Belongs to the parked language phase; it stays in the codebase but is optional (a demo without a `commentary.json` simply renders without it). The bundled Spirit vs Falcons dust2 sample includes a real aligned commentary track.

## Tech Stack

- Next.js 16
- React 19
- Tailwind CSS v4
- HTML Canvas for radar rendering

## Quickstart

```bash
git clone https://github.com/skkwowee/cs2-demo-viewer.git
cd cs2-demo-viewer
npm install
```

Add demo data to `public/viewer-data/` and radar images to `public/maps/` (see [Data Format](#data-format) below), then:

```bash
npm run dev
```

Open http://localhost:3000/viewer.

## Data Format

The viewer expects JSON data in `public/viewer-data/` and radar PNGs in `public/maps/`. See [docs/data-format.md](docs/data-format.md) for the full schema.

**Quick summary:**

```
public/
├── viewer-data/
│   ├── index.json                    # [{stem, map_name, rounds}]
│   └── {demo}/
│       ├── meta.json                 # rounds, kills, damages, shots, bomb events
│       └── round_XX.json             # frames with player positions per tick
└── maps/
    ├── map-data.json                 # coordinate transforms
    ├── de_mirage.png                 # radar images
    └── de_mirage_lower.png
```

### Generating data from .dem files

Use [cs2-tools](https://github.com/skkwowee/cs2-tools):

```bash
pip install cs2-tools[parse]
cs2-parse-demos data/demos/ --output data/processed/demos
cs2-export-viewer --input data/processed/demos --output public/viewer-data --maps-output public/maps
```

## Visualizing rollouts

The intended new use: dump a world-model rollout into the same per-round JSON shape, with the *actual* demo frames as ground truth and the model's *predicted* positions attached to each player. The renderer draws the real dot and a ghost dot for the prediction, so drift over the rollout horizon is visible directly on the radar.

This only needs optional `predicted_x` / `predicted_y` fields on the existing `PlayerFrame` (no schema change for normal demos — fields absent = no ghost dot) plus a few lines in `MapCanvas` to draw the ghost. The optional fields are described in [docs/data-format.md](docs/data-format.md). No rollout exporter exists yet — this is the planned direction, not a shipped feature.

## License

MIT
