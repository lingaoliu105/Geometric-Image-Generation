from img_params import *
import math
import random
class SimpleShape():
    
    __slots__=["shape","size","position","pattern","rotation","color"]
    def __init__(self) -> None:
        pass
    
    def calculate_linked_vertices(self) -> list:
        if self.shape==Shape.LINE:
            rot_sin = math.sin(math.radians(self.rotation))
            rot_cos = math.cos(math.radians(self.rotation))
            size = self.size.get_actual()
            return [(self.position[0]+size//2*rot_cos,self.position[1]+size//2*rot_sin),(self.position[0]-size//2*rot_cos,self.position[1]-size//2*rot_sin)]
    def get_attach_point(self):
        fraction = random.choice(list(TouchingPoint))*random.randint(5)%1
        vertices = self.calculate_linked_vertices()
        
            
            
            
        return
