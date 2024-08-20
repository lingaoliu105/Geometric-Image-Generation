from img_params import *
import math
import random
import numpy as np
class SimpleShape():

    __slots__=["shape","size","position","pattern","rotation","color"]
    def __init__(self) -> None:
        pass

    def calculate_linked_vertices(self) -> list:
        rot_rad = math.radians(self.rotation)
        rot_sin = math.sin(rot_rad)
        rot_cos = math.cos(rot_rad)
        rot_polar = np.array((rot_cos,rot_sin))
        rot_cart = self.size.value * rot_polar
        if self.shape==Shape.LINE:
            size = self.size.get_actual(self.shape)
            return [np.array(x) for x in[(self.position[0]+size//2*rot_cos,self.position[1]+size//2*rot_sin),(self.position[0]-size//2*rot_cos,self.position[1]-size//2*rot_sin)]]

        # TODO: complete other shapes. remember to add last -- first
        elif self.shape==Shape.CIRCLE:
            raise ValueError
        else :
            if self.shape == Shape.TRIANGLE_EQ:
                angle_list = [-30,90,210]
            elif self.shape==Shape.SQUARE:
                angle_list = [-45,45,135,225]
            elif self.shape==Shape.PENTAGON:
                angle_list = [-54+72*x for x in range(5)]
            elif self.shape==Shape.HEXAGON:
                angle_list = [60*x for x in range(6)]
                
            vertices = [None]*(len(angle_list)+1)
            index=0
            for angle in angle_list:
                rot_rad = math.radians(angle)
                rot_sin = math.sin(rot_rad)
                rot_cos = math.cos(rot_rad)
                rot_polar = np.array((rot_cos,rot_sin))
                rot_cart = self.size.value * rot_polar
                vertices[index] = self.position+rot_cart
                index+=1
            vertices[-1] = vertices[0]
            return vertices

    
    def get_attach_point(self)->np.ndarray:
        if self.shape==Shape.CIRCLE:
            rand_rad = random.random()*2*math.pi
            return self.position + self.size.value * np.array([math.cos(rand_rad),math.sin(rand_rad)])
        fraction = random.choice(list(TouchingPoint)).value*random.randint(1,5)%1
        vertices = self.calculate_linked_vertices()
        edge_index = random.randint(0,len(vertices)-2) # the edge is vert[index] -- vert[index+1]
        return vertices[edge_index]+fraction*(vertices[edge_index+1]-vertices[edge_index])