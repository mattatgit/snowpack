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
        "const BUILD_ID='snow-heatmap-5m-20261010-15';",
        "const BUILD_ID='snow-heatmap-5m-20261010-16';",
        "build id",
    )

    text = replace_once(
        text,
        "uniforms:{dataMap:{value:null},mode:{value:0}},vertexShader:",
        "uniforms:{dataMap:{value:null},mode:{value:0},coverageMap:{value:null},maskFine:{value:1}},vertexShader:",
        "overlay coverage uniforms",
    )

    text = replace_once(
        text,
        "uniform sampler2D dataMap; uniform float mode; varying vec2 vUv;",
        "uniform sampler2D dataMap; uniform sampler2D coverageMap; uniform float mode; uniform float maskFine; varying vec2 vUv;",
        "overlay fragment coverage uniforms",
    )

    text = replace_once(
        text,
        "    void main(){float x=texture2D(dataMap,vUv).r;if(x<.002)discard;",
        "    void main(){if(maskFine>.5&&texture2D(coverageMap,vUv).r>.5)discard;float x=texture2D(dataMap,vUv).r;if(x<.002)discard;",
        "coarse overlay fine-tile discard",
    )

    text = replace_once(
        text,
        "  const overlayMesh=new THREE.Mesh(overlayGeometry,overlayMaterial);overlayMesh.visible=false;scene.add(overlayMesh);",
        "  const coverageSize=128,coverageBytes=new Uint8Array(coverageSize*coverageSize*4),coverageTexture=new THREE.DataTexture(coverageBytes,coverageSize,coverageSize,THREE.RGBAFormat,THREE.UnsignedByteType);coverageTexture.flipY=false;coverageTexture.minFilter=THREE.NearestFilter;coverageTexture.magFilter=THREE.NearestFilter;coverageTexture.needsUpdate=true;overlayMaterial.uniforms.coverageMap.value=coverageTexture;overlayMaterial.uniforms.maskFine.value=1;const fineOverlayMaterial=overlayMaterial.clone();fineOverlayMaterial.uniforms.coverageMap.value=coverageTexture;fineOverlayMaterial.uniforms.maskFine.value=0;\n"
        "  const overlayMesh=new THREE.Mesh(overlayGeometry,overlayMaterial);overlayMesh.visible=false;scene.add(overlayMesh);\n"
        "  function updateOverlayCoverage(){coverageBytes.fill(0);for(const mesh of lodTiles.values()){const tile=mesh.userData.tile;if(!tile)continue;const x0=Math.max(0,Math.floor(tile.u0*(coverageSize-1))),x1=Math.min(coverageSize-1,Math.ceil(tile.u1*(coverageSize-1))),y0=Math.max(0,Math.floor(tile.v0*(coverageSize-1))),y1=Math.min(coverageSize-1,Math.ceil(tile.v1*(coverageSize-1)));for(let y=y0;y<=y1;y++)for(let x=x0;x<=x1;x++){const p=(y*coverageSize+x)*4;coverageBytes[p]=255;coverageBytes[p+1]=255;coverageBytes[p+2]=255;coverageBytes[p+3]=255;}}coverageTexture.needsUpdate=true;}" ,
        "overlay coverage texture",
    )

    text = replace_once(
        text,
        "const tileOverlay=new THREE.Mesh(geometry,overlayMaterial);",
        "const tileOverlay=new THREE.Mesh(geometry,fineOverlayMaterial);",
        "fine tile overlay material",
    )

    text = replace_once(
        text,
        "lodTiles.set(tile.id,mesh);lodGroup.add(mesh);",
        "lodTiles.set(tile.id,mesh);lodGroup.add(mesh);updateOverlayCoverage();",
        "coverage update after tile load",
    )

    text = replace_once(
        text,
        "lodGroup.remove(mesh);mesh.geometry.dispose();lodTiles.delete(id);}",
        "lodGroup.remove(mesh);mesh.geometry.dispose();lodTiles.delete(id);updateOverlayCoverage();}",
        "coverage update after tile removal",
    )

    text = replace_once(
        text,
        "overlayMaterial.uniforms.dataMap.value=overlayTexture;overlayMaterial.uniforms.mode.value=mode;overlayMesh.visible=true;",
        "overlayMaterial.uniforms.dataMap.value=overlayTexture;overlayMaterial.uniforms.mode.value=mode;fineOverlayMaterial.uniforms.dataMap.value=overlayTexture;fineOverlayMaterial.uniforms.mode.value=mode;overlayMesh.visible=true;",
        "sync fine overlay data texture",
    )

    path.write_text(text, encoding="utf-8")
    print("Masked coarse weather overlay beneath loaded 5 m terrain tiles")


if __name__ == "__main__":
    run()
