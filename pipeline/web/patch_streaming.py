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
        "const BUILD_ID='snow-heatmap-5m-20261009-11';",
        "const BUILD_ID='snow-heatmap-5m-20261010-12';",
        "build id",
    )

    text = replace_once(
        text,
        "const geometry=makeTerrainGeometry(data,tile.width,tile.height,tile.x0_m,tile.z0_m,tile.x1_m,tile.z1_m,tile.u0,tile.v0,tile.u1,tile.v1),mesh=new THREE.Mesh(geometry,fineTerrainMaterial);mesh.userData.tileId=tile.id;lodTiles.set(tile.id,mesh);lodGroup.add(mesh);",
        "const geometry=makeTerrainGeometry(data,tile.width,tile.height,tile.x0_m,tile.z0_m,tile.x1_m,tile.z1_m,tile.u0,tile.v0,tile.u1,tile.v1),mesh=new THREE.Mesh(geometry,fineTerrainMaterial);mesh.position.y=.35;mesh.userData.tileId=tile.id;lodTiles.set(tile.id,mesh);lodGroup.add(mesh);",
        "fine terrain depth priority",
    )

    old_lod = (
        "  function updateTerrainLOD(dt){lodClock+=dt;if(lodClock<.22)return;lodClock=0;const terrainOnly=layerSelect.value==='terrain';lodGroup.visible=terrainOnly;if(!terrainOnly)return;const maxTiles=isMobile?9:18,targetX=controls.target.x,targetZ=controls.target.z,ranked=lodMeta.tiles.map(tile=>({tile,score:Math.hypot(tile.centre_x_m-targetX,tile.centre_z_m-targetZ)})).sort((a,b)=>a.score-b.score),wanted=new Set(ranked.slice(0,maxTiles).map(item=>item.tile.id));for(const item of ranked.slice(0,maxTiles))void loadTerrainTile(item.tile);for(const [id,mesh] of lodTiles){if(wanted.has(id))continue;lodGroup.remove(mesh);mesh.geometry.dispose();lodTiles.delete(id);}}\n"
    )
    new_lod = (
        "  function updateTerrainLOD(dt){lodClock+=dt;if(lodClock<.22)return;lodClock=0;lodGroup.visible=true;const maxTiles=isMobile?12:24,targetX=controls.target.x,targetZ=controls.target.z,ranked=lodMeta.tiles.map(tile=>({tile,score:Math.hypot(tile.centre_x_m-targetX,tile.centre_z_m-targetZ)})).sort((a,b)=>a.score-b.score),wantedItems=ranked.slice(0,maxTiles),wanted=new Set(wantedItems.map(item=>item.tile.id));for(const item of wantedItems)void loadTerrainTile(item.tile);for(const [id,mesh] of lodTiles){if(wanted.has(id))continue;lodGroup.remove(mesh);mesh.geometry.dispose();lodTiles.delete(id);}if(layerSelect.value==='terrain'){let ready=0;for(const id of wanted)if(lodTiles.has(id))ready++;status.classList.remove('error');status.textContent='Terrain · 20 m base + 5 m detail '+ready+'/'+wanted.size+' tiles · build '+BUILD_ID;}}\n"
    )
    text = replace_once(text, old_lod, new_lod, "always-on terrain LOD")

    text = replace_once(
        text,
        "  async function updateLayer(){const layer=layerSelect.value,isDynamic=dynamicLayers.has(layer);lodGroup.visible=layer==='terrain';",
        "  async function updateLayer(){const layer=layerSelect.value,isDynamic=dynamicLayers.has(layer);lodGroup.visible=true;",
        "LOD visibility under overlays",
    )

    terrain_height_old = (
        "  function terrainHeightAt(x,z){const fx=clamp01(x/widthM+.5)*(meta.width-1),fz=clamp01(z/heightM+.5)*(meta.height-1),c0=Math.floor(fx),r0=Math.floor(fz),c1=Math.min(meta.width-1,c0+1),r1=Math.min(meta.height-1,r0+1),tx=fx-c0,tz=fz-r0;const e00=elevation[r0*meta.width+c0]-minE,e10=elevation[r0*meta.width+c1]-minE,e01=elevation[r1*meta.width+c0]-minE,e11=elevation[r1*meta.width+c1]-minE;return(e00+(e10-e00)*tx)*(1-tz)+(e01+(e11-e01)*tx)*tz;}\n"
    )
    terrain_height_new = (
        "  function terrainHeightAt(x,z){const w=lodMeta.coarse.width,h=lodMeta.coarse.height,fx=clamp01(x/widthM+.5)*(w-1),fz=clamp01(z/heightM+.5)*(h-1),c0=Math.floor(fx),r0=Math.floor(fz),c1=Math.min(w-1,c0+1),r1=Math.min(h-1,r0+1),tx=fx-c0,tz=fz-r0;const e00=coarseElevation[r0*w+c0]-minE,e10=coarseElevation[r0*w+c1]-minE,e01=coarseElevation[r1*w+c0]-minE,e11=coarseElevation[r1*w+c1]-minE;return(e00+(e10-e00)*tx)*(1-tz)+(e01+(e11-e01)*tx)*tz;}\n"
    )
    text = replace_once(text, terrain_height_old, terrain_height_new, "coarse airflow height sampling")

    text = replace_once(
        text,
        "matrix.compose(new THREE.Vector3((c/(meta.width-1)-.5)*widthM,elevation[i]-minE,(r/(meta.height-1)-.5)*heightM),q,s);",
        "matrix.compose(new THREE.Vector3((c/(meta.width-1)-.5)*widthM,terrainHeightAt((c/(meta.width-1)-.5)*widthM,(r/(meta.height-1)-.5)*heightM),(r/(meta.height-1)-.5)*heightM),q,s);",
        "coarse tree height sampling",
    )

    text = replace_once(
        text,
        "if(mask.length!==terrainCount)throw new Error('forest mask size mismatch');await ensureFullElevation();treeMesh=makeTreeMesh(mask);",
        "if(mask.length!==terrainCount)throw new Error('forest mask size mismatch');treeMesh=makeTreeMesh(mask);",
        "remove forest full-elevation download",
    )

    weather_pattern = r"  const weatherSpecs=.*?\n\n  function makeTreeMesh\(mask\)"
    weather_replacement = """  const weatherSpecs={snow:{label:'New snow accumulation'},wind:{label:'Wind speed'},solar:{label:'Solar loading'}};
  const weatherChunkCache=new Map(),weatherChunkLoading=new Map();let dynamicRenderToken=0;
  function weatherChunkPath(field,chunk,windowKey=''){const root=weather.meta.chunks.path_root,index=String(chunk).padStart(2,'0');if(field==='snow')return root+'/snow-'+windowKey+'-'+index+'.bin';if(field==='windSpeed')return root+'/wind-speed-'+index+'.bin';if(field==='windDirection')return root+'/wind-direction-'+index+'.bin';return root+'/shortwave-'+index+'.bin';}
  function chunkHourCount(chunk){const start=chunk*weather.meta.chunks.hours_per_chunk;return Math.max(0,Math.min(weather.meta.chunks.hours_per_chunk,weather.meta.hours-start));}
  async function loadWeatherChunk(field,chunk,windowKey=''){const key=field+':'+windowKey+':'+chunk;if(weatherChunkCache.has(key))return weatherChunkCache.get(key);if(weatherChunkLoading.has(key))return weatherChunkLoading.get(key);const promise=loadFloat32(weatherChunkPath(field,chunk,windowKey)).then(data=>{const expected=weather.meta.width*weather.meta.height*chunkHourCount(chunk);if(data.length!==expected)throw new Error(key+' chunk size mismatch');weatherChunkCache.set(key,data);return data;}).finally(()=>weatherChunkLoading.delete(key));weatherChunkLoading.set(key,promise);return promise;}
  async function weatherSlices(field,t,windowKey=''){const count=weather.meta.width*weather.meta.height,a=Math.floor(t),b=Math.min(weather.meta.hours-1,Math.ceil(t)),f=t-a,hpc=weather.meta.chunks.hours_per_chunk,ca=Math.floor(a/hpc),cb=Math.floor(b/hpc),chunks=ca===cb?[await loadWeatherChunk(field,ca,windowKey)]:await Promise.all([loadWeatherChunk(field,ca,windowKey),loadWeatherChunk(field,cb,windowKey)]),A=chunks[0],B=ca===cb?chunks[0]:chunks[1],oa=(a-ca*hpc)*count,ob=(b-cb*hpc)*count;return{A:A.subarray(oa,oa+count),B:B.subarray(ob,ob+count),f,a,b};}
  function interpolateSlices(A,B,f){const out=new Float32Array(A.length);for(let i=0;i<A.length;i++)out[i]=A[i]+(B[i]-A[i])*f;return out;}
  function updateSnowLegend(){const s=weather?.meta?.chunks?.snow_scales?.[snowWindow.value]||1;snowMid.textContent=(s/2).toFixed(s<10?1:0);snowMax.textContent=s.toFixed(s<10?1:0)+' mm SWE';}
  async function renderDynamic(){const layer=layerSelect.value;if(!dynamicLayers.has(layer)||!weather)return;const token=++dynamicRenderToken,t=Number(timeSlider.value),summary=weather.meta.summary[Math.round(t)];timeLabel.textContent=formatTimeFraction(weather.meta,t);windLines.visible=false;updateStaticColors('terrain');status.classList.remove('error');status.textContent='Loading '+(weatherSpecs[layer]?.label||layer).toLowerCase()+'…';try{if(layer==='snow'){const pair=await weatherSlices('snow',t,snowWindow.value);if(token!==dynamicRenderToken)return;const vals=interpolateSlices(pair.A,pair.B,pair.f),scale=weather.meta.chunks.snow_scales[snowWindow.value];setOverlay(vals,scale,0);updateSnowLegend();let max=0;for(const v of vals)if(v>max)max=v;status.textContent=(snowWindow.value==='storm'?'Storm-to-date':snowWindow.value+' h')+' new snow · max in view '+max.toFixed(1)+' mm SWE · 12 h streamed data';}else if(layer==='wind'){const [speed,direction]=await Promise.all([weatherSlices('windSpeed',t),weatherSlices('windDirection',t)]);if(token!==dynamicRenderToken)return;const vals=interpolateSlices(speed.A,speed.B,speed.f),norm=new Float32Array(vals.length);for(let i=0;i<vals.length;i++)norm[i]=clamp01(vals[i]/15);setOverlay(norm,1,2);windLines.visible=true;updateWindFieldSlices(speed.A,speed.B,direction.A,direction.B,speed.f,speed.a,speed.b);status.textContent='Wind overlay · mean '+summary.wind_speed_mean_m_s.toFixed(1)+' m/s from '+cardinal(summary.wind_direction_mean_deg)+' · 12 h streamed data · low-confidence ridge estimate';}else if(layer==='solar'){const pair=await weatherSlices('shortwave',t);if(token!==dynamicRenderToken)return;const vals=interpolateSlices(pair.A,pair.B,pair.f),norm=new Float32Array(vals.length);for(let i=0;i<vals.length;i++)norm[i]=clamp01(vals[i]/800);setOverlay(norm,1,3);status.textContent='Solar loading overlay · mean '+summary.shortwave_mean_w_m2.toFixed(0)+' W/m² · 12 h streamed data';}}catch(e){if(token!==dynamicRenderToken)return;console.error(e);status.classList.add('error');status.textContent=(weatherSpecs[layer]?.label||layer)+' failed: '+e.message;}}

  function makeTreeMesh(mask)"""
    text = regex_once(text, weather_pattern, weather_replacement, "chunked dynamic weather renderer")

    old_wind_update = (
        "  function updateWindField(t){if(!windAnchors.length)buildWindAnchors();const a=Math.floor(t),b=Math.min(weather.meta.hours-1,Math.ceil(t)),f=t-a,count=weather.meta.width*weather.meta.height;for(const anchor of windAnchors){const i=anchor.index,sa=weather.data.windSpeed[a*count+i],sb=weather.data.windSpeed[b*count+i];anchor.speed=sa+(sb-sa)*f;let da=weather.data.windDirection[a*count+i],db=weather.data.windDirection[b*count+i];if(!Number.isFinite(da))da=weather.meta.summary[a].wind_direction_mean_deg||0;if(!Number.isFinite(db))db=weather.meta.summary[b].wind_direction_mean_deg||da;anchor.direction=angleLerp(da,db,f);}}\n"
    )
    new_wind_update = (
        "  function updateWindFieldSlices(speedA,speedB,directionA,directionB,f,aHour,bHour){if(!windAnchors.length)buildWindAnchors();for(const anchor of windAnchors){const i=anchor.index,sa=speedA[i],sb=speedB[i];anchor.speed=sa+(sb-sa)*f;let da=directionA[i],db=directionB[i];if(!Number.isFinite(da))da=weather.meta.summary[aHour].wind_direction_mean_deg||0;if(!Number.isFinite(db))db=weather.meta.summary[bHour].wind_direction_mean_deg||da;anchor.direction=angleLerp(da,db,f);}}\n"
    )
    text = replace_once(text, old_wind_update, new_wind_update, "chunked wind field slices")

    text = replace_once(
        text,
        "snowWindow.addEventListener('change',()=>{accumCache.clear();if(layerSelect.value==='snow')void renderDynamic();});",
        "snowWindow.addEventListener('change',()=>{if(layerSelect.value==='snow')void renderDynamic();});",
        "snow chunk window change",
    )

    path.write_text(text, encoding="utf-8")
    print("Applied always-on 5 m LOD, coarse terrain sampling for wind/trees, and 12 h weather streaming")


if __name__ == "__main__":
    run()
