from enum import Enum

class Representation(Enum):
    Points = 0
    Wireframe = 1
    Surface = 2
    SurfaceWithEdges = 3


class ColorLookupTable(Enum):
    Rainbow = 0
    Inverted_Rainbow = 1
    Greyscale = 2
    Inverted_Greyscale = 3

class Orientation(Enum):
    pos_z = 0
    pos_y = 1
    pos_x = 2
    neg_z = 3
    neg_y = 4
    neg_x = 5