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

        # TODO: complete other shapes. remember to add last -- first 
        elif self.shape==Shape.CIRCLE:
            raise ValueError
        elif self.shape == Shape.TRIANGLE_EQ:
            
    def get_attach_point(self)->tuple:
        fraction = random.choice(list(TouchingPoint))*random.randint(5)%1
        vertices = self.calculate_linked_vertices()
        edge_index = random.randint(0,len(vertices)-2) # the edge is vert[index] -- vert[index+1]
        v0 = vertices[edge_index] # a 2-tuple
        v1 = vertices[edge_index+1]
        return (v0[0] + (v1[0] - v0[0]) * fraction, v0[1] + (v1[1] - v0[1]) * fraction)
