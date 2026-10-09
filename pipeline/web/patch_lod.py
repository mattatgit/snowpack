from __future__ import annotations

import re
from pathlib import Path


HTML_PATH = Path("web/index.html")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise ValueError(f"Could not find viewer fragment for {label}")
    return text.replace(old, new, 1)


def regex_once(text: str, pattern: str, replacement: str, label: str) -> str:
    text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f"Could not find unique viewer fragment for {label}: {count}")
    return text


def run(path: Path = HTML_PATH) -> None:
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "const BUILD_ID='snow-heatmap-5m-20261009-10';",
        "const BUILD_ID='snow-heatmap-5m-20261009-11';",
        "build id",
    )

    text = replace_once(
        text,
        "  const [meta,elevation]=await Promise.all([loadJSON('./data/terrain-meta.json'),loadFloat32('./data/elevation.bin')]);\n"
        "  const terrainCount=meta.width*meta.height;\n"
        "  if(elevation.length!==terrainCount)throw new Error('Terrain data size mismatch');\n"
        "  const widthM=meta.east_m-meta.west_m,heightM=meta.north_m-meta.south_m,centreX=(meta.east_m+meta.west_m)/2,centreY=(meta.north_m+meta.south_m)/2;",
        "  const [meta,lodMeta,coarseElevation]=await Promise.all([loadJSON('./data/terrain-meta.json'),loadJSON('./data/lod/lod-meta.json'),loadFloat32('./data/lod/coarse-20m.bin')]);\n"
        "  const terrainCount=meta.width*meta.height;\n"
        "  if(coarseElevation.length!==lodMeta.coarse.width*lodMeta.coarse.height)throw new Error('Coarse terrain data size mismatch');\n"
        "  let elevation=null,elevationPromise=null;\n"
        "  async function ensureFullElevation(){if(elevation)return elevation;if(elevationPromise)return elevationPromise;elevationPromise=loadFloat32('./data/elevation.bin').then(data=>{if(data.length!==terrainCount)throw new Error('Full terrain data size mismatch');elevation=data;return data;}).catch(error=>{elevationPromise=null;throw error;});return elevationPromise;}\n"
        "  const widthM=meta.east_m-meta.west_m,heightM=meta.north_m-meta.south_m,centreX=(meta.east_m+meta.west_m)/2,centreY=(meta.north_m+meta.south_m)/2;",
        "progressive terrain startup",
    )

    geometry_pattern = (
        r"  const positions=new Float32Array\(terrainCount\*3\),colors=new Float32Array\(terrainCount\*3\),uvs=new Float32Array\(terrainCount\*2\);.*?"
        r"  const terrainMesh=new THREE\.Mesh\(terrainGeometry,terrainMaterial\);scene\.add\(terrainMesh\);"
    )
    geometry_replacement = """  function makeTerrainGeometry(grid,gridWidth,gridHeight,x0,z0,x1,z1,u0=0,v0=0,u1=1,v1=1){
    const count=gridWidth*gridHeight,positions=new Float32Array(count*3),colors=new Float32Array(count*3),uvs=new Float32Array(count*2);
    for(let row=0;row<gridHeight;row++)for(let col=0;col<gridWidth;col++){const i=row*gridWidth+col,p=i*3,u=i*2,fx=gridWidth===1?0:col/(gridWidth-1),fz=gridHeight===1?0:row/(gridHeight-1),e=grid[i];positions[p]=x0+(x1-x0)*fx;positions[p+1]=e-minE;positions[p+2]=z0+(z1-z0)*fz;const rgb=terrainColor((e-minE)/(maxE-minE));colors[p]=rgb[0];colors[p+1]=rgb[1];colors[p+2]=rgb[2];uvs[u]=u0+(u1-u0)*fx;uvs[u+1]=v0+(v1-v0)*fz;}
    const indices=new Uint32Array((gridWidth-1)*(gridHeight-1)*6);let k=0;for(let row=0;row<gridHeight-1;row++)for(let col=0;col<gridWidth-1;col++){const a=row*gridWidth+col,b=a+1,c=a+gridWidth,d=c+1;indices[k++]=a;indices[k++]=c;indices[k++]=b;indices[k++]=b;indices[k++]=c;indices[k++]=d;}
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.setAttribute('color',new THREE.BufferAttribute(colors,3));geometry.setAttribute('uv',new THREE.BufferAttribute(uvs,2));geometry.setIndex(new THREE.BufferAttribute(indices,1));geometry.computeVertexNormals();return geometry;
  }
  const terrainMaterial=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.94,metalness:.01,side:THREE.DoubleSide});
  const fineTerrainMaterial=terrainMaterial.clone();fineTerrainMaterial.polygonOffset=true;fineTerrainMaterial.polygonOffsetFactor=-1;fineTerrainMaterial.polygonOffsetUnits=-1;
  const terrainGeometry=makeTerrainGeometry(coarseElevation,lodMeta.coarse.width,lodMeta.coarse.height,-widthM*.5,-heightM*.5,widthM*.5,heightM*.5);
  const terrainMesh=new THREE.Mesh(terrainGeometry,terrainMaterial);scene.add(terrainMesh);
  const lodGroup=new THREE.Group();lodGroup.scale.y=Number(exaggeration.value);scene.add(lodGroup);
  const lodTiles=new Map(),lodLoading=new Set();let lodClock=.3;
  async function loadTerrainTile(tile){if(lodTiles.has(tile.id)||lodLoading.has(tile.id))return;lodLoading.add(tile.id);try{const data=await loadFloat32(tile.path);if(data.length!==tile.width*tile.height)throw new Error(tile.id+' terrain tile size mismatch');const geometry=makeTerrainGeometry(data,tile.width,tile.height,tile.x0_m,tile.z0_m,tile.x1_m,tile.z1_m,tile.u0,tile.v0,tile.u1,tile.v1),mesh=new THREE.Mesh(geometry,fineTerrainMaterial);mesh.userData.tileId=tile.id;lodTiles.set(tile.id,mesh);lodGroup.add(mesh);}catch(error){console.warn('Terrain LOD tile failed',tile.id,error);}finally{lodLoading.delete(tile.id);}}
  function updateTerrainLOD(dt){lodClock+=dt;if(lodClock<.22)return;lodClock=0;const terrainOnly=layerSelect.value==='terrain';lodGroup.visible=terrainOnly;if(!terrainOnly)return;const maxTiles=isMobile?9:18,targetX=controls.target.x,targetZ=controls.target.z,ranked=lodMeta.tiles.map(tile=>({tile,score:Math.hypot(tile.centre_x_m-targetX,tile.centre_z_m-targetZ)})).sort((a,b)=>a.score-b.score),wanted=new Set(ranked.slice(0,maxTiles).map(item=>item.tile.id));for(const item of ranked.slice(0,maxTiles))void loadTerrainTile(item.tile);for(const [id,mesh] of lodTiles){if(wanted.has(id))continue;lodGroup.remove(mesh);mesh.geometry.dispose();lodTiles.delete(id);}}
"""
    text = regex_once(text, geometry_pattern, geometry_replacement, "LOD terrain geometry")

    text = replace_once(
        text,
        "  function updateStaticColors(){setGeometryColors(terrainGeometry,terrainCount,i=>terrainColor((elevation[i]-minE)/(maxE-minE)));}",
        "  function updateStaticColors(){/* terrain colours are baked into the coarse and streamed tile geometries */}",
        "LOD static terrain colours",
    )

    text = replace_once(
        text,
        "  buildContourLabels();\n",
        "  let contourLabelsBuilt=false,contourLabelsLoading=null;\n"
        "  async function ensureContourLabels(){if(contourLabelsBuilt)return;if(contourLabelsLoading)return contourLabelsLoading;contourLabelsLoading=ensureFullElevation().then(()=>{buildContourLabels();contourLabelsBuilt=true;});return contourLabelsLoading;}\n",
        "deferred contour labels",
    )

    text = replace_once(
        text,
        "  async function loadForest(){try{const [fm,mask]=await Promise.all([loadJSON('./data/forest-meta.json'),loadUint8('./data/forest-mask.bin')]);if(mask.length!==terrainCount)throw new Error('forest mask size mismatch');treeMesh=makeTreeMesh(mask);",
        "  async function loadForest(){try{const [fm,mask]=await Promise.all([loadJSON('./data/forest-meta.json'),loadUint8('./data/forest-mask.bin')]);if(mask.length!==terrainCount)throw new Error('forest mask size mismatch');await ensureFullElevation();treeMesh=makeTreeMesh(mask);",
        "deferred full terrain for forest",
    )

    text = replace_once(
        text,
        "else if(layer==='wind'){const vals=interpolatedField(weather.data.windSpeed,t)",
        "else if(layer==='wind'){await ensureFullElevation();const vals=interpolatedField(weather.data.windSpeed,t)",
        "full terrain before wind airflow",
    )

    text = replace_once(
        text,
        "  const WIND_SEGMENTS=16,WIND_COUNT=160;",
        "  const WIND_SEGMENTS=16,WIND_COUNT=isMobile?88:160;",
        "adaptive mobile wind count",
    )

    text = replace_once(
        text,
        "  async function updateLayer(){const layer=layerSelect.value,isDynamic=dynamicLayers.has(layer);",
        "  async function updateLayer(){const layer=layerSelect.value,isDynamic=dynamicLayers.has(layer);lodGroup.visible=layer==='terrain';",
        "LOD visibility by layer",
    )

    text = replace_once(
        text,
        "  function updateVertical(){const v=Number(exaggeration.value);terrainMesh.scale.y=v;overlayMesh.scale.y=v;contourMesh.scale.y=v;if(treeMesh)treeMesh.scale.y=v;verticalValue.textContent=v.toFixed(2).replace(/0+$/,'').replace(/\\.$/,'')+'×';}",
        "  function updateVertical(){const v=Number(exaggeration.value);terrainMesh.scale.y=v;lodGroup.scale.y=v;overlayMesh.scale.y=v;contourMesh.scale.y=v;if(treeMesh)treeMesh.scale.y=v;verticalValue.textContent=v.toFixed(2).replace(/0+$/,'').replace(/\\.$/,'')+'×';}",
        "LOD vertical scaling",
    )

    text = replace_once(
        text,
        "topoToggle.addEventListener('change',()=>{contourMesh.visible=topoToggle.checked;});",
        "topoToggle.addEventListener('change',()=>{contourMesh.visible=topoToggle.checked;if(topoToggle.checked)void ensureContourLabels();});",
        "deferred contour label toggle",
    )

    text = replace_once(
        text,
        "controls.update();updateFeatureLabels();updateContourLabels(dt);updateCompass();animateWind(dt);renderer.render(scene,camera);",
        "controls.update();updateTerrainLOD(dt);updateFeatureLabels();updateContourLabels(dt);updateCompass();animateWind(dt);renderer.render(scene,camera);",
        "LOD frame update",
    )

    text = replace_once(
        text,
        "  await Promise.allSettled([loadForest(),loadFeatures()]);loadWeatherMetadata().catch(e=>{console.error(e);status.classList.add('error');status.textContent='Terrain loaded; weather metadata failed: '+e.message;});",
        "  await loadFeatures();loadWeatherMetadata().catch(e=>{console.error(e);status.classList.add('error');status.textContent='Terrain loaded; weather metadata failed: '+e.message;});const deferredForest=()=>void loadForest();if('requestIdleCallback' in window)requestIdleCallback(deferredForest,{timeout:3000});else setTimeout(deferredForest,1400);",
        "deferred forest loading",
    )

    path.write_text(text, encoding="utf-8")
    print("Applied progressive 20 m fallback + streamed 5 m terrain tile LOD")


if __name__ == "__main__":
    run()
