

from entities.simple_shape import SimpleShape
from image_generators.image_generator import ImageGenerator


class RadialImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        super().__init__()
        
        
    def generate_center(self):
        center_shape = SimpleShape(self.panel_center(),size=self.panel_radius / 2)
        self.shapes.append(center_shape)
        
    def generate(self):
        return super().generate()