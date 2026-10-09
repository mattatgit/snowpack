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
        "const BUILD_ID='snow-heatmap-5m-20261009-8';",
        "const BUILD_ID='snow-heatmap-5m-20261009-9';",
        "build id",
    )

    text = replace_once(
        text,
        "  const WIND_SEGMENTS=16,WIND_COUNT=160;const windPositions=new Float32Array(WIND_COUNT*WIND_SEGMENTS*2*3),windGeometry=new THREE.BufferGeometry();windGeometry.setAttribute('position',new THREE.BufferAttribute(windPositions,3));const windLines=new THREE.LineSegments(windGeometry,new THREE.LineBasicMaterial({color:0xff6157,transparent:true,opacity:.88}));windLines.visible=false;scene.add(windLines);",
        "  const WIND_SEGMENTS=16,WIND_COUNT=160,WIND_ARROW_SEGMENTS=2;const windPositions=new Float32Array(WIND_COUNT*(WIND_SEGMENTS+WIND_ARROW_SEGMENTS)*2*3),windGeometry=new THREE.BufferGeometry();windGeometry.setAttribute('position',new THREE.BufferAttribute(windPositions,3));const windLines=new THREE.LineSegments(windGeometry,new THREE.LineBasicMaterial({color:0xff786f,transparent:true,opacity:.96}));windLines.visible=false;scene.add(windLines);",
        "brighter wind lines with arrow capacity",
    )

    old_animate = (
        "  function animateWind(dt){if(!windLines.visible||!windAnchors.length)return;const pos=windGeometry.getAttribute('position').array,vertical=Number(exaggeration.value);let p=0,drawn=0;for(const a of windAnchors){const to=(a.direction+180)*Math.PI/180,dx=Math.sin(to),dz=-Math.cos(to),speed=Math.max(0,a.speed);a.phase=(a.phase+dt*(.055+speed*.012))%1;const fullLength=180+speed*22,track=300+speed*36,growEnd=.28,growth=Math.min(1,a.phase/growEnd),travel=a.phase<=growEnd?0:((a.phase-growEnd)/(1-growEnd))*track,tail=-track*.46+travel,currentLength=fullLength*(growth*growth*(3-2*growth));for(let s=0;s<WIND_SEGMENTS;s++){const f0=s/WIND_SEGMENTS,f1=(s+1)/WIND_SEGMENTS;if(f0>growth)break;const d0=tail+Math.min(f0,growth)*currentLength/Math.max(growth,.0001),d1=tail+Math.min(f1,growth)*currentLength/Math.max(growth,.0001),x0=a.x+dx*d0,z0=a.z+dz*d0,x1=a.x+dx*d1,z1=a.z+dz*d1;pos[p++]=x0;pos[p++]=(terrainHeightAt(x0,z0)+22)*vertical;pos[p++]=z0;pos[p++]=x1;pos[p++]=(terrainHeightAt(x1,z1)+22)*vertical;pos[p++]=z1;drawn+=2;}}for(;p<pos.length;p++)pos[p]=0;windGeometry.setDrawRange(0,drawn);windGeometry.getAttribute('position').needsUpdate=true;}\n"
    )

    new_animate = (
        "  function airflowHeightAt(x,z,dx,dz){const s=34,h0=terrainHeightAt(x,z),h1a=terrainHeightAt(x-dx*s,z-dz*s),h1b=terrainHeightAt(x+dx*s,z+dz*s),h2a=terrainHeightAt(x-dx*s*2,z-dz*s*2),h2b=terrainHeightAt(x+dx*s*2,z+dz*s*2),smooth=(h0*4+(h1a+h1b)*2+h2a+h2b)/10,broad=(h0+h1a+h1b+h2a+h2b)/5;return Math.max(h0+18,smooth+30,broad+26);}\n"
        "  function animateWind(dt){if(!windLines.visible||!windAnchors.length)return;const pos=windGeometry.getAttribute('position').array,vertical=Number(exaggeration.value);let p=0,drawn=0;for(const a of windAnchors){const to=(a.direction+180)*Math.PI/180,dx=Math.sin(to),dz=-Math.cos(to),px=-dz,pz=dx,speed=Math.max(0,a.speed);a.phase=(a.phase+dt*(.055+speed*.012))%1;const fullLength=190+speed*24,track=320+speed*38,growEnd=.30,growth=Math.min(1,a.phase/growEnd),travel=a.phase<=growEnd?0:((a.phase-growEnd)/(1-growEnd))*track,tail=-track*.46+travel,ease=growth*growth*(3-2*growth),currentLength=fullLength*ease,denom=Math.max(growth,.0001);let tipX=a.x,tipZ=a.z,tipY=(airflowHeightAt(a.x,a.z,dx,dz))*vertical,active=0;for(let s=0;s<WIND_SEGMENTS;s++){const f0=s/WIND_SEGMENTS,f1=(s+1)/WIND_SEGMENTS;if(f0>growth)break;const d0=tail+Math.min(f0,growth)*currentLength/denom,d1=tail+Math.min(f1,growth)*currentLength/denom,x0=a.x+dx*d0,z0=a.z+dz*d0,x1=a.x+dx*d1,z1=a.z+dz*d1,y0=airflowHeightAt(x0,z0,dx,dz)*vertical,y1=airflowHeightAt(x1,z1,dx,dz)*vertical;pos[p++]=x0;pos[p++]=y0;pos[p++]=z0;pos[p++]=x1;pos[p++]=y1;pos[p++]=z1;tipX=x1;tipY=y1;tipZ=z1;drawn+=2;active++;}if(active>=3){const arrowBack=22+Math.min(12,speed*1.2),arrowSide=arrowBack*.52,baseX=tipX-dx*arrowBack,baseZ=tipZ-dz*arrowBack,leftX=baseX+px*arrowSide,leftZ=baseZ+pz*arrowSide,rightX=baseX-px*arrowSide,rightZ=baseZ-pz*arrowSide,leftY=airflowHeightAt(leftX,leftZ,dx,dz)*vertical,rightY=airflowHeightAt(rightX,rightZ,dx,dz)*vertical;pos[p++]=tipX;pos[p++]=tipY;pos[p++]=tipZ;pos[p++]=leftX;pos[p++]=leftY;pos[p++]=leftZ;pos[p++]=tipX;pos[p++]=tipY;pos[p++]=tipZ;pos[p++]=rightX;pos[p++]=rightY;pos[p++]=rightZ;drawn+=4;}}for(;p<pos.length;p++)pos[p]=0;windGeometry.setDrawRange(0,drawn);windGeometry.getAttribute('position').needsUpdate=true;}\n"
    )

    text = replace_once(text, old_animate, new_animate, "smoothed airflow and arrowheads")

    path.write_text(text, encoding="utf-8")
    print("Applied smoothed hovering airflow streamlines, arrowheads, and brighter wind colour")


if __name__ == "__main__":
    run()
