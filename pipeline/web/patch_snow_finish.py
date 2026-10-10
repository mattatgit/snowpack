from __future__ import annotations

from pathlib import Path


HTML_PATH = Path("web/index.html")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise ValueError(f"Could not find viewer fragment for {label}")
    return text.replace(old, new, 1)


def run(path: Path = HTML_PATH) -> None:
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "const BUILD_ID='snow-heatmap-5m-20261010-17';",
        "const BUILD_ID='snow-heatmap-5m-20261010-18';",
        "build id",
    )

    text = replace_once(
        text,
        "float alpha=mode<.5?mix(.30,.96,smoothstep(.015,.24,x)):mix(.18,.72,x);",
        "float alpha=mode<.5?1.0:mix(.18,.72,x);",
        "opaque quantitative snow",
    )

    text = replace_once(
        text,
        "const coverageSize=128,coverageBytes=new Uint8Array(coverageSize*coverageSize*4)",
        "const coverageSize=512,coverageBytes=new Uint8Array(coverageSize*coverageSize*4)",
        "higher resolution LOD coverage mask",
    )

    old_bounds = (
        "const x0=Math.max(0,Math.floor(tile.u0*(coverageSize-1))),"
        "x1=Math.min(coverageSize-1,Math.ceil(tile.u1*(coverageSize-1))),"
        "y0=Math.max(0,Math.floor(tile.v0*(coverageSize-1))),"
        "y1=Math.min(coverageSize-1,Math.ceil(tile.v1*(coverageSize-1)));"
        "for(let y=y0;y<=y1;y++)for(let x=x0;x<=x1;x++){"
    )
    new_bounds = (
        "const x0=Math.max(0,Math.ceil(tile.u0*(coverageSize-1))+1),"
        "x1=Math.min(coverageSize-1,Math.floor(tile.u1*(coverageSize-1))-1),"
        "y0=Math.max(0,Math.ceil(tile.v0*(coverageSize-1))+1),"
        "y1=Math.min(coverageSize-1,Math.floor(tile.v1*(coverageSize-1))-1);"
        "if(x1<x0||y1<y0)continue;"
        "for(let y=y0;y<=y1;y++)for(let x=x0;x<=x1;x++){"
    )
    text = replace_once(text, old_bounds, new_bounds, "overlapping coarse/fine snow mask")

    path.write_text(text, encoding="utf-8")
    print("Made visible snow opaque and overlapped coarse/fine LOD snow coverage to hide tile seams")


if __name__ == "__main__":
    run()
