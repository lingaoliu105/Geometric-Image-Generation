import math
from SimpleShape import SimpleShape


class TouchingPoint():
    __slots__ = [
        "position",
        "type",
        "neighbor_A",  # how to order A and B: compare left/right first, left is A right is B,if same, up is A, down is B
        "neighbor_B",
        "attach_type_A",  # edge, corner or arc
        "attach_type_B",
        "attach_position_A",  # top, near-top, middle, bottom, near-bottom, only applicable when attach_type_A is edge
        "attach_position_B",
    ]

    def __init__(self,neighbor1:SimpleShape,neighbor2:SimpleShape):
        center1 = neighbor1.position
        center2 = neighbor2.position
        if center1[0]<center2[0]:
            self.neighbor_A,self.neighbor_B = neighbor1,neighbor2
        elif math.abs(center1[0]-center2[0])<1e-10:
            if center1[1]>center2[1]:
                self.neighbor_A,self.neighbor_B = neighbor1,neighbor2
            else:
                self.neighbor_A, self.neighbor_B = neighbor2, neighbor1
        else:
            self.neighbor_A, self.neighbor_B = neighbor2, neighbor1
            
