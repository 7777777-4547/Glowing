#version 150

#moj_import <fog.glsl>

uniform sampler2D Sampler0;

uniform vec4 ColorModulator;
uniform float FogStart;
uniform float FogEnd;
uniform vec4 FogColor;

in float vertexDistance;
in vec4 vertexColor;
in vec2 texCoord0;
in vec4 lightMapColor;

out vec4 fragColor;

void main() {
    vec4 color = textureLod(Sampler0, texCoord0, 0.0);
    if (color.a == 1.0) {
        color = texture(Sampler0, texCoord0) * ColorModulator * vertexColor;
        color = linear_fog(color, vertexDistance, FogStart, FogEnd, FogColor);
    } else {
        color *= lightMapColor / 4 + vec4(1.0, 1.0, 1.0, 0.0);
        float fogDifference = FogEnd - FogStart;
        vec4 newFogColor = mix(FogColor, color, fogDifference / 100.0);
        color = linear_fog(color, vertexDistance, FogStart, FogEnd, newFogColor);
        color.a = 1.0;
    }
    fragColor = color;
}
