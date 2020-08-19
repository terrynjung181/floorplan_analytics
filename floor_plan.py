import numpy as np
import math
from item import Item
import matplotlib.pyplot as plt
import matplotlib.path as mpltPath
from shapely.geometry import Polygon


class Corner:
    def __init__(self, corner_id, position):
        self.id = corner_id
        self.position = np.array([position['x'], position['y'], position['z']])

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return str(self.position)

    # Returns x position of corner
    def x_pos(self):
        return self.position[0]

    # Returns y position of corner
    def y_pos(self):
        return self.position[1]

    # Returns z position of corner
    def z_pos(self):
        return self.position[2]

    # Converts class to dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'position': {'x': self.x_pos, 'y': self.y_pos, 'z': self.z_pos}
        }


class Wall:
    def __init__(self, start, end, height=1000, thickness=100):
        self.start = start
        self.end = end
        self.height = height
        self.thickness = thickness

    # Returns length of wall
    def length(self):
        x_term = (self.start.x_pos() - self.end.x_pos()) ** 2
        z_term = (self.start.z_pos() - self.end.z_pos()) ** 2
        return math.sqrt(x_term + z_term)

    # Returns the start corner id of wall
    def get_start(self):
        return self.start

    # Returns the end corner id of wall
    def get_end(self):
        return self.end

    # Returns boolean indicating whether this instance of Wall is a neighbor of a different instance of Wall.
    def is_neighbor(self, w):
        return sum(
            [self.start == w.start, self.start == w.end,
             self.end == w.start, self.end == w.start]) == 1

    # Returns boolean indicating whether the first end of the Wall is a neighbor of a different instance of Wall.
    def is_start_neighbor(self, w):
        return self.start == w.end or self.start == w.start

    # Returns boolean indicating whether the second end of the Wall is a neighbor of a different instance of Wall.
    def is_end_neighbour(self, w):
        return self.end == w.end or self.end == w.start

    # Returns bottom surface area of current instance of Wall
    def area(self):
        return self.length() * self.thickness

    # Converts class to dictionary
    def to_dict(self):
        return {
            'start': self.start.id,
            'end': self.end.id,
            'height': self.height,
            'thickness': self.thickness
        }


