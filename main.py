import pathlib

import moderngl as mgl
import moderngl_window as mglw
import numpy as np
import tween

render_vert = '''
#version 460
in vec2 position;
void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
}
'''

class LavaLamp(mglw.WindowConfig):
    gl_version = 4,6
    title = "Lava Lamp"
    window_size = 800, 800
    aspect_ratio = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_count = 5
        self.texture0 = self.make_tex()
        self.texture1 = self.make_tex()

        version = '#version 460'
        noise_lib = pathlib.Path('noise.glsl').read_text()
        frag_shader = pathlib.Path('render.frag').read_text()

        self.render_program = self.ctx.program(vertex_shader=render_vert, fragment_shader='\n'.join([version, noise_lib, frag_shader]))
        self.render_buffer = self.ctx.buffer(np.array([[-1, -1], [3, -1], [-1, 3]], dtype=np.float32))
        self.render_vao = self.ctx.vertex_array(self.render_program, self.render_buffer, 'position')

        self.shape_t = np.random.random() * 10000
        self.color_t = 1
        self.texture0.write(self.random_colors())
        self.texture1.write(self.random_colors())

    def make_tex(self):
        texture = self.ctx.texture(size=(1, self.color_count), components=4, dtype='f4')
        texture.filter = mgl.NEAREST, mgl.NEAREST
        texture.repeat_x = False
        texture.repeat_y = False
        return texture

    def random_colors(self):
        return np.random.random((self.color_count, 4)).astype(np.float32)

    def transition(self):
        self.color_t = 0
        tween_time = 1.5
        ease = 'easeInOutSine'
        tween.to(self, 'color_t', 1, tween_time, ease)
        tween.to(self, 'shape_t', self.shape_t + 50, tween_time, ease)
        self.texture0, self.texture1 = self.texture1, self.texture0
        self.texture1.write(self.random_colors())

    def render(self, time: float, frame_time: float):
        self.shape_t += frame_time
        tween.update(frame_time)
        self.render_program['time'] = self.shape_t
        self.render_program['color_t'] = self.color_t
        self.render_program['colors0'] = 0
        self.render_program['colors1'] = 1
        self.texture0.use(0)
        self.texture1.use(1)
        self.render_vao.render()

    def key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            self.transition()

if __name__ == '__main__':
    mglw.run_window_config(LavaLamp)
