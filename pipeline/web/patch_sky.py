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
        "import { Sky } from 'three/addons/objects/Sky.js';\n",
        "",
        "Sky addon import",
    )

    text = replace_once(
        text,
        "const BUILD_ID='snow-heatmap-5m-20261009-2';",
        "const BUILD_ID='snow-heatmap-5m-20261009-3';",
        "build id",
    )

    text = replace_once(
        text,
        "    .panel { position:absolute; left:18px; top:18px; z-index:5; width:min(410px,calc(100vw - 36px)); padding:14px 15px; border:1px solid rgba(255,255,255,.18); border-radius:12px; background:rgba(18,22,24,.88); backdrop-filter:blur(11px); }\n",
        "    .panel { position:absolute; left:18px; top:18px; z-index:5; width:min(410px,calc(100vw - 36px)); padding:14px 15px; border:1px solid rgba(255,255,255,.18); border-radius:12px; background:rgba(18,22,24,.88); backdrop-filter:blur(11px); transition:width .18s ease,padding .18s ease; }\n"
        "    .panel-header { display:flex; align-items:center; justify-content:space-between; gap:12px; cursor:pointer; user-select:none; -webkit-tap-highlight-color:transparent; }\n"
        "    .panel-header h1 { flex:1; }\n"
        "    .panel-toggle { display:none; width:34px; height:30px; flex:0 0 auto; border:1px solid rgba(255,255,255,.16); border-radius:7px; background:rgba(255,255,255,.06); color:#eef2f3; font:inherit; font-size:16px; line-height:1; cursor:pointer; }\n"
        "    .panel-toggle::before { content:'−'; }\n"
        "    .panel.collapsed .panel-toggle::before { content:'+'; }\n"
        "    .panel.collapsed .panel-body { display:none; }\n",
        "accordion CSS",
    )

    text = replace_once(
        text,
        "    @media (max-width:620px) {\n      .panel { top:10px; left:10px; width:calc(100vw - 20px); }\n      .row { grid-template-columns:84px 1fr; }\n      #timeLabel { margin-left:94px; }\n      #compass { right:10px; bottom:10px; top:auto; width:72px; height:72px; }\n    }",
        "    @media (max-width:620px) {\n"
        "      .panel { top:10px; left:10px; width:calc(100vw - 20px); max-height:calc(100vh - 20px); overflow-y:auto; padding:11px 12px; }\n"
        "      .panel-toggle { display:block; }\n"
        "      .panel.collapsed { width:min(220px,calc(100vw - 20px)); overflow:hidden; padding:8px 10px; }\n"
        "      .panel.collapsed .panel-header { min-height:30px; }\n"
        "      .panel.collapsed h1 { margin:0; font-size:14px; }\n"
        "      .row { grid-template-columns:84px 1fr; }\n"
        "      #timeLabel { margin-left:94px; }\n"
        "      #compass { right:10px; bottom:10px; top:auto; width:72px; height:72px; }\n"
        "    }",
        "mobile accordion CSS",
    )

    text = replace_once(
        text,
        "  <div class=\"panel\">\n    <h1>Furanodake</h1>\n    <p class=\"sub\">5 m terrain + historical weather experiment. Drag to rotate, scroll/pinch to zoom, right-drag to pan.</p>",
        "  <div id=\"controlPanel\" class=\"panel\">\n"
        "    <div id=\"panelHeader\" class=\"panel-header\" role=\"button\" tabindex=\"0\" aria-expanded=\"true\" aria-controls=\"panelBody\">\n"
        "      <h1>Furanodake</h1>\n"
        "      <button id=\"panelToggle\" class=\"panel-toggle\" type=\"button\" aria-label=\"Collapse controls\"></button>\n"
        "    </div>\n"
        "    <div id=\"panelBody\" class=\"panel-body\">\n"
        "    <p class=\"sub\">5 m terrain + historical weather experiment. Drag to rotate, scroll/pinch to zoom, right-drag to pan.</p>",
        "accordion markup start",
    )

    text = replace_once(
        text,
        "    <div id=\"solarNotice\" class=\"notice\">Solar loading is modelled terrain exposure. The bluebird sky is deliberately cosmetic and does not represent historical weather.</div>\n  </div>\n  <div id=\"attribution\" class=\"attribution\"></div>",
        "    <div id=\"solarNotice\" class=\"notice\">Solar loading is modelled terrain exposure. The bluebird sky is deliberately cosmetic and does not represent historical weather.</div>\n"
        "    </div>\n"
        "  </div>\n"
        "  <div id=\"attribution\" class=\"attribution\"></div>",
        "accordion markup end",
    )

    text = replace_once(
        text,
        "const app=document.querySelector('#app');\nconst status=document.querySelector('#status');\n",
        "const app=document.querySelector('#app');\n"
        "const controlPanel=document.querySelector('#controlPanel');\n"
        "const panelHeader=document.querySelector('#panelHeader');\n"
        "const panelToggle=document.querySelector('#panelToggle');\n"
        "const status=document.querySelector('#status');\n",
        "accordion JS controls",
    )

    text = replace_once(
        text,
        "function cardinal(deg){if(!Number.isFinite(deg))return'calm/variable';const n=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];return n[Math.round(deg/22.5)%16];}\n",
        "function cardinal(deg){if(!Number.isFinite(deg))return'calm/variable';const n=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];return n[Math.round(deg/22.5)%16];}\n"
        "function setPanelCollapsed(collapsed){controlPanel.classList.toggle('collapsed',collapsed);panelHeader.setAttribute('aria-expanded',String(!collapsed));panelToggle.setAttribute('aria-label',collapsed?'Expand controls':'Collapse controls');}\n"
        "function togglePanel(){setPanelCollapsed(!controlPanel.classList.contains('collapsed'));}\n"
        "panelHeader.addEventListener('click',togglePanel);\n"
        "panelHeader.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();togglePanel();}});\n"
        "panelToggle.addEventListener('click',event=>event.stopPropagation());\n"
        "panelToggle.addEventListener('click',togglePanel);\n",
        "accordion behaviour",
    )

    text = replace_once(
        text,
        "  const sky=new Sky();sky.scale.setScalar(450000);scene.add(sky);\n"
        "  const skyU=sky.material.uniforms;skyU.turbidity.value=.65;skyU.rayleigh.value=4.0;skyU.mieCoefficient.value=.00055;skyU.mieDirectionalG.value=.72;\n"
        "  const fixedSun=new THREE.Vector3();const phi=THREE.MathUtils.degToRad(34),theta=THREE.MathUtils.degToRad(205);fixedSun.setFromSphericalCoords(1,phi,theta);skyU.sunPosition.value.copy(fixedSun);\n"
        "  scene.fog=new THREE.Fog(0x79b3df,sceneSpan*2.25,sceneSpan*5.4);",
        "  // Deliberately cosmetic bluebird sky: a controlled gradient rather than\n"
        "  // an atmospheric model, so the mountain always has a readable blue backdrop.\n"
        "  const skyGeometry=new THREE.SphereGeometry(sceneSpan*20,48,24);\n"
        "  const skyMaterial=new THREE.ShaderMaterial({\n"
        "    side:THREE.BackSide,depthWrite:false,fog:false,\n"
        "    uniforms:{\n"
        "      zenith:{value:new THREE.Color(0x2877c7)},\n"
        "      horizon:{value:new THREE.Color(0x79b9e5)},\n"
        "      lower:{value:new THREE.Color(0xa8d0ea)}\n"
        "    },\n"
        "    vertexShader:`varying float vSkyY; void main(){vSkyY=normalize(position).y;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,\n"
        "    fragmentShader:`uniform vec3 zenith;uniform vec3 horizon;uniform vec3 lower;varying float vSkyY;void main(){float upper=smoothstep(-.06,.78,vSkyY);vec3 c=mix(horizon,zenith,upper);if(vSkyY<-.06)c=mix(lower,horizon,smoothstep(-.55,-.06,vSkyY));gl_FragColor=vec4(c,1.0);}`\n"
        "  });\n"
        "  skyMaterial.toneMapped=false;\n"
        "  const skyDome=new THREE.Mesh(skyGeometry,skyMaterial);scene.add(skyDome);\n"
        "  scene.fog=new THREE.Fog(0x79b9e5,sceneSpan*2.25,sceneSpan*5.4);",
        "controlled sky dome",
    )

    text = replace_once(
        text,
        "    <div id=\"snowNotice\" class=\"notice\">The snow overlay is modelled snowfall water equivalent, accumulated over a fixed window. The colour scale stays fixed while you scrub time; it does not imply 50 m observational accuracy.</div>",
        "    <div id=\"snowNotice\" class=\"notice\">The snow overlay is modelled snowfall water equivalent, accumulated over a fixed window. Changes while scrubbing show the evolution of the modelled accumulation field—not an observed direction of snowfall travel. The colour scale stays fixed; it does not imply 50 m observational accuracy.</div>",
        "snow motion caveat",
    )

    path.write_text(text, encoding="utf-8")
    print("Applied controlled blue gradient sky, mobile accordion, and snow-motion caveat")


if __name__ == "__main__":
    run()
