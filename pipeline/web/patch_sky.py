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
        "const BUILD_ID='snow-heatmap-5m-20261009-4';",
        "build id",
    )

    text = replace_once(
        text,
        "body { margin: 0; background: #5599d6; color: #eceeee; overflow: hidden; }",
        "body { margin: 0; background: #65a9dd; color: #eceeee; overflow: hidden; }",
        "body sky fallback",
    )

    text = replace_once(
        text,
        "    #app { position: relative; width: 100vw; height: 100vh; }",
        "    #app { position: relative; width: 100vw; height: 100vh; background:linear-gradient(to bottom,#2676c5 0%,#4f9ed8 48%,#9ac9e8 82%,#c0def0 100%); }",
        "CSS sky gradient",
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
        "  const renderer=new THREE.WebGLRenderer({antialias:true});",
        "  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});",
        "transparent renderer",
    )

    text = replace_once(
        text,
        "renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.96;app.prepend(renderer.domElement);",
        "renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.96;renderer.setClearColor(0x000000,0);app.prepend(renderer.domElement);",
        "transparent clear color",
    )

    text = replace_once(
        text,
        "  const sky=new Sky();sky.scale.setScalar(450000);scene.add(sky);\n"
        "  const skyU=sky.material.uniforms;skyU.turbidity.value=.65;skyU.rayleigh.value=4.0;skyU.mieCoefficient.value=.00055;skyU.mieDirectionalG.value=.72;\n"
        "  const fixedSun=new THREE.Vector3();const phi=THREE.MathUtils.degToRad(34),theta=THREE.MathUtils.degToRad(205);fixedSun.setFromSphericalCoords(1,phi,theta);skyU.sunPosition.value.copy(fixedSun);\n"
        "  scene.fog=new THREE.Fog(0x79b3df,sceneSpan*2.25,sceneSpan*5.4);",
        "  // The sky is CSS behind a transparent WebGL canvas for consistent Safari/Chromium rendering.\n"
        "  scene.background=null;\n"
        "  scene.fog=new THREE.Fog(0xa9cee8,sceneSpan*2.6,sceneSpan*5.8);",
        "CSS sky replacement",
    )

    text = replace_once(
        text,
        "  camera.position.set(-sceneSpan*.92,sceneSpan*.68,sceneSpan*.98);const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,(maxE-minE)*.34,0);",
        "  // Default view from north of the mountain, looking south across the main rideable faces.\n"
        "  camera.position.set(-sceneSpan*.12,sceneSpan*.66,-sceneSpan*1.08);const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,(maxE-minE)*.34,0);",
        "south-facing default view",
    )

    text = replace_once(
        text,
        "    <div id=\"snowNotice\" class=\"notice\">The snow overlay is modelled snowfall water equivalent, accumulated over a fixed window. The colour scale stays fixed while you scrub time; it does not imply 50 m observational accuracy.</div>",
        "    <div id=\"snowNotice\" class=\"notice\">The snow overlay is modelled snowfall water equivalent, accumulated over a fixed window. Changes while scrubbing show the evolution of the modelled accumulation field—not an observed direction of snowfall travel. The colour scale stays fixed; it does not imply 50 m observational accuracy.</div>",
        "snow motion caveat",
    )

    path.write_text(text, encoding="utf-8")
    print("Applied CSS blue sky, south-facing default view, mobile accordion, and snow-motion caveat")


if __name__ == "__main__":
    run()
