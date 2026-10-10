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
        "const BUILD_ID='snow-heatmap-5m-20261009-7';",
        "const BUILD_ID='snow-heatmap-5m-20261009-8';",
        "build id",
    )

    text = replace_once(
        text,
        "  const [meta,elevation,slope,aspect]=await Promise.all([loadJSON('./data/terrain-meta.json'),loadFloat32('./data/elevation.bin'),loadFloat32('./data/slope.bin'),loadFloat32('./data/aspect.bin')]);\n"
        "  const terrainCount=meta.width*meta.height;\n"
        "  if([elevation.length,slope.length,aspect.length].some(n=>n!==terrainCount))throw new Error('Terrain data size mismatch');",
        "  const [meta,elevation]=await Promise.all([loadJSON('./data/terrain-meta.json'),loadFloat32('./data/elevation.bin')]);\n"
        "  const terrainCount=meta.width*meta.height;\n"
        "  if(elevation.length!==terrainCount)throw new Error('Terrain data size mismatch');",
        "unused slope/aspect loads",
    )

    text = replace_once(
        text,
        "renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight);",
        "const isMobile=matchMedia('(max-width: 760px)').matches||navigator.maxTouchPoints>1;renderer.setPixelRatio(Math.min(devicePixelRatio,isMobile?1.35:2));renderer.setSize(innerWidth,innerHeight);",
        "mobile pixel ratio",
    )

    text = replace_once(
        text,
        "  const overlayGeometry=terrainGeometry.clone();const overlayPos=overlayGeometry.getAttribute('position').array;for(let i=1;i<overlayPos.length;i+=3)overlayPos[i]+=1.2;overlayGeometry.getAttribute('position').needsUpdate=true;\n"
        "  const overlayMaterial=new THREE.ShaderMaterial({transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1,uniforms:{dataMap:{value:null},mode:{value:0}},vertexShader:`varying vec2 vUv; void main(){vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`",
        "  // Share the 5 m terrain buffers for overlays instead of cloning ~30 MB of geometry per pass.\n"
        "  const overlayGeometry=terrainGeometry;\n"
        "  const overlayMaterial=new THREE.ShaderMaterial({transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1,uniforms:{dataMap:{value:null},mode:{value:0}},vertexShader:`varying vec2 vUv; void main(){vUv=uv;vec3 p=position;p.y+=1.2;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);}`",
        "shared snow overlay geometry",
    )

    text = replace_once(
        text,
        "  const contourGeometry=terrainGeometry.clone();\n"
        "  const contourPos=contourGeometry.getAttribute('position').array;\n"
        "  for(let i=1;i<contourPos.length;i+=3)contourPos[i]+=1.6;\n"
        "  contourGeometry.getAttribute('position').needsUpdate=true;\n"
        "  const contourMaterial=new THREE.ShaderMaterial({\n"
        "    transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2,toneMapped:false,\n"
        "    uniforms:{elevationBase:{value:minE}},\n"
        "    vertexShader:`uniform float elevationBase; varying float vElevation; void main(){vElevation=position.y+elevationBase;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`",
        "  const contourGeometry=terrainGeometry;\n"
        "  const contourMaterial=new THREE.ShaderMaterial({\n"
        "    transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2,toneMapped:false,\n"
        "    uniforms:{elevationBase:{value:minE}},\n"
        "    vertexShader:`uniform float elevationBase; varying float vElevation; void main(){vElevation=position.y+elevationBase;vec3 p=position;p.y+=1.6;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);}`",
        "shared contour geometry",
    )

    text = replace_once(
        text,
        "  function updateStaticColors(layer){setGeometryColors(terrainGeometry,terrainCount,i=>layer==='slope'?slopeColor(slope[i]):layer==='aspect'?aspectColor(aspect[i]):terrainColor((elevation[i]-minE)/(maxE-minE)));}",
        "  function updateStaticColors(){setGeometryColors(terrainGeometry,terrainCount,i=>terrainColor((elevation[i]-minE)/(maxE-minE)));}",
        "remove unused static layer data",
    )

    path.write_text(text, encoding="utf-8")
    print("Optimized viewer memory for mobile: shared geometry, fewer terrain rasters, lower mobile pixel ratio")


if __name__ == "__main__":
    run()
