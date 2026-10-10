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
        "const BUILD_ID='snow-heatmap-5m-20261010-16';",
        "const BUILD_ID='snow-heatmap-5m-20261010-17';",
        "build id",
    )

    text = replace_once(
        text,
        "vertexShader:`varying vec2 vUv; void main(){vUv=uv;vec3 p=position;p.y+=1.2;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);}`",
        "vertexShader:`varying vec2 vUv; varying float vShade; void main(){vUv=uv;vec3 n=normalize(normalMatrix*normal);vec3 lightDir=normalize(vec3(-.45,.82,.35));vShade=.78+.22*max(dot(n,lightDir),0.0);vec3 p=position;p.y+=1.2;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);}`",
        "snow surface relief lighting",
    )

    text = replace_once(
        text,
        "uniform sampler2D dataMap; uniform sampler2D coverageMap; uniform float mode; uniform float maskFine; varying vec2 vUv;",
        "uniform sampler2D dataMap; uniform sampler2D coverageMap; uniform float mode; uniform float maskFine; varying vec2 vUv; varying float vShade;",
        "snow fragment relief varying",
    )

    text = replace_once(
        text,
        "vec3 c=mode<.5?snowPalette(x):(mode<1.5?tempPalette(x):(mode<2.5?windPalette(x):solarPalette(x)));float alpha=mode<.5?mix(.05,.46,pow(x,.70)):mix(.18,.72,x);gl_FragColor=vec4(c,alpha);",
        "vec3 c=mode<.5?snowPalette(x):(mode<1.5?tempPalette(x):(mode<2.5?windPalette(x):solarPalette(x)));if(mode<.5)c*=vShade;float alpha=mode<.5?mix(.30,.96,smoothstep(.015,.24,x)):mix(.18,.72,x);gl_FragColor=vec4(c,alpha);",
        "snow opacity curve",
    )

    path.write_text(text, encoding="utf-8")
    print("Made accumulated snow visually dominant while retaining terrain relief lighting")


if __name__ == "__main__":
    run()
