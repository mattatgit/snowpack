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
        "const BUILD_ID='snow-heatmap-5m-20261009-5';",
        "const BUILD_ID='snow-heatmap-5m-20261009-7';",
        "build id",
    )

    text = replace_once(
        text,
        "    .map-label .dot { display:block; width:5px; height:5px; margin:4px auto 0; border-radius:50%; background:#fff; box-shadow:0 0 4px #000; }\n",
        "    .map-label .dot { display:block; width:5px; height:5px; margin:4px auto 0; border-radius:50%; background:#fff; box-shadow:0 0 4px #000; }\n"
        "    .contour-label { position:absolute; transform:translate(-50%,-50%); padding:1px 4px; border-radius:3px; background:rgba(246,242,231,.78); color:#302a24; font-family:\"Inter Tight\",sans-serif; font-size:9px; font-weight:600; line-height:1.25; white-space:nowrap; box-shadow:0 0 0 1px rgba(65,54,43,.14); pointer-events:none; }\n",
        "contour label CSS",
    )

    text = replace_once(
        text,
        "      float contour(float interval,float thickness){float m=mod(vElevation,interval);float d=min(m,interval-m);float w=max(fwidth(vElevation)*thickness,.24);return 1.0-smoothstep(w,w*1.75,d);}\n"
        "      void main(){float minor=contour(10.0,1.0);float major=contour(50.0,1.45);float a=max(minor*.34,major*.76);if(a<.015)discard;vec3 c=mix(vec3(.30,.26,.22),vec3(.12,.10,.08),major);gl_FragColor=vec4(c,a);}`\n",
        "      float contour(float interval,float thickness){float m=mod(vElevation,interval);float d=min(m,interval-m);float w=max(fwidth(vElevation)*thickness,.12);return 1.0-smoothstep(w,w*1.55,d);}\n"
        "      void main(){float minor=contour(10.0,.55);float major=contour(50.0,.85);float a=max(minor*.30,major*.68);if(a<.015)discard;vec3 c=mix(vec3(.30,.26,.22),vec3(.12,.10,.08),major);gl_FragColor=vec4(c,a);}`\n",
        "thinner contour strokes",
    )

    text = replace_once(
        text,
        "  let treeMesh=null,forestAttribution='',featureLabels=[],weather=null,snowScales={},accumCache=new Map(),overlayTexture=null,windAnchors=[];",
        "  let treeMesh=null,forestAttribution='',featureLabels=[],contourLabels=[],contourLabelClock=0,weather=null,snowScales={},accumCache=new Map(),overlayTexture=null,windAnchors=[];",
        "contour label state",
    )

    text = replace_once(
        text,
        "  const windPositions=new Float32Array(6*160),windGeometry=new THREE.BufferGeometry();windGeometry.setAttribute('position',new THREE.BufferAttribute(windPositions,3));const windLines=new THREE.LineSegments(windGeometry,new THREE.LineBasicMaterial({color:0xf3fbff,transparent:true,opacity:.62}));windLines.visible=false;scene.add(windLines);",
        "  const WIND_SEGMENTS=16,WIND_COUNT=160;const windPositions=new Float32Array(WIND_COUNT*WIND_SEGMENTS*2*3),windGeometry=new THREE.BufferGeometry();windGeometry.setAttribute('position',new THREE.BufferAttribute(windPositions,3));const windLines=new THREE.LineSegments(windGeometry,new THREE.LineBasicMaterial({color:0xff6157,transparent:true,opacity:.88}));windLines.visible=false;scene.add(windLines);",
        "segmented red wind lines",
    )

    text = replace_once(
        text,
        "  async function loadFeatures(){try{const features=await loadJSON('./data/features.json');featureLabels=features.map(f=>{const el=document.createElement('div');el.className='map-label '+(f.kind==='summit'?'summit ':'')+(f.approximate?'approximate':'');el.innerHTML='<span>'+f.label+'</span><span class=\"dot\"></span>';featureLabelsRoot.appendChild(el);return{feature:f,element:el};});}catch(e){console.warn(e);}}\n"
        "  function updateFeatureLabels(){const vertical=Number(exaggeration.value);for(const item of featureLabels){const f=item.feature,p=new THREE.Vector3(f.x_m-centreX,(f.elevation_m-minE)*vertical+42,centreY-f.y_m);p.project(camera);if(p.z<-1||p.z>1||Math.abs(p.x)>1.15||Math.abs(p.y)>1.15){item.element.style.display='none';continue;}item.element.style.display='block';item.element.style.left=((p.x*.5+.5)*innerWidth)+'px';item.element.style.top=((-p.y*.5+.5)*innerHeight)+'px';}}\n",
        "  async function loadFeatures(){try{const features=await loadJSON('./data/features.json');featureLabels=features.map(f=>{const el=document.createElement('div');el.className='map-label '+(f.kind==='summit'?'summit ':'')+(f.approximate?'approximate':'');el.innerHTML='<span>'+f.label+'</span><span class=\"dot\"></span>';featureLabelsRoot.appendChild(el);return{feature:f,element:el};});}catch(e){console.warn(e);}}\n"
        "  function buildContourLabels(){const first=Math.ceil(minE/50)*50,last=Math.floor(maxE/50)*50,rowStep=Math.max(8,Math.round(90/meta.resolution_m)),colStep=rowStep;for(let level=first;level<=last;level+=50){const candidates=[];for(let row=Math.floor(rowStep/2);row<meta.height;row+=rowStep){for(let col=1;col<meta.width;col++){const e0=elevation[row*meta.width+col-1],e1=elevation[row*meta.width+col];if((e0-level)*(e1-level)>0||Math.abs(e1-e0)<.001)continue;const t=clamp01((level-e0)/(e1-e0));candidates.push({x:(((col-1+t)/(meta.width-1))-.5)*widthM,z:((row/(meta.height-1))-.5)*heightM});}}for(let col=Math.floor(colStep/2);col<meta.width;col+=colStep){for(let row=1;row<meta.height;row++){const e0=elevation[(row-1)*meta.width+col],e1=elevation[row*meta.width+col];if((e0-level)*(e1-level)>0||Math.abs(e1-e0)<.001)continue;const t=clamp01((level-e0)/(e1-e0));candidates.push({x:((col/(meta.width-1))-.5)*widthM,z:(((row-1+t)/(meta.height-1))-.5)*heightM});}}if(!candidates.length)continue;const el=document.createElement('div');el.className='contour-label';el.textContent=level+' m';featureLabelsRoot.appendChild(el);contourLabels.push({elevation:level,candidates,element:el,anchor:null});}}\n"
        "  buildContourLabels();\n"
        "  function updateFeatureLabels(){const vertical=Number(exaggeration.value);for(const item of featureLabels){const f=item.feature,p=new THREE.Vector3(f.x_m-centreX,(f.elevation_m-minE)*vertical+42,centreY-f.y_m);p.project(camera);if(p.z<-1||p.z>1||Math.abs(p.x)>1.15||Math.abs(p.y)>1.15){item.element.style.display='none';continue;}item.element.style.display='block';item.element.style.left=((p.x*.5+.5)*innerWidth)+'px';item.element.style.top=((-p.y*.5+.5)*innerHeight)+'px';}}\n"
        "  function chooseContourAnchors(){if(!topoToggle.checked)return;const vertical=Number(exaggeration.value),world=new THREE.Vector3(),projected=new THREE.Vector3();for(const item of contourLabels){let best=null,bestScore=Infinity;for(const c of item.candidates){world.set(c.x,(item.elevation-minE)*vertical+5,c.z);projected.copy(world).project(camera);if(projected.z<-1||projected.z>1||Math.abs(projected.x)>.88||Math.abs(projected.y)>.86)continue;const distance=camera.position.distanceTo(world),centrePenalty=(Math.abs(projected.x)*.18+Math.abs(projected.y)*.10)*sceneSpan,score=distance+centrePenalty;if(score<bestScore){best=c;bestScore=score;}}item.anchor=best;}}\n"
        "  function updateContourLabels(dt){const show=topoToggle.checked,vertical=Number(exaggeration.value);contourLabelClock+=dt;if(show&&contourLabelClock>.12){chooseContourAnchors();contourLabelClock=0;}for(const item of contourLabels){if(!show||!item.anchor){item.element.style.display='none';continue;}const p=new THREE.Vector3(item.anchor.x,(item.elevation-minE)*vertical+5,item.anchor.z);p.project(camera);if(p.z<-1||p.z>1||Math.abs(p.x)>.94||Math.abs(p.y)>.94){item.element.style.display='none';continue;}item.element.style.display='block';item.element.style.left=((p.x*.5+.5)*innerWidth)+'px';item.element.style.top=((-p.y*.5+.5)*innerHeight)+'px';}}\n",
        "single camera-aware index contour labels",
    )

    text = replace_once(
        text,
        "  function buildWindAnchors(){windAnchors=[];const w=weather.meta.width,h=weather.meta.height,b=weather.meta.bounds_m,res=weather.meta.render_resolution_m;for(let gy=1;gy<=11;gy++){const row=Math.min(h-1,Math.round(gy*h/12));for(let gx=1;gx<=14;gx++){const col=Math.min(w-1,Math.round(gx*w/15)),i=row*w+col;windAnchors.push({index:i,x:b.west+(col+.5)*res-centreX,z:centreY-(b.north-(row+.5)*res),y:weather.elevation[i]-minE+28,speed:0,direction:0,phase:deterministicNoise(row,col)});}}windAnchors=windAnchors.slice(0,160);}\n",
        "  function terrainHeightAt(x,z){const fx=clamp01(x/widthM+.5)*(meta.width-1),fz=clamp01(z/heightM+.5)*(meta.height-1),c0=Math.floor(fx),r0=Math.floor(fz),c1=Math.min(meta.width-1,c0+1),r1=Math.min(meta.height-1,r0+1),tx=fx-c0,tz=fz-r0;const e00=elevation[r0*meta.width+c0]-minE,e10=elevation[r0*meta.width+c1]-minE,e01=elevation[r1*meta.width+c0]-minE,e11=elevation[r1*meta.width+c1]-minE;return(e00+(e10-e00)*tx)*(1-tz)+(e01+(e11-e01)*tx)*tz;}\n"
        "  function buildWindAnchors(){windAnchors=[];const w=weather.meta.width,h=weather.meta.height,b=weather.meta.bounds_m,res=weather.meta.render_resolution_m;for(let gy=1;gy<=11;gy++){const row=Math.min(h-1,Math.round(gy*h/12));for(let gx=1;gx<=14;gx++){const col=Math.min(w-1,Math.round(gx*w/15)),i=row*w+col;windAnchors.push({index:i,x:b.west+(col+.5)*res-centreX,z:centreY-(b.north-(row+.5)*res),speed:0,direction:0,phase:deterministicNoise(row,col)});}}windAnchors=windAnchors.slice(0,WIND_COUNT);}\n",
        "terrain-following wind anchors",
    )

    text = replace_once(
        text,
        "  function animateWind(dt){if(!windLines.visible||!windAnchors.length)return;const pos=windGeometry.getAttribute('position').array,vertical=Number(exaggeration.value);let p=0;for(const a of windAnchors){const to=(a.direction+180)*Math.PI/180,dx=Math.sin(to),dz=-Math.cos(to),speed=Math.max(0,a.speed);a.phase=(a.phase+dt*(.09+speed*.018))%1;const track=260+speed*32,seg=52+speed*9,c=(a.phase-.5)*track;for(const v of[c-seg*.5,c+seg*.5]){pos[p++]=a.x+dx*v;pos[p++]=a.y*vertical;pos[p++]=a.z+dz*v;}}for(;p<pos.length;p++)pos[p]=0;windGeometry.setDrawRange(0,windAnchors.length*2);windGeometry.getAttribute('position').needsUpdate=true;}\n",
        "  function animateWind(dt){if(!windLines.visible||!windAnchors.length)return;const pos=windGeometry.getAttribute('position').array,vertical=Number(exaggeration.value);let p=0,drawn=0;for(const a of windAnchors){const to=(a.direction+180)*Math.PI/180,dx=Math.sin(to),dz=-Math.cos(to),speed=Math.max(0,a.speed);a.phase=(a.phase+dt*(.055+speed*.012))%1;const fullLength=180+speed*22,track=300+speed*36,growEnd=.28,growth=Math.min(1,a.phase/growEnd),travel=a.phase<=growEnd?0:((a.phase-growEnd)/(1-growEnd))*track,tail=-track*.46+travel,currentLength=fullLength*(growth*growth*(3-2*growth));for(let s=0;s<WIND_SEGMENTS;s++){const f0=s/WIND_SEGMENTS,f1=(s+1)/WIND_SEGMENTS;if(f0>growth)break;const d0=tail+Math.min(f0,growth)*currentLength/Math.max(growth,.0001),d1=tail+Math.min(f1,growth)*currentLength/Math.max(growth,.0001),x0=a.x+dx*d0,z0=a.z+dz*d0,x1=a.x+dx*d1,z1=a.z+dz*d1;pos[p++]=x0;pos[p++]=(terrainHeightAt(x0,z0)+22)*vertical;pos[p++]=z0;pos[p++]=x1;pos[p++]=(terrainHeightAt(x1,z1)+22)*vertical;pos[p++]=z1;drawn+=2;}}for(;p<pos.length;p++)pos[p]=0;windGeometry.setDrawRange(0,drawn);windGeometry.getAttribute('position').needsUpdate=true;}\n",
        "growing terrain-conforming wind streamlines",
    )

    text = replace_once(
        text,
        "controls.update();updateFeatureLabels();updateCompass();animateWind(dt);renderer.render(scene,camera);",
        "controls.update();updateFeatureLabels();updateContourLabels(dt);updateCompass();animateWind(dt);renderer.render(scene,camera);",
        "dynamic contour label and wind frame update",
    )

    path.write_text(text, encoding="utf-8")
    print("Applied camera-aware single contour labels and growing terrain-conforming wind streamlines")


if __name__ == "__main__":
    run()
