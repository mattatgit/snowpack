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
        "const BUILD_ID='snow-heatmap-5m-20261010-14';",
        "const BUILD_ID='snow-heatmap-5m-20261010-15';",
        "build id",
    )

    text = replace_once(
        text,
        '<label class="row"><span>Trees</span><input id="treesToggle" type="checkbox" checked></label>',
        '<label class="row"><span>Trees</span><input id="treesToggle" type="checkbox"></label>',
        "trees default off",
    )

    text = replace_once(
        text,
        "setOverlay(norm,1,2);windLines.visible=true;updateWindFieldSlices(speed.A,speed.B,direction.A,direction.B,speed.f,speed.a,speed.b);",
        "overlayMesh.visible=false;for(const mesh of lodTiles.values())if(mesh.userData.overlay)mesh.userData.overlay.visible=false;updateEarthBlockColors('terrain');windLines.visible=true;updateWindFieldSlices(speed.A,speed.B,direction.A,direction.B,speed.f,speed.a,speed.b);",
        "terrain surface under wind animation",
    )

    text = replace_once(
        text,
        "Object.entries(legends).forEach(([name,node])=>node.classList.toggle('visible',name===layer));",
        "Object.entries(legends).forEach(([name,node])=>node.classList.toggle('visible',name===layer&&layer!=='wind'));",
        "hide obsolete wind heatmap legend",
    )

    path.write_text(text, encoding="utf-8")
    print("Kept terrain surface under wind animation and set trees default off")


if __name__ == "__main__":
    run()