class Room:
    def __init__(self, corners, inner_corners, height, label, type, interval=None, items=None):
        self.corners = corners
        self.inner_points = np.empty((0, 3), float)
        for i in inner_corners:
            self.inner_points = np.concatenate((self.inner_points, [[i['x'], i['y'], i['z']]]), axis=0)
        self.height = height
        self.label = label
        self.type = type
        self.interval = interval
        self.items_list = items if items is not None else []
        self.poly = self.room_polygon()
        # Dictionary of mesh coordinates and their ids
        self.mesh_dict = self.merge_mesh() if interval is not None else []

    # Returns inner-points of the room
    def get_inner_points(self):
        return self.inner_points

    # Returns list of corners in the room (unordered)
    def get_corners(self):
        return self.corners

    # Returns current list of items inside the room
    def get_items_list(self):
        return self.items_list

    # Returns interval of mesh points of the room
    def get_interval(self):
        return self.interval

    # Sets interval to different value [inter]
    def set_interval(self, inter):
        self.interval = inter
        return

    # Returns room type
    def get_type(self):
        return self.type

    # Returns mesh dictionary with ids and mesh coordinate points
    def get_mesh_dict(self):
        return self.mesh_dict

    # Returns id list of the mesh points
    def get_id_list(self):
        return list(self.mesh_dict.keys())

    # Returns merged coordinate list
    def get_merged_coordinates(self):
        return list(self.mesh_dict.values())

    # Returns area of the room
    def area(self):
        return Polygon(self.poly).area

    # Returns a polygon object of the room
    def room_polygon(self):
        points = []
        for i in self.inner_points:
            points.append((i[0], i[2]))
        return points

    # Returns boolean indicating whether item belongs inside the instance of the room
    def item_is_inside(self, item):
        if isinstance(item, Item):
            p = (item.x_pos(), item.z_pos())
            path = mpltPath.Path(self.poly)
            return path.contains_points([p])
        else:
            False

    # Returns boolean indicating whether given point belongs inside the instance of the room
    def point_is_inside(self, x, y):
        path = mpltPath.Path(self.poly)
        return path.contains_points([(x, y)])

    # Returns (x,y) mesh coordinate that is closest to (cx, cy)
    def find_closest(self, cx, cy):
        return min(list(self.mesh_dict.values()), key=lambda p: (cx - p[0]) ** 2 + (cy - p[1]) ** 2)

    # Adds item to list of items in the instance of the room
    def add_item(self, item):
        if self.item_is_inside(item):
            self.items_list.append(item)

    # Returns a dictionary of window items with Item object as key and (x, z) position as value
    def window_items(self):
        window_dict = {}
        for i in self.walls_list:
            if i.is_window():
                window_dict[i] = (i.x_pos, i.z_pos)
        return window_dict

    # Returns dictionary of desk items inside the room.
    def desk_items(self):
        desk_list = []
        for i in self.items_list:
            if i.is_desk():
                desk_list.append({"desk_id": i.get_archi_id(),
                                  "position": {"x": i.x_pos(),
                                               "y": i.y_pos(),
                                               "z": i.z_pos()}})
        return desk_list

    # Returns a dictionary of column items inside the room
    def column_items(self):
        column_dict = {}
        for i in self.items_list:
            if i.is_column():
                column_dict[(i.x_pos(), i.z_pos())] = (i.item_polygon())
        return column_dict

    # Returns dictionary of chair items inside the room.
    def chair_items(self):
        chair_dict = {}
        chair_num = 0
        for i in self.items_list:
            if i.is_chair():
                chair_dict["chair " + str(chair_num)] = i
                chair_num = chair_num + 1
        return chair_dict

    # Returns dictionary of chair items inside the room. Hold information to create chair nodes
    def chair_node_items(self):
        chair_dict = {}
        chair_num = 0
        if self.mesh_dict is not None:
            for i in self.items_list:
                if i.is_chair():
                    chair_x = i.x_pos()
                    chair_z = i.z_pos()
                    chair_dict["chair " + str(chair_num)] = [(chair_x, chair_z), self.find_closest(chair_x, chair_z)]
                    chair_num = chair_num + 1
        return chair_dict

    # Returns min and max x, y coordinates of the room
    def min_max_coor(self):
        coord = [(i[0], i[2]) for i in self.inner_points]
        xs, ys = zip(*coord)
        return max(xs), min(xs), max(ys), min(ys)

    # Updates mesh grid by removing points that are out of bound or points that overlap with an obstacle.
    # Returns a new merged grid as well as updates the id list
    def update_mesh(self):
        new_dict = self.mesh_dict.copy()
        for id_point in new_dict.keys():
            (x, y) = self.mesh_dict[id_point]
            for i in self.items_list:
                if i.point_is_inside(x, y):
                    self.mesh_dict.pop(id_point)
                    break
            if not (self.point_is_inside(x, y)):
                try:
                    self.mesh_dict.pop(id_point)
                except KeyError:
                    continue
        return self.mesh_dict.keys()

    # Returns list of tuples, where each tuple represents a mesh grid point
    def merge_mesh(self):
        x_max, x_min, y_max, y_min = self.min_max_coor()
        x_interval = int(x_max - x_min) // self.get_interval()
        y_interval = int(y_max - y_min) // self.get_interval()
        x = np.linspace(x_min + 10, x_max - 10, x_interval)
        y = np.linspace(y_min + 10, y_max - 10, y_interval)
        x_mesh, y_mesh = np.meshgrid(x, y)
        if len(x_mesh) <= 5:
            self.set_interval(350)
            x_interval = int(x_max - x_min) // self.get_interval()
            y_interval = int(y_max - y_min) // self.get_interval()
            x = np.linspace(x_min + 10, x_max - 10, x_interval)
            y = np.linspace(y_min + 10, y_max - 10, y_interval)
            x_mesh, y_mesh = np.meshgrid(x, y)
        if not len(x_mesh):
            return {}
        grid_points = {(j, i): (x_mesh[i][j], y_mesh[i][j]) for i in range(len(x_mesh)) for j in range(len(x_mesh[0]))}
        return grid_points

    # Appends a new coordinate to the merged mesh coordinates
    def add_merged_dict(self, id_point, new_coord):
        self.mesh_dict[id_point] = new_coord
        return

    # Plots single room. If plotting single room, then individual is True and plot shows
    def draw_room(self, color, individual=True):
        coord = []
        for i in self.inner_points:
            coord.append((i[0], i[2]))
        coord.append(coord[0])
        xs, ys = zip(*coord)
        plt.plot(xs, ys, color=color)
        plt.axis('equal')
        if individual:
            plt.show()

    # Plots items inside a single room. Does not show plot on call.
    def draw_items(self, color):
        for i in self.items_list:
            points = i.get_poly()
            xs, ys = zip(*points)
            plt.fill(xs, ys, facecolor=color)
        plt.axis('equal')

    # Plots all non-chair items in a single room.
    def draw_items_except_chair(self):
        for i in self.items_list:
            if not (i.is_chair()):
                points = i.get_poly()
                xs, ys = zip(*points)
                plt.fill(xs, ys, facecolor=(0, 0, 0))

    # Plots mesh grid inside a single room. Does not show plot on call.
    def draw_mesh(self):
        for a in self.update_mesh():
            (x, y) = self.get_mesh_dict()[a]
            plt.plot(x, y, 'ko', markersize=1)
        plt.axis('equal')

    # Plots mesh grid before updating inside a single room. Does not show plot on call.
    def draw_no_update_mesh(self):
        for (x, y) in self.get_merged_coordinates():
            plt.plot(x, y, 'ro', markersize=1)
        plt.axis('equal')

    # Draws current room, items, and mesh grid of room using matplotlib. Shows plot on call.
    def draw(self, individual=True):
        self.draw_room((0, 0, 0), False)
        self.draw_items((0, 0, 0))
        if individual:
            plt.show()

    # Converts class to dictionary
    def to_dict(self):
        return {
            'corners': [c.id for c in self.corners],
            'inner_points': [{'x': self.inner_points[i][0],
                              'y': self.inner_points[i][1],
                              'z': self.inner_points[i][2]} for i in range(len(self.inner_points))],
            'height': self.height,
            'label': self.label
        }


