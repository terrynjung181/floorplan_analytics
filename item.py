import numpy as np
import matplotlib.path as mpltPath
import math

class Item:
    def __init__(self, archi_id, category, archi_category, dimensions, position, code, rotation, scale):
        self.archi_id = archi_id
        self.category = category
        self.archi_category = archi_category
        self.dimensions = dimensions
        self.position = np.array([position['x'], position['y'], position['z']])
        self.code = code // 10
        self.rotation = rotation
        self.scale = np.array([scale['x'], scale['y'], scale['z']])
        self.poly = self.item_polygon()

    def get_archi_id(self):
        return self.archi_id

    # Returns width of dimensions of item.
    def get_width(self):
        return self.dimensions['width'] / 2

    # Returns height of dimensions of item.
    def get_height(self):
        return self.dimensions['height'] / 2

    # Returns depth of dimensions of item.
    def get_depth(self):
        return self.dimensions['depth'] / 2

    # Returns unit of dimensions of item.
    def get_unit(self):
        return self.dimensions['unit']

    # Returns coordinates of position of item.
    def get_position(self):
        return self.position

    # Returns editorType code of the item.
    def get_code(self):
        return self.code

    # Returns archiCategory of the item
    def get_archi_category(self):
        return self.archi_category

    # Returns y rotation of item
    def get_rotation(self):
        return self.rotation

    # Returns x scale factor of item
    def get_x_scale(self):
        return self.scale[0]

    # Returns y scale factor of item
    def get_y_scale(self):
        return self.scale[1]

    # Returns z scale factor of item
    def get_z_scale(self):
        return self.scale[2]

    # Returns polygon array
    def get_poly(self):
        return self.poly

    # Checks whether the item is a chair. Returns True if it is a chair, False if it is not.
    def is_chair(self):
        chair_list = ["3BDCB55FABF94B0D", "918B3C2E26C1401E", "F15E2BBF8A7342DB", "7B4432E264464CF3",
                      "3AC1C027F3FD430A", "81326D90BC5E4C1D", "3F877C0C80134DFC", "23833539033C4061"]
        if self.archi_category is None:
            return False
        elif self.archi_category[0] in chair_list:
            return True
        return False

    # Checks whether the items is a desk. Returns True if it is a desk, False if it is not.
    def is_desk(self):
        if self.archi_category is None:
            return False
        elif self.archi_category[0] == 'E7468C0CC8FB4B63':
            return True
        return False

    # Checks whether the items is a door. Returns True if it is a door, False if it is not.
    def is_door(self):
        door_list = ["1633637E83634380", "83D507B20A56479F", "AE5BFBA2DE9F439B",
                     "FA0D229869E34AEF", "4F088FF30DF04594"]
        if self.archi_category is None:
            return False
        elif self.archi_category[0] in door_list:
            return True
        return False

    def is_column(self):
        if self.archi_category is None:
            return False
        elif self.archi_category[0] == "AF6BCC66E8014F7B":
            return True
        return False

    def is_window(self):
        window_list = ["B8A92E293E4E4047", "7D73016B30CC43F9", "7F67F38404474A5F",
                       "362F158D9E544F69", "D141E06C8BB441C5"]
        if self.archi_category is None:
            return False
        elif self.archi_category[0] in window_list:
            return True
        return False

    # Checks whether point (x, y) is inside the item.
    def point_is_inside(self, x, y):
        path = mpltPath.Path(self.poly)
        return path.contains_points([(x, y)])

    # Returns x coordinates of item.
    def x_pos(self):
        return self.position[0]

    # Returns y coordinates of item.
    def y_pos(self):
        return self.position[1]

    # Returns z coordinates of item.
    def z_pos(self):
        return self.position[2]

    # Changes position of item instance. [new_pos] is a numpy array.
    def move(self, new_pos):
        self.position = new_pos

    # Returns array of points that form the polygon shape of the instance of the item
    def item_polygon(self):
        item_xpos = self.x_pos()
        item_zpos = self.z_pos()
        item_width = abs((self.get_width()*self.get_x_scale())) / 2
        item_depth = abs((self.get_depth()*self.get_z_scale())) / 2
        x1, x2 = item_xpos - item_width, item_xpos + item_width
        y1, y2 = item_zpos - item_depth, item_zpos + item_depth
        points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        points_rot = []
        for (x, y) in points:
            rotation = self.get_rotation()
            y_rot = (y - item_zpos) * math.cos(rotation) + (x - item_xpos) * math.sin(rotation) + item_zpos
            x_rot = (x - item_xpos) * math.cos(rotation) - (y - item_zpos) * math.sin(rotation) + item_xpos
            points_rot.append((x_rot, y_rot))
        points_rot.append(points_rot[0])
        return points_rot

