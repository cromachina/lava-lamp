uniform float time;
uniform float color_t;
uniform sampler2D colors0;
uniform sampler2D colors1;

out vec4 frag_color;

vec2 grad(vec3 v, float eps = 1)
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
        p += grad(vec3(p / i, t));
    }
    float v = snoise(vec3(p, t)) + 1.0 / 2.0;
    vec4 c0 = texture(colors0, vec2(0, v));
    vec4 c1 = texture(colors1, vec2(0, v));
    frag_color = mix(c0, c1, color_t);
}
