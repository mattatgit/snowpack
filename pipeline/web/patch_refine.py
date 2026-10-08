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
        "const BUILD_ID='snow-heatmap-5m-20261009-6';",
        "build id",
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
        "const windLines=new THREE.LineSegments(windGeometry,new THREE.LineBasicMaterial({color:0xf3fbff,transparent:true,opacity:.62}));",
        "const windLines=new THREE.LineSegments(windGeometry,new THREE.LineBasicMaterial({color:0xff6157,transparent:true,opacity:.88}));",
        "red wind lines",
    )

    text = replace_once(
        text,
        "  function buildWindAnchors(){windAnchors=[];const w=weather.meta.width,h=weather.meta.height,b=weather.meta.bounds_m,res=weather.meta.render_resolution_m;for(let gy=1;gy<=11;gy++){const row=Math.min(h-1,Math.round(gy*h/12));for(let gx=1;gx<=14;gx++){const col=Math.min(w-1,Math.round(gx*w/15)),i=row*w+col;windAnchors.push({index:i,x:b.west+(col+.5)*res-centreX,z:centreY-(b.north-(row+.5)*res),y:weather.elevation[i]-minE+28,speed:0,direction:0,phase:deterministicNoise(row,col)});}}windAnchors=windAnchors.slice(0,160);}\n",
        "  function terrainHeightAt(x,z){const fx=clamp01(x/widthM+.5)*(meta.width-1),fz=clamp01(z/heightM+.5)*(meta.height-1),c0=Math.floor(fx),r0=Math.floor(fz),c1=Math.min(meta.width-1,c0+1),r1=Math.min(meta.height-1,r0+1),tx=fx-c0,tz=fz-r0;const e00=elevation[r0*meta.width+c0]-minE,e10=elevation[r0*meta.width+c1]-minE,e01=elevation[r1*meta.width+c0]-minE,e11=elevation[r1*meta.width+c1]-minE;return(e00+(e10-e00)*tx)*(1-tz)+(e01+(e11-e01)*tx)*tz;}\n"
        "  function buildWindAnchors(){windAnchors=[];const w=weather.meta.width,h=weather.meta.height,b=weather.meta.bounds_m,res=weather.meta.render_resolution_m;for(let gy=1;gy<=11;gy++){const row=Math.min(h-1,Math.round(gy*h/12));for(let gx=1;gx<=14;gx++){const col=Math.min(w-1,Math.round(gx*w/15)),i=row*w+col;windAnchors.push({index:i,x:b.west+(col+.5)*res-centreX,z:centreY-(b.north-(row+.5)*res),speed:0,direction:0,phase:deterministicNoise(row,col)});}}windAnchors=windAnchors.slice(0,160);}\n",
        "terrain-following wind anchors",
    )

    text = replace_once(
        text,
        "  function animateWind(dt){if(!windLines.visible||!windAnchors.length)return;const pos=windGeometry.getAttribute('position').array,vertical=Number(exaggeration.value);let p=0;for(const a of windAnchors){const to=(a.direction+180)*Math.PI/180,dx=Math.sin(to),dz=-Math.cos(to),speed=Math.max(0,a.speed);a.phase=(a.phase+dt*(.09+speed*.018))%1;const track=260+speed*32,seg=52+speed*9,c=(a.phase-.5)*track;for(const v of[c-seg*.5,c+seg*.5]){pos[p++]=a.x+dx*v;pos[p++]=a.y*vertical;pos[p++]=a.z+dz*v;}}for(;p<pos.length;p++)pos[p]=0;windGeometry.setDrawRange(0,windAnchors.length*2);windGeometry.getAttribute('position').needsUpdate=true;}\n",
        "  function animateWind(dt){if(!windLines.visible||!windAnchors.length)return;const pos=windGeometry.getAttribute('position').array,vertical=Number(exaggeration.value);let p=0;for(const a of windAnchors){const to=(a.direction+180)*Math.PI/180,dx=Math.sin(to),dz=-Math.cos(to),speed=Math.max(0,a.speed);a.phase=(a.phase+dt*(.075+speed*.015))%1;const track=420+speed*48,seg=110+speed*14,c=(a.phase-.5)*track;for(const v of[c-seg*.5,c+seg*.5]){const x=a.x+dx*v,z=a.z+dz*v;pos[p++]=x;pos[p++]=(terrainHeightAt(x,z)+30)*vertical;pos[p++]=z;}}for(;p<pos.length;p++)pos[p]=0;windGeometry.setDrawRange(0,windAnchors.length*2);windGeometry.getAttribute('position').needsUpdate=true;}\n",
        "longer terrain-following wind animation",
    )

    path.write_text(text, encoding="utf-8")
    print("Applied thinner topo contours and longer red terrain-following wind animation")


if __name__ == "__main__":
    run()
