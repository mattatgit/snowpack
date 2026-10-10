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
        "const BUILD_ID='snow-heatmap-5m-20261010-12';",
        "const BUILD_ID='snow-heatmap-5m-20261010-13';",
        "build id",
    )

    old_terrain = (
        "  const terrainGeometry=makeTerrainGeometry(coarseElevation,lodMeta.coarse.width,lodMeta.coarse.height,-widthM*.5,-heightM*.5,widthM*.5,heightM*.5);\n"
        "  const terrainMesh=new THREE.Mesh(terrainGeometry,terrainMaterial);scene.add(terrainMesh);\n"
        "  const lodGroup=new THREE.Group();lodGroup.scale.y=Number(exaggeration.value);scene.add(lodGroup);"
    )

    new_terrain = (
        "  const terrainGeometry=makeTerrainGeometry(coarseElevation,lodMeta.coarse.width,lodMeta.coarse.height,-widthM*.5,-heightM*.5,widthM*.5,heightM*.5);\n"
        "  const terrainMesh=new THREE.Mesh(terrainGeometry,terrainMaterial);scene.add(terrainMesh);\n"
        "\n"
        "  // Give the map extent a physical sliced-earth base instead of leaving the DEM as a floating sheet.\n"
        "  function makeEarthBlock(){\n"
        "    const w=lodMeta.coarse.width,h=lodMeta.coarse.height,blockDepth=Math.min(260,Math.max(180,sceneSpan*.055)),bottomY=-blockDepth,positions=[],indices=[];\n"
        "    function addWall(samples){const base=positions.length/3;for(const s of samples){positions.push(s.x,s.y,s.z,s.x,bottomY,s.z);}for(let i=0;i<samples.length-1;i++){const a=base+i*2,b=a+1,c=a+2,d=a+3;indices.push(a,b,c,c,b,d);}}\n"
        "    const north=[],south=[],west=[],east=[];\n"
        "    for(let col=0;col<w;col++){const x=(col/(w-1)-.5)*widthM;north.push({x,y:coarseElevation[col]-minE,z:-heightM*.5});south.push({x,y:coarseElevation[(h-1)*w+col]-minE,z:heightM*.5});}\n"
        "    for(let row=0;row<h;row++){const z=(row/(h-1)-.5)*heightM;west.push({x:-widthM*.5,y:coarseElevation[row*w]-minE,z});east.push({x:widthM*.5,y:coarseElevation[row*w+w-1]-minE,z});}\n"
        "    addWall(north);addWall(south);addWall(west);addWall(east);\n"
        "    const base=positions.length/3;positions.push(-widthM*.5,bottomY,-heightM*.5,widthM*.5,bottomY,-heightM*.5,widthM*.5,bottomY,heightM*.5,-widthM*.5,bottomY,heightM*.5);indices.push(base,base+1,base+2,base,base+2,base+3);\n"
        "    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setIndex(indices);geometry.computeVertexNormals();\n"
        "    const material=new THREE.MeshStandardMaterial({color:0x756f69,roughness:1,metalness:0,side:THREE.DoubleSide});\n"
        "    const mesh=new THREE.Mesh(geometry,material);mesh.renderOrder=-1;return mesh;\n"
        "  }\n"
        "  const earthBlock=makeEarthBlock();earthBlock.scale.y=Number(exaggeration.value);scene.add(earthBlock);\n"
        "  const lodGroup=new THREE.Group();lodGroup.scale.y=Number(exaggeration.value);scene.add(lodGroup);"
    )
    text = replace_once(text, old_terrain, new_terrain, "sliced earth block")

    text = replace_once(
        text,
        "  function updateVertical(){const v=Number(exaggeration.value);terrainMesh.scale.y=v;lodGroup.scale.y=v;overlayMesh.scale.y=v;contourMesh.scale.y=v;if(treeMesh)treeMesh.scale.y=v;verticalValue.textContent=v.toFixed(2).replace(/0+$/,'').replace(/\\.$/,'')+'×';}",
        "  function updateVertical(){const v=Number(exaggeration.value);terrainMesh.scale.y=v;earthBlock.scale.y=v;lodGroup.scale.y=v;overlayMesh.scale.y=v;contourMesh.scale.y=v;if(treeMesh)treeMesh.scale.y=v;verticalValue.textContent=v.toFixed(2).replace(/0+$/,'').replace(/\\.$/,'')+'×';}",
        "earth block vertical scaling",
    )

    path.write_text(text, encoding="utf-8")
    print("Applied matte sliced-earth perimeter walls and solid base")


if __name__ == "__main__":
    run()
