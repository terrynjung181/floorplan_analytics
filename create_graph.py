import matplotlib.pyplot as plt
import a_star
import math


def door_nodes(graph, floor):
    """
    Creates nodes in the provided graph between door points
    :param graph: A Graph object (a_star.py)
    :param floor: A FloorPlan object (floor_plan.py)
    :return: [door_connections] = List of door connections in form (door_id, id of connected node)
    """
    door_list = floor.door_node_items()
    id_list = floor.get_id_list()
    door_connections = []
    grid_points = floor.get_merged_coordinates()

    # Connects door id points to mesh id points in 500 units radius
    # Door ids are in form of "Door #"
    for d in door_list.keys():
        current = door_list[d]
        (dx, dy) = current[0]
        closest_points = current[1]
        for (x, y) in closest_points:
            dist = math.sqrt((dx - x) ** 2 + (dy - y) ** 2)
            id_point_closest = id_list[grid_points.index((x, y))]
            door_connections.append((d, id_point_closest))
            graph.connect(d, id_point_closest, dist)
            floor.add_merged_dict(d, (dx, dy))

    return door_connections


def chair_nodes_room(graph, room):
    """
    Creates connections in the provided graph between chair points of a single room.
    :param graph: A Graph object (a_star.py)
    :param room: A Room object (floor_plan.py)
    :return: None
    """
    grid_points = room.get_merged_coordinates()
    chair_list = room.chair_node_items()
    id_list = room.get_id_list()

    # Connects chair id_points to closest mesh id_points
    # Chair ids are in form of "chair #"
    for c in chair_list.keys():
        current = chair_list[c]
        coord = current[0]
        closest = current[1]
        dist = math.sqrt((coord[0] - closest[0]) ** 2 + (coord[1] - closest[1]) ** 2)
        id_point_closest = id_list[grid_points.index(closest)]
        graph.connect(c, id_point_closest, dist)
        room.add_merged_dict(c, coord)

    return


def chair_nodes_floor(graph, floor):
    """
    Creates connections in the provided graph between chair points of the entire floor.
    :param graph: A Graph object (a_star.py)
    :param floor: A FloorPlan object (floor_plan.py)
    :return: [chair_ids] = A list of chair ids in form (room_num, "chair #")
    """
    id_list = floor.get_id_list()
    room_num = 0
    chair_ids = []
    grid_points = floor.get_merged_coordinates()

    # Connects chair id points to closest mesh id points
    # Chair ids are in form of (room_num, "chair #")
    for r in floor.rooms:
        chair_list = r.chair_node_items()
        for c in chair_list.keys():
            current = chair_list[c]
            coord = current[0]
            closest = current[1]
            dist = math.sqrt((coord[0] - closest[0]) ** 2 + (coord[1] - closest[1]) ** 2)
            id_point_closest = id_list[grid_points.index(closest)]
            graph.connect((room_num, c), id_point_closest, dist)
            chair_ids.append((room_num, c))
            floor.add_merged_dict((room_num, c), coord)
        room_num = room_num + 1

    return chair_ids


def make_nodes_room(graph, room):
    """
    Creates nodes in the provided graph between mesh points for a single room.
    :param graph: A Graph object (a_star.py)
    :param room:  A Room object (floor_plan.py)
    :return: None
    """
    id_list = room.get_id_list()

    # Connects each point to direct neighbors vertically, horizontally, and diagonally, if such points exist.
    for (x, y) in id_list:
        if (x + 1, y) in id_list:
            graph.connect((x, y), (x + 1, y), room.get_interval())
        if (x + 1, y + 1) in id_list:
            graph.connect((x, y), (x + 1, y + 1), room.get_interval() * math.sqrt(2))
        if (x - 1, y + 1) in id_list:
            graph.connect((x, y), (x - 1, y + 1), room.get_interval() * math.sqrt(2))
        if (x, y + 1) in id_list:
            graph.connect((x, y), (x, y + 1), room.get_interval())

    return


