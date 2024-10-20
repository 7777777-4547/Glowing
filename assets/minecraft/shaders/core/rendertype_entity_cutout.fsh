#version 150

#moj_import <fog.glsl>

uniform sampler2D Sampler0;

uniform vec4 ColorModulator;
uniform float FogStart;
uniform float FogEnd;
uniform vec4 FogColor;

in float vertexDistance;
in vec4 vertexColor;
in vec4 lightMapColor;
in vec4 overlayColor;
in vec2 texCoord0;

out vec4 fragColor;

void main() {
    vec4 color = texture(Sampler0, texCoord0);
    vec4 newColor;
    if (color.a < 0.1) {
        discard;
    }
    if (color.a == 1.0) {
        color *= vertexColor * ColorModulator;
        color.rgb = mix(overlayColor.rgb, color.rgb, overlayColor.a);
        color *= lightMapColor;
        newColor = linear_fog(color, vertexDistance, FogStart, FogEnd, FogColor);
    } else {
        color *= lightMapColor / 4 + vec4(1.0, 1.0, 1.0, 0.0);
        float fogDifference = FogEnd - FogStart;
        vec4 newFogColor = mix(FogColor, color, fogDifference / 100.0);
        newColor = linear_fog(color, vertexDistance, FogStart, FogEnd, newFogColor);
        newColor.a = 1.0;
    }
    fragColor = newColor;
}
