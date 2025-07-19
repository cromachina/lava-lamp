import pathlib
import colorsys
import random

import cv2
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

def uniform(prog, key, value):
    val = prog.get(key, None)
    if val is not None:
        val.value = value

def lerp(a, b, t):
    return (b - a) * t + a

class LavaLamp(mglw.WindowConfig):
    gl_version = 4,6
    title = "Lava Lamp"
    window_size = 800, 800
    aspect_ratio = None

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('--auto-transition', action='store_true', help='Automatically transition colors.')
        parser.add_argument('--frequency', type=float, default=60, help='How often a color transition occurs.')
        parser.add_argument('--time', type=float, default=5, help='How long it takes a color transition to finish.')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_count = 5
        self.texture = self.make_tex()
        self.current_color = self.random_colors()
        self.next_color = self.random_colors()

        version = '#version 460'
        noise_lib = pathlib.Path('noise.glsl').read_text()
        frag_shader = pathlib.Path('render.frag').read_text()

        self.render_program = self.ctx.program(vertex_shader=render_vert, fragment_shader='\n'.join([version, noise_lib, frag_shader]))
        self.render_buffer = self.ctx.buffer(np.array([[-1, -1], [3, -1], [-1, 3]], dtype=np.float32))
        self.render_vao = self.ctx.vertex_array(self.render_program, self.render_buffer, 'position')

        self.shape_t = np.random.random() * 10000
        self.shape_t_delta = 0
        self.color_t = 1
        self.texture.write(self.current_color)
        uniform(self.render_program, 'colors', 0)
        self.texture.use(0)
        if self.argv.auto_transition:
            self.auto_transition()

    def auto_transition(self):
        tween.to([0], 0, 0, self.argv.frequency, 'linear').on_complete(self.auto_transition)
        self.transition()

    def make_tex(self):
        texture = self.ctx.texture(size=(1, self.color_count), components=3, dtype='f4')
        texture.filter = mgl.NEAREST, mgl.NEAREST
        texture.repeat_x = False
        texture.repeat_y = False
        return texture

    def cvt_color(self, colors, conversion_type):
        return cv2.cvtColor(colors.reshape((1, self.color_count, 3)), conversion_type).reshape((self.color_count, 3))

    # Pastel looking on average.
    def random_colors_rgb(self):
        return np.random.random((self.color_count, 3)).astype(np.float32)

    def random_colors_hs_helper(self, hls):
        index = 1 if hls else 2
        cvt = cv2.COLOR_HLS2RGB if hls else cv2.COLOR_HSV2RGB
        colors = self.random_colors_rgb()
        colors[:,index] = np.linspace(0, 1, self.color_count)
        if random.random() < 0.5:
            colors[:,0] = random.random()
        colors[:,0] *= 360
        np.random.shuffle(colors)
        return self.cvt_color(colors, cvt)

    # Highest contrast and always between black and white.
    def random_colors_lightness_contrast(self):
        return self.random_colors_hs_helper(True)

    # Less contrast than lightness, but always has black.
    def random_colors_value_contrast(self):
        return self.random_colors_hs_helper(False)

    def random_colors(self):
        return random.choice([
            self.random_colors_rgb,
            self.random_colors_lightness_contrast,
            self.random_colors_value_contrast])()

    def transition(self):
        self.color_t = 0
        tween_time = self.argv.time
        ease = 'easeInOutSine'
        tween.to(self, 'color_t', 1, tween_time, ease).on_update(self.update_colors)
        tween.to(self, 'shape_t_delta', 1 / tween_time, tween_time / 2, ease).on_complete(
            lambda: tween.to(self, 'shape_t_delta', 0, tween_time / 2, ease)
        )
        self.current_color = self.next_color
        self.next_color = self.random_colors()

    def update_colors(self):
        conv_type = cv2.COLOR_RGB2LAB
        inv_type = cv2.COLOR_LAB2RGB
        target_color = lerp(self.cvt_color(self.current_color, conv_type), self.cvt_color(self.next_color, conv_type), self.color_t)
        target_color = self.cvt_color(target_color, inv_type)
        self.texture.write(target_color)

    def on_render(self, time: float, frame_time: float):
        self.shape_t += frame_time + self.shape_t_delta
        tween.update(frame_time)
        uniform(self.render_program, 'time', self.shape_t)
        self.render_vao.render()

    def on_key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            self.transition()

if __name__ == '__main__':
    LavaLamp.run()