class FloorPlan:
    def __init__(self, corner_list, wall_list, room_list, interval=None, item_list=None):
        self.corners = corner_list
        self.walls = wall_list
        self.rooms = room_list
        self.items = item_list
        self.opening_items = []
        self.update_item_list()
        self.mesh_dict = None
        self.interval = interval

    # Returns list of corner objects that exist in the entire floor plan
    def get_corners(self):
        return self.corners

    # Returns list of walls that do not belong to the walls of a room
    def rogue_wall(self):
        room_corner = []
        for r in self.rooms:
            room_corner = room_corner + r.get_corners()
        rogue_walls = []
        for w in self.walls:
            if w.get_start() in room_corner:
                continue
            if w.get_end() in room_corner:
                continue
            else:
                rogue_walls.append(w)
        return rogue_walls

    # Returns current list of wall items inside the room.
    def get_opening_list(self):
        return self.opening_items

    # Returns interval of mesh coordinates
    def get_interval(self):
        return self.interval

    # Returns mesh dictionary with ids and mesh coordinate points
    def get_mesh_dict(self):
        return self.mesh_dict

    # Returns id list of the mesh points
    def get_id_list(self):
        return list(self.mesh_dict.keys())

    # Returns merged coordinate list
    def get_merged_coordinates(self):
        return list(self.mesh_dict.values())

    # Updates item list for each room. If item is in certain room, the item is added to the
    # room's item list.
    def update_item_list(self):
        for i in self.items:
            item_code = i.get_code()
            if item_code == 5:
                self.opening_items.append(i)
            elif not item_code == 2:
                continue
            for r in self.rooms:
                if r.item_is_inside(i) and item_code == 2:
                    r.add_item(i)
                    break

    # Returns list of mesh points within a radius of 500 units from (dx, dy)
    def closest_points(self, dx, dy, len):
        return [p for p in self.mesh_dict.values() if ((dx - p[0]) ** 2 + (dy - p[1]) ** 2) < len]

    # Returns dictionary of door items inside the room. Hold information to create door nodes
    def door_node_items(self):
        door_dict = {}
        door_num = 0
        if self.mesh_dict is not None:
            for i in self.opening_items:
                if i.is_door():
                    door_x = i.x_pos()
                    door_z = i.z_pos()
                    door_dict["door " + str(door_num)] = [(door_x, door_z), self.closest_points(door_x, door_z, 250000)]
                    door_num = door_num + 1
        return door_dict

    # Returns a dictionary of window items inside the floor plan
    def window_items(self):
        window_dict = {}
        for i in self.opening_items:
            if i.is_window():
                w_x = i.x_pos()
                w_z = i.z_pos()
                window_dict[i] = [(w_x, w_z), self.closest_points(w_x, w_z, 250000)]
        return window_dict

    # Returns dictionary of the mesh coordinates of all rooms. Gives coordinates ids in the form (i, x, y)
    # (x,y) is the original id and i changes by room
    def collect_mesh(self):
        total_mesh = {}
        room_num = 0
        for r in self.rooms:
            r.update_mesh()
            mesh_dict = r.get_mesh_dict()
            for i in mesh_dict.keys():
                total_mesh[(room_num,) + i] = mesh_dict[i]
            room_num = room_num + 1
        self.mesh_dict = total_mesh
        return total_mesh

    # Adds a coordinate to the mesh coordinate dictionary
    def add_merged_dict(self, id_p, coord):
        self.mesh_dict[id_p] = coord

    # Draws all the window items in the floor plan
    def draw_window(self):
        window_dict = self.window_items()
        for w in window_dict.keys():
            (x, y) = window_dict[w][0]
            plt.plot(x, y, 'o', color=(0, 1, 0))

    # Draws all the rooms in the provided list of Room objects.
    def draw_all(self):
        for r in self.rooms:
            r.draw(False)

    # Draws all the rooms in the provided list of Room objects as well as the items.
    def draw_rooms_all(self):
        for r in self.rooms:
            r.draw_room((0, 0, 0), False)
            r.draw_items_except_chair()

    # Draws mesh on top of entire floor plan.
    def draw_mesh_all(self):
        for (x, y) in self.get_merged_coordinates():
            plt.plot(x, y, 'ro', markersize=2)
        plt.axis('equal')
