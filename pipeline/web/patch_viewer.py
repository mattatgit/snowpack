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
        "body { margin: 0; background: #8ec7ef; color: #eceeee; overflow: hidden; }",
        "body { margin: 0; background: #5599d6; color: #eceeee; overflow: hidden; }",
        "page background",
    )

    text = replace_once(
        text,
        "    input[type=\"range\"] { accent-color:#e2e7e8; }\n",
        "    input[type=\"range\"] { accent-color:#e2e7e8; }\n"
        "    .vertical-control { display:grid; grid-template-columns:1fr auto; gap:8px; align-items:center; }\n"
        "    .vertical-slider { position:relative; padding-bottom:13px; }\n"
        "    .vertical-slider input { display:block; }\n"
        "    .vertical-default-marker { position:absolute; left:25%; top:17px; width:1px; height:7px; background:rgba(255,255,255,.72); pointer-events:none; }\n"
        "    .vertical-default-label { position:absolute; left:25%; top:24px; transform:translateX(-50%); color:#949b9e; font-size:9px; white-space:nowrap; pointer-events:none; }\n"
        "    .vertical-label { display:flex; align-items:baseline; gap:5px; }\n"
        "    .vertical-value { color:#9fa6a8; font-size:10px; font-variant-numeric:tabular-nums; }\n"
        "    .reset-button { width:auto; min-width:48px; height:27px; padding:0 8px; border:1px solid #454b4e; border-radius:6px; background:#202527; color:#c8cdcf; font:inherit; font-size:10px; cursor:pointer; }\n"
        "    .reset-button:hover { background:#2a3032; color:#fff; }\n",
        "vertical control CSS",
    )

    text = replace_once(
        text,
        "    <label class=\"row\"><span>Vertical</span><input id=\"exaggeration\" type=\"range\" min=\"0.6\" max=\"2.2\" value=\"1.1\" step=\"0.05\"></label>",
        "    <div class=\"row\"><span class=\"vertical-label\">Vertical <span id=\"verticalValue\" class=\"vertical-value\">1.0×</span></span><div class=\"vertical-control\"><div class=\"vertical-slider\"><input id=\"exaggeration\" type=\"range\" min=\"0.6\" max=\"2.2\" value=\"1.0\" step=\"0.05\"><span class=\"vertical-default-marker\"></span><span class=\"vertical-default-label\">1× default</span></div><button id=\"verticalReset\" class=\"reset-button\" type=\"button\">Reset</button></div></div>",
        "vertical control markup",
    )

    text = replace_once(
        text,
        "const BUILD_ID='snow-heatmap-5m-20261009-1';",
        "const BUILD_ID='snow-heatmap-5m-20261009-2';",
        "build id",
    )

    text = replace_once(
        text,
        "const exaggeration=document.querySelector('#exaggeration');\n",
        "const exaggeration=document.querySelector('#exaggeration');\n"
        "const verticalValue=document.querySelector('#verticalValue');\n"
        "const verticalReset=document.querySelector('#verticalReset');\n",
        "vertical JS controls",
    )

    text = replace_once(
        text,
        "renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;app.prepend(renderer.domElement);",
        "renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.96;app.prepend(renderer.domElement);",
        "renderer exposure",
    )

    text = replace_once(
        text,
        "  const sky=new Sky();sky.scale.setScalar(450000);scene.add(sky);\n"
        "  const skyU=sky.material.uniforms;skyU.turbidity.value=1.8;skyU.rayleigh.value=1.8;skyU.mieCoefficient.value=.0025;skyU.mieDirectionalG.value=.82;\n"
        "  const fixedSun=new THREE.Vector3();const phi=THREE.MathUtils.degToRad(62),theta=THREE.MathUtils.degToRad(205);fixedSun.setFromSphericalCoords(1,phi,theta);skyU.sunPosition.value.copy(fixedSun);\n"
        "  scene.fog=new THREE.Fog(0xa7cfe6,sceneSpan*2.1,sceneSpan*5.2);",
        "  const sky=new Sky();sky.scale.setScalar(450000);scene.add(sky);\n"
        "  const skyU=sky.material.uniforms;skyU.turbidity.value=.65;skyU.rayleigh.value=4.0;skyU.mieCoefficient.value=.00055;skyU.mieDirectionalG.value=.72;\n"
        "  const fixedSun=new THREE.Vector3();const phi=THREE.MathUtils.degToRad(34),theta=THREE.MathUtils.degToRad(205);fixedSun.setFromSphericalCoords(1,phi,theta);skyU.sunPosition.value.copy(fixedSun);\n"
        "  scene.fog=new THREE.Fog(0x79b3df,sceneSpan*2.25,sceneSpan*5.4);",
        "bluebird sky",
    )

    text = replace_once(
        text,
        "    void main(){float x=texture2D(dataMap,vUv).r;if(x<.002)discard;vec3 c=mode<.5?snowPalette(x):(mode<1.5?tempPalette(x):(mode<2.5?windPalette(x):solarPalette(x)));float alpha=mode<.5?mix(.24,.84,sqrt(x)):mix(.18,.72,x);gl_FragColor=vec4(c,alpha);}`});",
        "    void main(){float x=texture2D(dataMap,vUv).r;if(x<.008)discard;vec3 c=mode<.5?snowPalette(x):(mode<1.5?tempPalette(x):(mode<2.5?windPalette(x):solarPalette(x)));float alpha=mode<.5?mix(.05,.46,pow(x,.70)):mix(.18,.72,x);gl_FragColor=vec4(c,alpha);}`});",
        "snow overlay opacity",
    )

    text = replace_once(
        text,
        "  function updateVertical(){const v=Number(exaggeration.value);terrainMesh.scale.y=v;overlayMesh.scale.y=v;if(treeMesh)treeMesh.scale.y=v;}\n"
        "  treesToggle.addEventListener('change',()=>{if(treeMesh)treeMesh.visible=treesToggle.checked;});exaggeration.addEventListener('input',updateVertical);layerSelect.addEventListener('change',()=>void updateLayer());snowWindow.addEventListener('change',()=>{accumCache.clear();if(layerSelect.value==='snow')void renderDynamic();});timeSlider.addEventListener('input',()=>{if(weather&&dynamicLayers.has(layerSelect.value))void renderDynamic();});updateVertical();",
        "  function updateVertical(){const v=Number(exaggeration.value);terrainMesh.scale.y=v;overlayMesh.scale.y=v;if(treeMesh)treeMesh.scale.y=v;verticalValue.textContent=v.toFixed(2).replace(/0+$/,'').replace(/\\.$/,'')+'×';}\n"
        "  treesToggle.addEventListener('change',()=>{if(treeMesh)treeMesh.visible=treesToggle.checked;});exaggeration.addEventListener('input',updateVertical);verticalReset.addEventListener('click',()=>{exaggeration.value='1.0';updateVertical();});layerSelect.addEventListener('change',()=>void updateLayer());snowWindow.addEventListener('change',()=>{accumCache.clear();if(layerSelect.value==='snow')void renderDynamic();});timeSlider.addEventListener('input',()=>{if(weather&&dynamicLayers.has(layerSelect.value))void renderDynamic();});updateVertical();",
        "vertical reset behaviour",
    )

    path.write_text(text, encoding="utf-8")
    print("Applied viewer presentation tweaks: bluer sky, translucent snow overlay, vertical reset")


if __name__ == "__main__":
    run()
