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
        "const BUILD_ID='snow-heatmap-5m-20261010-13';",
        "const BUILD_ID='snow-heatmap-5m-20261010-14';",
        "build id",
    )

    text = replace_once(
        text,
        "const geometry=makeTerrainGeometry(data,tile.width,tile.height,tile.x0_m,tile.z0_m,tile.x1_m,tile.z1_m,tile.u0,tile.v0,tile.u1,tile.v1),mesh=new THREE.Mesh(geometry,fineTerrainMaterial);mesh.position.y=.35;mesh.userData.tileId=tile.id;lodTiles.set(tile.id,mesh);lodGroup.add(mesh);",
        "const geometry=makeTerrainGeometry(data,tile.width,tile.height,tile.x0_m,tile.z0_m,tile.x1_m,tile.z1_m,tile.u0,tile.v0,tile.u1,tile.v1),mesh=new THREE.Mesh(geometry,fineTerrainMaterial);mesh.position.y=.35;mesh.userData.tileId=tile.id;mesh.userData.tile=tile;mesh.userData.elevation=data;const tileOverlay=new THREE.Mesh(geometry,overlayMaterial);tileOverlay.visible=overlayMesh.visible;mesh.userData.overlay=tileOverlay;mesh.add(tileOverlay);lodTiles.set(tile.id,mesh);lodGroup.add(mesh);",
        "fine terrain shared weather overlay",
    )

    old_height = (
        "  function terrainHeightAt(x,z){const w=lodMeta.coarse.width,h=lodMeta.coarse.height,fx=clamp01(x/widthM+.5)*(w-1),fz=clamp01(z/heightM+.5)*(h-1),c0=Math.floor(fx),r0=Math.floor(fz),c1=Math.min(w-1,c0+1),r1=Math.min(h-1,r0+1),tx=fx-c0,tz=fz-r0;const e00=coarseElevation[r0*w+c0]-minE,e10=coarseElevation[r0*w+c1]-minE,e01=coarseElevation[r1*w+c0]-minE,e11=coarseElevation[r1*w+c1]-minE;return(e00+(e10-e00)*tx)*(1-tz)+(e01+(e11-e01)*tx)*tz;}\n"
    )
    new_height = (
        "  function terrainHeightAt(x,z){const sourceCol=clamp01(x/widthM+.5)*(meta.width-1),sourceRow=clamp01(z/heightM+.5)*(meta.height-1),tileCol=Math.min(lodMeta.tile_cols-1,Math.floor(sourceCol/lodMeta.tile_cells)),tileRow=Math.min(lodMeta.tile_rows-1,Math.floor(sourceRow/lodMeta.tile_cells)),fine=lodTiles.get('r'+tileRow+'-c'+tileCol);if(fine?.userData?.elevation){const tile=fine.userData.tile,data=fine.userData.elevation,fx=sourceCol-tile.col0,fz=sourceRow-tile.row0,c0=Math.max(0,Math.min(tile.width-1,Math.floor(fx))),r0=Math.max(0,Math.min(tile.height-1,Math.floor(fz))),c1=Math.min(tile.width-1,c0+1),r1=Math.min(tile.height-1,r0+1),tx=Math.max(0,Math.min(1,fx-c0)),tz=Math.max(0,Math.min(1,fz-r0)),e00=data[r0*tile.width+c0]-minE,e10=data[r0*tile.width+c1]-minE,e01=data[r1*tile.width+c0]-minE,e11=data[r1*tile.width+c1]-minE;return(e00+(e10-e00)*tx)*(1-tz)+(e01+(e11-e01)*tx)*tz;}const w=lodMeta.coarse.width,h=lodMeta.coarse.height,fx=clamp01(x/widthM+.5)*(w-1),fz=clamp01(z/heightM+.5)*(h-1),c0=Math.floor(fx),r0=Math.floor(fz),c1=Math.min(w-1,c0+1),r1=Math.min(h-1,r0+1),tx=fx-c0,tz=fz-r0,e00=coarseElevation[r0*w+c0]-minE,e10=coarseElevation[r0*w+c1]-minE,e01=coarseElevation[r1*w+c0]-minE,e11=coarseElevation[r1*w+c1]-minE;return(e00+(e10-e00)*tx)*(1-tz)+(e01+(e11-e01)*tx)*tz;}\n"
    )
    text = replace_once(text, old_height, new_height, "LOD-aware terrain height sampling")

    text = replace_once(
        text,
        "  function airflowHeightAt(x,z,dx,dz){const s=34,h0=terrainHeightAt(x,z),h1a=terrainHeightAt(x-dx*s,z-dz*s),h1b=terrainHeightAt(x+dx*s,z+dz*s),h2a=terrainHeightAt(x-dx*s*2,z-dz*s*2),h2b=terrainHeightAt(x+dx*s*2,z+dz*s*2),smooth=(h0*4+(h1a+h1b)*2+h2a+h2b)/10,broad=(h0+h1a+h1b+h2a+h2b)/5;return Math.max(h0+18,smooth+30,broad+26);}",
        "  function airflowHeightAt(x,z,dx,dz){const s=34,h0=terrainHeightAt(x,z),h1a=terrainHeightAt(x-dx*s,z-dz*s),h1b=terrainHeightAt(x+dx*s,z+dz*s),h2a=terrainHeightAt(x-dx*s*2,z-dz*s*2),h2b=terrainHeightAt(x+dx*s*2,z+dz*s*2),smooth=(h0*4+(h1a+h1b)*2+h2a+h2b)/10,broad=(h0+h1a+h1b+h2a+h2b)/5;return Math.max(h0+26,smooth+38,broad+34);}",
        "airflow clearance over fine terrain",
    )

    text = replace_once(
        text,
        "windArrowGeometry.setDrawRange(0,0);windLines.add(windArrows);windLines.visible=false;scene.add(windLines);",
        "windArrowGeometry.setDrawRange(0,0);windLines.add(windArrows);windLines.visible=false;windLines.renderOrder=8;windArrows.renderOrder=9;scene.add(windLines);",
        "wind render order",
    )

    text = replace_once(
        text,
        "  const weatherSpecs={snow:{label:'New snow accumulation'},wind:{label:'Wind speed'},solar:{label:'Solar loading'}};\n  const weatherChunkCache=new Map(),weatherChunkLoading=new Map();let dynamicRenderToken=0;",
        "  const weatherSpecs={snow:{label:'New snow accumulation'},wind:{label:'Wind speed'},solar:{label:'Solar loading'}};\n"
        "  function setOverlay(values,maxValue,mode){const w=weather.meta.width,h=weather.meta.height,bytes=new Uint8Array(w*h*4);for(let i=0;i<w*h;i++){const n=clamp01(values[i]/maxValue),v=Math.round(n*255),p=i*4;bytes[p]=v;bytes[p+1]=v;bytes[p+2]=v;bytes[p+3]=255;}if(overlayTexture)overlayTexture.dispose();overlayTexture=new THREE.DataTexture(bytes,w,h,THREE.RGBAFormat,THREE.UnsignedByteType);overlayTexture.flipY=false;overlayTexture.minFilter=THREE.LinearFilter;overlayTexture.magFilter=THREE.LinearFilter;overlayTexture.needsUpdate=true;overlayMaterial.uniforms.dataMap.value=overlayTexture;overlayMaterial.uniforms.mode.value=mode;overlayMesh.visible=true;for(const mesh of lodTiles.values())if(mesh.userData.overlay)mesh.userData.overlay.visible=true;updateEarthBlockColors(layerSelect.value,values,maxValue,mode);}\n"
        "  const weatherChunkCache=new Map(),weatherChunkLoading=new Map();let dynamicRenderToken=0;",
        "restore streamed overlay renderer",
    )

    text = replace_once(
        text,
        "timeLabel.textContent=formatTimeFraction(weather.meta,t);windLines.visible=false;updateStaticColors('terrain');status.classList.remove('error');",
        "timeLabel.textContent=formatTimeFraction(weather.meta,t);windLines.visible=false;status.classList.remove('error');",
        "remove stale static colour call from dynamic renderer",
    )

    text = replace_once(
        text,
        "if(!isDynamic){overlayMesh.visible=false;timeLabel.textContent='';updateStaticColors(layer);status.classList.remove('error');",
        "if(!isDynamic){overlayMesh.visible=false;for(const mesh of lodTiles.values())if(mesh.userData.overlay)mesh.userData.overlay.visible=false;updateEarthBlockColors('terrain');timeLabel.textContent='';status.classList.remove('error');",
        "remove stale static colour call from layer switch",
    )

    text = replace_once(
        text,
        "  // Give the map extent a physical sliced-earth base instead of leaving the DEM as a floating sheet.\n  function makeEarthBlock(){",
        "  // Give the map extent a physical sliced-earth base instead of leaving the DEM as a floating sheet.\n  const earthEdgeSamples=[];let earthBottomVertexStart=0;\n  function makeEarthBlock(){",
        "earth edge colour state",
    )

    text = replace_once(
        text,
        "    const w=lodMeta.coarse.width,h=lodMeta.coarse.height,blockDepth=Math.min(260,Math.max(180,sceneSpan*.055)),bottomY=-blockDepth,positions=[],indices=[];",
        "    const w=lodMeta.coarse.width,h=lodMeta.coarse.height,blockDepth=Math.min(260,Math.max(180,sceneSpan*.055)),bottomY=-blockDepth,positions=[],colors=[],indices=[];earthEdgeSamples.length=0;",
        "earth block vertex colours",
    )

    text = replace_once(
        text,
        "    function addWall(samples){const base=positions.length/3;for(const s of samples){positions.push(s.x,s.y,s.z,s.x,bottomY,s.z);}for(let i=0;i<samples.length-1;i++){const a=base+i*2,b=a+1,c=a+2,d=a+3;indices.push(a,b,c,c,b,d);}}",
        "    function addWall(samples){const base=positions.length/3;for(const s of samples){const top=positions.length/3;positions.push(s.x,s.y,s.z,s.x,bottomY,s.z);colors.push(.72,.72,.71,.62,.62,.61);earthEdgeSamples.push({top,bottom:top+1,x:s.x,z:s.z,elevation:s.y+minE});}for(let i=0;i<samples.length-1;i++){const a=base+i*2,b=a+1,c=a+2,d=a+3;indices.push(a,b,c,c,b,d);}}",
        "earth wall edge samples",
    )

    text = replace_once(
        text,
        "    const base=positions.length/3;positions.push(-widthM*.5,bottomY,-heightM*.5,widthM*.5,bottomY,-heightM*.5,widthM*.5,bottomY,heightM*.5,-widthM*.5,bottomY,heightM*.5);indices.push(base,base+1,base+2,base,base+2,base+3);",
        "    const base=positions.length/3;earthBottomVertexStart=base;positions.push(-widthM*.5,bottomY,-heightM*.5,widthM*.5,bottomY,-heightM*.5,widthM*.5,bottomY,heightM*.5,-widthM*.5,bottomY,heightM*.5);colors.push(.62,.62,.61,.62,.62,.61,.62,.62,.61,.62,.62,.61);indices.push(base,base+1,base+2,base,base+2,base+3);",
        "earth bottom colours",
    )

    text = replace_once(
        text,
        "    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setIndex(indices);geometry.computeVertexNormals();",
        "    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));geometry.setIndex(indices);geometry.computeVertexNormals();",
        "earth block colour attribute",
    )

    text = replace_once(
        text,
        "    const material=new THREE.MeshStandardMaterial({color:0x756f69,roughness:1,metalness:0,side:THREE.DoubleSide});",
        "    const material=new THREE.MeshStandardMaterial({vertexColors:true,roughness:1,metalness:0,side:THREE.DoubleSide});",
        "neutral vertex-coloured earth material",
    )

    text = replace_once(
        text,
        "  const earthBlock=makeEarthBlock();earthBlock.scale.y=Number(exaggeration.value);scene.add(earthBlock);",
        "  const earthBlock=makeEarthBlock();earthBlock.scale.y=Number(exaggeration.value);scene.add(earthBlock);\n"
        "  function earthPalette(mode,x){x=clamp01(x);if(mode<.5)return interpolateStops(x,[[0,[.04,.08,.28]],[.17,[.03,.25,.90]],[.34,[.02,.78,.92]],[.51,[.10,.72,.32]],[.68,[.94,.84,.08]],[.84,[.96,.43,.06]],[1,[.86,.06,.06]]]);if(mode<2.5)return interpolateStops(x,[[0,[.08,.18,.18]],[.55,[.35,.58,.48]],[1,[.94,.72,.38]]]);return interpolateStops(x,[[0,[.10,.12,.15]],[.55,[.62,.53,.20]],[1,[1,.85,.36]]]);}\n"
        "  function sampleWeatherEdge(values,x,z){if(!weather||!values)return 0;const b=weather.meta.bounds_m,w=weather.meta.width,h=weather.meta.height,px=centreX+x,py=centreY-z,fx=clamp01((px-b.west)/(b.east-b.west))*(w-1),fy=clamp01((b.north-py)/(b.north-b.south))*(h-1),c0=Math.floor(fx),r0=Math.floor(fy),c1=Math.min(w-1,c0+1),r1=Math.min(h-1,r0+1),tx=fx-c0,ty=fy-r0,v00=values[r0*w+c0],v10=values[r0*w+c1],v01=values[r1*w+c0],v11=values[r1*w+c1];return(v00+(v10-v00)*tx)*(1-ty)+(v01+(v11-v01)*tx)*ty;}\n"
        "  function updateEarthBlockColors(layer='terrain',values=null,maxValue=1,mode=0){const attr=earthBlock.geometry.getAttribute('color'),c=attr.array;let ar=0,ag=0,ab=0,n=0;for(const s of earthEdgeSamples){let rgb;if(layer==='terrain'||!values){const base=terrainColor(clamp01((s.elevation-minE)/(maxE-minE))),l=(base[0]+base[1]+base[2])/3,shade=Math.min(.86,Math.max(.62,.58+l*.32));rgb=[shade,shade,shade*.99];}else rgb=earthPalette(mode,sampleWeatherEdge(values,s.x,s.z)/Math.max(maxValue,.0001));const bottom=[rgb[0]*.68+.18,rgb[1]*.68+.18,rgb[2]*.68+.18];let p=s.top*3;c[p]=rgb[0];c[p+1]=rgb[1];c[p+2]=rgb[2];p=s.bottom*3;c[p]=bottom[0];c[p+1]=bottom[1];c[p+2]=bottom[2];ar+=bottom[0];ag+=bottom[1];ab+=bottom[2];n++;}const avg=[ar/Math.max(1,n),ag/Math.max(1,n),ab/Math.max(1,n)];for(let i=0;i<4;i++){const p=(earthBottomVertexStart+i)*3;c[p]=avg[0];c[p+1]=avg[1];c[p+2]=avg[2];}attr.needsUpdate=true;}\n"
        "  updateEarthBlockColors('terrain');",
        "layer-aware earth block colours",
    )

    path.write_text(text, encoding="utf-8")
    print("Fixed streamed overlays/wind, draped overlays onto 5 m tiles, and matched block colours to active layer")


if __name__ == "__main__":
    run()
