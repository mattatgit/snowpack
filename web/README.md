# 3D viewer

The first viewer is a deliberately small Three.js proof of concept for the real Furanodake terrain.

It supports:

- orbit / zoom / pan;
- terrain, slope and aspect layers;
- adjustable vertical exaggeration;
- GSI source attribution.

## Generate data

After building the terrain rasters:

```bash
python -m pipeline.terrain.export_web
```

This writes a 20 m browser grid to `web/data/`:

```text
terrain-meta.json
elevation.bin
slope.bin
aspect.bin
```

The generated data directory is not committed to Git.

## Run locally

Browsers should load the binary terrain via HTTP rather than `file://`.

From the repository root:

```bash
python -m http.server 8000
```

Then open:

`http://localhost:8000/web/`

The full terrain processing grid remains 5 m. The 20 m web grid is only a rendering representation and must not be fed back into the snow model.