def make_nodes_floor(graph, floor):
    """
    Creates nodes in the provided graph between mesh points for the entire floor plan.
    :param graph: A Graph object (a_star.py)
    :param floor: A FloorPlan object (floor_plan.py)
    :return: [fake_mesh] = List of fake mesh point ids
    """
    mesh_dict = floor.get_mesh_dict()
    id_list = floor.get_id_list()
    fake_mesh = {}

    # Connects each point to direct neighbors vertically, horizontally, and diagonally, if such points exist.
    # For every connection made, a fake point is created at the midpoint and appended to [fake_mesh]
    for (i, x, y) in id_list:
        (mx, my) = mesh_dict[(i, x, y)]
        interval = floor.rooms[i].get_interval()
        if (i, x + 1, y) in id_list:
            (nx, ny) = mesh_dict[(i, x + 1, y)]
            graph.connect((i, x, y), (i, x + 1, y), interval)
            fake_mesh[(i, x + 0.5, y)] = ((mx + nx) / 2, ny)
        if (i, x + 1, y + 1) in id_list:
            (nx, ny) = mesh_dict[(i, x + 1, y + 1)]
            graph.connect((i, x, y), (i, x + 1, y + 1), interval * math.sqrt(2))
            fake_mesh[(i, x + 0.5, y + 0.5)] = ((mx + nx) / 2, (my + ny) / 2)
        if (i, x - 1, y + 1) in id_list:
            (nx, ny) = mesh_dict[(i, x - 1, y + 1)]
            graph.connect((i, x, y), (i, x - 1, y + 1), interval * math.sqrt(2))
            fake_mesh[(i, x - 0.5, y + 0.5)] = ((mx + nx) / 2, (my + ny) / 2)
        if (i, x, y + 1) in id_list:
            (nx, ny) = mesh_dict[(i, x, y + 1)]
            graph.connect((i, x, y), (i, x, y + 1), interval)
            fake_mesh[(i, x, y + 0.5)] = (mx, (my + ny) / 2)

    return fake_mesh


def create_corona(room):
    """
    Creates an undirected graph for the COVID-19 algorithms in corona.py
    :param room: A room object (floor_plan.py)
    :return: [graph] = Graph object (a_star.py)
             [graph.connected] = List of connections in graph
    """
    # Create new graph
    graph = a_star.Graph()

    # Create mesh, chair nodes inside graph
    make_nodes_room(graph, room)
    chair_nodes_room(graph, room)

    # Make graph undirected
    graph.make_undirected()

    return graph, graph.connected


def create_analysis(floor):
    """
    Creates an undirected graph for the floor plan analysis algorithms in analysis.py.
    :param floor: A FloorPlan object (floor_plan.py)
    :return: [graph] = Graph object
             [graph.connected] = List of connections in graph
             [chair_ids] = List of chair_ids in form (room_num, "chair #")
             [door_connected] = List of door connections in form (door_id, id of connected node)
             [fake_mesh] = List of fake mesh point ids
    """
    # Create new graph
    graph = a_star.Graph()

    # Create mesh, door, and chair nodes inside graph
    fake_mesh = make_nodes_floor(graph, floor)
    door_connected = door_nodes(graph, floor)
    chair_ids = chair_nodes_floor(graph, floor)

    # Make graph undirected
    graph.make_undirected()

    return graph, graph.connected, chair_ids, door_connected, fake_mesh


def shortest_path(graph, room, start_id, goal_id, heuristics=None):
    """
    Returns shortest path from start_id to goal_id
    :param graph: A Graph object (a_star.py)
    :param room: A Room object (floor_plan.py)
    :param start_id: Tuple that represents id of start point
    :param goal_id: Tuple that represents id of goal poin
    :param heuristics: Dictionary with heuristics data
    :return: [path] = List of nodes where each node is a step in the shortest path
             [heuristics] = Dictionary with heuristics data
    """
    # Creates new heuristics if they do not exist yet.
    if heuristics is None:
        heuristics = {}
        try:
            (goal_x, goal_y) = room.get_mesh_dict()[goal_id]
        except KeyError:
            return None
        # Creates heuristics for each connection
        for i in room.get_id_list():
            (grid_x, grid_y) = room.get_mesh_dict()[i]
            dist = math.sqrt(((goal_x - grid_x) ** 2) + ((goal_y - grid_y) ** 2))
            heuristics[i] = dist
    # Finds shortest path using a* algorithm
    path = a_star.astar_search(graph, heuristics, start_id, goal_id)

    return path, heuristics


def draw_connections(mesh_dict, connections):
    """
    Draws all connections in a graph
    :param mesh_dict: Dictionary of mesh point ids and coordinates
    :param connections: List of connections between points
    :return: None
    """
    for c in connections:
        first = c[0]
        second = c[1]
        first = mesh_dict[first]
        second = mesh_dict[second]
        plt.plot([first[0], second[0]], [first[1], second[1]])

    return


def draw_path(id_points, grid_points, path):
    """
    Draws a path from one point to another
    :param id_points: List of tuples of the ids of points
    :param grid_points: List of tuples of the coordinates of points
    :param path: List of nodes where each node is a step in the path
    :return: None
    """
    x_list = []
    y_list = []
    for p in path:
        current = p[0]
        grid = grid_points[id_points.index(current)]
        x_list.append(grid[0])
        y_list.append(grid[1])
    plt.plot(x_list, y_list)

    return
