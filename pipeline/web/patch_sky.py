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
    print("Applied controlled blue gradient sky and snow-motion caveat")


if __name__ == "__main__":
    run()
