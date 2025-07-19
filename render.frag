uniform float time;
uniform sampler2D colors;

out vec4 frag_color;

vec2 grad(vec3 v, float eps)
{
    float vx = snoise(v + vec3(eps, 0, 0));
    float vy = snoise(v + vec3(0, eps, 0));
    float nv = snoise(v);
    return vec2(nv - vx, nv - vy);
}

void main()
{
    float t = time * 0.01;
    vec2 p = (gl_FragCoord.xy) / 200.0;
    for (int i = 2; i <= 4; i++)
    {
        p += grad(vec3(p / i, t), 1);
    }
    float v = snoise(vec3(p, t)) + 1.0 / 2.0;
    frag_color = texture(colors, vec2(0, v));
}
