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

    marker = (
        "const fineOverlayMaterial=overlayMaterial.clone();"
        "fineOverlayMaterial.uniforms.coverageMap.value=coverageTexture;"
        "fineOverlayMaterial.uniforms.maskFine.value=0;"
    )
    snow_material = marker + "\n" + (
        "  const snowSurfaceMaterial=new THREE.ShaderMaterial({transparent:false,depthWrite:true,depthTest:true,side:THREE.DoubleSide,toneMapped:false,uniforms:{dataMap:{value:null}},"
        "vertexShader:`varying vec2 vUv; varying float vShade; void main(){vUv=uv;vec3 n=normalize(normalMatrix*normal);vec3 lightDir=normalize(vec3(-.45,.82,.35));vShade=.76+.24*max(dot(n,lightDir),0.0);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,"
        "fragmentShader:`uniform sampler2D dataMap; varying vec2 vUv; varying float vShade;"
        "vec3 snowPalette(float x){vec3 c0=vec3(.04,.08,.28),c1=vec3(.03,.25,.90),c2=vec3(.02,.78,.92),c3=vec3(.10,.72,.32),c4=vec3(.94,.84,.08),c5=vec3(.96,.43,.06),c6=vec3(.86,.06,.06);"
        "if(x<.17)return mix(c0,c1,x/.17);if(x<.34)return mix(c1,c2,(x-.17)/.17);if(x<.51)return mix(c2,c3,(x-.34)/.17);if(x<.68)return mix(c3,c4,(x-.51)/.17);if(x<.84)return mix(c4,c5,(x-.68)/.16);return mix(c5,c6,(x-.84)/.16);}"
        "void main(){float x=texture2D(dataMap,vUv).r;vec3 c=snowPalette(x)*vShade;gl_FragColor=vec4(c,1.0);}`});\n"
        "  function setSnowSurface(enabled){terrainMesh.material=enabled?snowSurfaceMaterial:terrainMaterial;for(const mesh of lodTiles.values()){mesh.material=enabled?snowSurfaceMaterial:fineTerrainMaterial;if(mesh.userData.overlay)mesh.userData.overlay.visible=!enabled&&overlayMesh.visible;}}"
    )
    text = replace_once(text, marker, snow_material, "opaque snow terrain material")

    text = replace_once(
        text,
        "const geometry=makeTerrainGeometry(data,tile.width,tile.height,tile.x0_m,tile.z0_m,tile.x1_m,tile.z1_m,tile.u0,tile.v0,tile.u1,tile.v1),mesh=new THREE.Mesh(geometry,fineTerrainMaterial);mesh.position.y=.35;",
        "const geometry=makeTerrainGeometry(data,tile.width,tile.height,tile.x0_m,tile.z0_m,tile.x1_m,tile.z1_m,tile.u0,tile.v0,tile.u1,tile.v1),mesh=new THREE.Mesh(geometry,layerSelect.value==='snow'?snowSurfaceMaterial:fineTerrainMaterial);mesh.position.y=.35;",
        "snow material for newly streamed terrain tiles",
    )

    old_set_overlay = (
        "overlayMaterial.uniforms.dataMap.value=overlayTexture;overlayMaterial.uniforms.mode.value=mode;"
        "fineOverlayMaterial.uniforms.dataMap.value=overlayTexture;fineOverlayMaterial.uniforms.mode.value=mode;"
        "overlayMesh.visible=true;for(const mesh of lodTiles.values())if(mesh.userData.overlay)mesh.userData.overlay.visible=true;"
        "updateEarthBlockColors(layerSelect.value,values,maxValue,mode);"
    )
    new_set_overlay = (
        "if(mode<.5){snowSurfaceMaterial.uniforms.dataMap.value=overlayTexture;overlayMesh.visible=false;setSnowSurface(true);for(const mesh of lodTiles.values())if(mesh.userData.overlay)mesh.userData.overlay.visible=false;}"
        "else{setSnowSurface(false);overlayMaterial.uniforms.dataMap.value=overlayTexture;overlayMaterial.uniforms.mode.value=mode;fineOverlayMaterial.uniforms.dataMap.value=overlayTexture;fineOverlayMaterial.uniforms.mode.value=mode;overlayMesh.visible=true;for(const mesh of lodTiles.values())if(mesh.userData.overlay)mesh.userData.overlay.visible=true;}"
        "updateEarthBlockColors(layerSelect.value,values,maxValue,mode);"
    )
    text = replace_once(text, old_set_overlay, new_set_overlay, "snow uses terrain material instead of overlay")

    text = replace_once(
        text,
        "overlayMesh.visible=false;for(const mesh of lodTiles.values())if(mesh.userData.overlay)mesh.userData.overlay.visible=false;updateEarthBlockColors('terrain');windLines.visible=true;",
        "setSnowSurface(false);overlayMesh.visible=false;for(const mesh of lodTiles.values())if(mesh.userData.overlay)mesh.userData.overlay.visible=false;updateEarthBlockColors('terrain');windLines.visible=true;",
        "restore terrain material for wind",
    )

    text = replace_once(
        text,
        "if(!isDynamic){overlayMesh.visible=false;for(const mesh of lodTiles.values())if(mesh.userData.overlay)mesh.userData.overlay.visible=false;updateEarthBlockColors('terrain');",
        "if(!isDynamic){setSnowSurface(false);overlayMesh.visible=false;for(const mesh of lodTiles.values())if(mesh.userData.overlay)mesh.userData.overlay.visible=false;updateEarthBlockColors('terrain');",
        "restore terrain material for static layer",
    )

    path.write_text(text, encoding="utf-8")
    print("Rendered snow directly on coarse and streamed terrain meshes with an opaque snow surface material")


if __name__ == "__main__":
    run()
