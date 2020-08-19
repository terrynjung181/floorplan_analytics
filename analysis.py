import matplotlib.pyplot as plt
import matplotlib.colors as clr
import matplotlib.path as mpltPath
import api_manager
import create_graph
import random
import math
import coordinate_plane as c_plane
from constants import *

# Color bar for continuous color coding rather than discrete.
cmap = clr.LinearSegmentedColormap.from_list('custom', ['red', 'yellow', 'green'], N=256)


def draw_items_except_chair(room):
    """
    Plots all non-chair items in a single room.
    :param room: A Room object (floor_plan.py)
    :return: None
    """
    for i in room.items_list:
        if not (i.is_chair()):
            plt.plot(i.x_pos(), i.z_pos(), 'o', color=(0, 0, 0))

    return


def draw_items_except_desk(room):
    """
    Plots all non-desk items in a single room.
    :param room: A Room object (floor_plan.py)
    :return: None
    """
    for i in room.items_list:
        if not (i.is_desk()):
            points = i.get_poly()
            xs, ys = zip(*points)
            plt.fill(xs, ys, facecolor='black')

    return


def work_station(room):
    """
    Plots the floor plan of a single room. Labels all possible work spaces as green.
    Desks in meeting rooms are omitted as they are not workspaces. Returns the number of workspaces as well.
    Color legend --> Is workspace: green
    :param room: A Room object (floor_plan.py)
    :return: An integer representing total number of work stations in the Room.
    """

    # Checks if room is a meeting room. Desks in meeting rooms does not count towards work stations.
    # 26 is archi id for meeting. In this case it is supposed to represent meeting rooms.
    if room.get_type() == 26:
        return []
    return room.desk_items()


def work_station_all(room_list):
    """
    Plots the entire floor plan with the work_station algorithm. Prints total number of work stations
    in floor plan.
    :param room_list: A list of Room objects in a floor plan (floor_plan.py)
    :return: None
    """
    work_list = []
    for r in room_list:
        desk_list = work_station(r)
        if len(desk_list) != 0:
            work_list += work_station(r)
    return {"work_stations": work_list}


def probability(room):
    """
    Plots the floor plan of a single room. Labels probability that a person can be found in a particular chair.
    Color legend --> Likely: Green, Less likely: Yellow, Unlikely: Red
    :param room: A Room object (floor_plan.py)
    :param ax: A matplotlib axis
    :return: None
    """
    chair_dict = room.chair_items()
    prob_list = []
    for c in chair_dict.values():
        archi = c.get_archi_category()[0]
        if archi in list(CHAIR_PROB.keys()):
            prob_list.append({'chair_id': c.get_archi_id(),
                              'position': {'x': c.x_pos(),
                                           'y': c.y_pos(),
                                           'z': c.z_pos()},
                              'probability': CHAIR_PROB[archi] if room.get_type() != 26 else CHAIR_PROB[archi] * 0.5})

    return {'chairs': prob_list}


def probability_all(room_list):
    """
    Plots the entire floor plan with the probability algorithm
    :param room_list: A list of Room objects in a floor plan (floor_plan.py)
    :return: None
    """
    prob_list = []
    for r in room_list:
        r_prob = probability(r)
        if r_prob is not None:
            prob_list.append(r_prob)
        probability(r)

    return {'rooms': prob_list}


def human_movement_organize(floor):
    """
    Organizes the doors and chair ids of the floor plan to their respective rooms before using in the
    human movements algorithm. Serves as a helper function.
    :param floor: A FloorPlan object (floor_plan.py)
    :return: [graph] = A Graph object (a_star.py)
             [chair_ids] = A list of tuples where each tuple is a chair id.
             [room_door] = A dictionary showing connections between rooms and doors.
             [room_chair] = A dictionary showing connections between rooms and chairs.
             [fake_mesh] = A list tuples where each tuple is a fake mesh id.
    """
    graph, connected, chair_ids, door_connected, fake_mesh = create_graph.create_analysis(floor)
    room_door = {}
    room_chair = {}
    room_num = 0
    for r in floor.rooms:
        door_inside = []
        chair_inside = []

        # Extracts doors that are connected to room r
        for d in door_connected:
            if d[1][0] == room_num and d[0] not in door_inside:
                door_inside.append(d[0])

        # Extracts chairs that are connected to room r
        for c in chair_ids:
            if c[0] == room_num:
                chair_inside.append(c)

        room_door[room_num] = door_inside
        room_chair[room_num] = chair_inside
        room_num = room_num + 1
    return graph, chair_ids, room_door, room_chair, fake_mesh


def fake_mesh_helper(mesh_dict, i, x, y, occurrence):
    """
    Assigns values to the "fake" points before plotting them on the floor plan.
    Serves as a helper function
    :param mesh_dict: A dictionary of mesh id keys and mesh coordinate values.
    :param i: An integer representing a room number id
    :param x: An integer representing x id of fake point
    :param y: An integer representing y id of fake point
    :param occurrence: A dictionary showing mesh id keys and number of occurrences values
    :return: A float representing occurrence value to be given to fake node
    """
    m_key = list(mesh_dict.keys())
    num = 0
    total = 0

    # Only looks for real nodes that are direct neighbors of the fake points
    if (i, x - 0.5, y + 0.5) in m_key:
        num += 1
        total = total + occurrence[(i, x - 0.5, y + 0.5)]
    if (i, x + 0.5, y + 0.5) in m_key:
        num += 1
        total = total + occurrence[(i, x + 0.5, y + 0.5)]
    if (i, x - 0.5, y - 0.5) in m_key:
        num += 1
        total = total + occurrence[(i, x - 0.5, y - 0.5)]
    if (i, x + 0.5, y - 0.5) in m_key:
        num += 1
        total = total + occurrence[(i, x + 0.5, y - 0.5)]
    if (i, x + 0.5, y) in m_key:
        num += 1
        total = total + occurrence[(i, x + 0.5, y)]
    if (i, x - 0.5, y) in m_key:
        num += 1
        total = total + occurrence[(i, x - 0.5, y)]
    if (i, x, y - 0.5) in m_key:
        num += 1
        total = total + occurrence[(i, x, y - 0.5)]
    if (i, x, y + 0.5) in m_key:
        num += 1
        total = total + occurrence[(i, x, y + 0.5)]
    return total / num


def human_movement(floor):
    """
    Displays which areas of the floor plan has more human movement. The human movement density is
    calculated by counting how many different shortest paths (door to door, door to chair) cross a node
    Color legend: Red - not a lot of human movement, yellow - decent human movement, green - a lot of human movement
    :param floor: A FloorPlan object (floor_plan.py)
    :return: None
    """
    node_list = []
    mesh_dict = floor.collect_mesh()
    graph, chair_ids, room_door, room_chair, fake_mesh = human_movement_organize(floor)
    occurrence = {i: 0 for i in floor.get_id_list()}

    # Parse through every room.
    for r in room_door.keys():
        door_list = room_door[r]
        chair_list = room_chair[r]
        for i in range(len(door_list)):
            goal = door_list[i]

            # Initialize heuristics to None for every new goal node
            heuristics = None

            # Door to door connections (of same room)
            for j in range(i + 1, len(door_list)):
                start = door_list[j]
                path, heuristics = create_graph.shortest_path(graph, floor, start, goal, heuristics)
                if path is None:
                    continue
                for p in range(1, len(path) - 1):
                    occurrence[path[p][0]] = occurrence[path[p][0]] + 1

            # Chair to door connections (of same room)
            for c in chair_list:
                path, heuristics = create_graph.shortest_path(graph, floor, c, goal, heuristics)
                if path is None:
                    continue
                for p in range(1, len(path) - 1):
                    occurrence[path[p][0]] = occurrence[path[p][0]] + 0.25

    # Calls fake mesh helper function to assign values to every existing fake node.
    for (i, x, y) in fake_mesh.keys():
        occ_val = fake_mesh_helper(mesh_dict, i, x, y, occurrence)
        occurrence[(i, x, y)] = occ_val
        floor.add_merged_dict((i, x, y), fake_mesh[(i, x, y)])

    maximum_val = max(list(occurrence.values()))
    mesh_dict = floor.get_mesh_dict()
    for k in mesh_dict.keys():
        node_list.append({'position': {'x': mesh_dict[k][0],
                                       'z': mesh_dict[k][1]},
                          'value': occurrence[k] / maximum_val})
    return {'nodes': node_list}


def view_helper(corners, p, p1, p2, mid_point, counter):
    """
    Recursive helper function for view_helper
    :param corners: list of corners of the room
    :param p: Point object that represents the view point
    :param p1: Point object that represents the current viewpoint segment
    :param p2: Point object that represents the current viewpoint segment
    :param mid_point: Point object that represents the mid_point between p1 and p2
    :param counter: An integer that represents the current run through number
    :return: [mid_point] - Point object
    """
    if counter <= 0:
        return mid_point
    if c_plane.do_intersect_exclude_on_segment(corners, p, mid_point):
        mid_p = c_plane.Point((mid_point.x + p2.x) / 2, (mid_point.y + p2.y) / 2)
        return view_helper(corners, p, mid_point, p2, mid_p, counter - 1)
    else:
        mid_p = c_plane.Point((p1.x + mid_point.x) / 2, (p1.y + mid_point.y) / 2)
        return view_helper(corners, p, p1, mid_point, mid_p, counter - 1)


def view_main_loop(p, corners):
    """
    Main loop the field of view function runs to find the view area polygon
    :param p: Point object that represents view point
    :param corners: list of corners of the room
    :return: [view_list] - list of coordinates corresponding to corners of the view area polygon
    """
    view_list = []
    for i in range(len(corners)):
        (first_x, first_y), (second_x, second_y) = corners[i], corners[(i + 1) % len(corners)]
        p1 = c_plane.Point(first_x, first_y)
        p2 = c_plane.Point(second_x, second_y)
        if c_plane.do_intersect_exclude_on_segment(corners, p, p1):
            if c_plane.do_intersect_exclude_on_segment(corners, p, p2):
                p1_new = view_helper(corners, p, p1, p2, p1, REC_COUNT)
                p2_new = view_helper(corners, p, p2, p1, p2, REC_COUNT)
                if -10 < p1_new.x - p2.x < 10 and -10 < p1_new.y - p2.y < 10 and -10 < p2_new.x - p1.x < 10 and -10 < p2_new.y - p1.y < 10:
                    continue
                elif -10 < p1_new.x - p2.x < 10 and -10 < p1_new.y - p2.y < 10:
                    p1_new = view_helper(corners, p, p1, p2_new, p1, REC_COUNT)
                    view_list = view_list + [p1_new, p2_new]
                elif -10 < p2_new.x - p1.x < 10 and -10 < p2_new.y - p1.y < 10:
                    p2_new = view_helper(corners, p, p2, p1_new, p2, REC_COUNT)
                    view_list = view_list + [p1_new, p2_new]
                else:
                    view_list = view_list + [p1_new, p2_new]
            else:
                p_new = view_helper(corners, p, p1, p2, p1, REC_COUNT)
                view_list = view_list + [p_new]
        else:
            if c_plane.do_intersect_exclude_on_segment(corners, p, p2):
                p_new = view_helper(corners, p, p2, p1, p2, REC_COUNT)
                view_list = view_list + [p1, p_new]
            else:
                view_list = view_list + [p1]
    return view_list


def column_helper(column, p, view_list):
    """
    Helper function for the field of view function. Takes the view area polygon and updates it while taking
    obstacles such as columns and walls into account.
    :param column: column item object or a rogue wall inside the room
    :param p: Point object that represents the view point
    :param view_list: list of coordinates that correspond to the corners of the view area polygon
    :return: [view_list_new] - list of coordinates that correspond to the corners of the view area polygon
    """
    view_list_new = []
    color = (random.random(), random.random(), random.random())
    for i in range(len(view_list)):
        p1, p2 = view_list[i], view_list[(i + 1) % len(view_list)]
        path = mpltPath.Path([(p.x, p.y), (p1.x, p1.y), (p2.x, p2.y)])
        current = []
        corners_new = {}
        for (cx, cy) in column:
            # Checks that corner is in current segment
            if not path.contains_points([(cx, cy)]):
                continue
            c_point = c_plane.Point(cx, cy)
            # Checks that current viewpoint to corner segment intersects itself
            if c_plane.do_intersect_exclude_on_segment(column, p, c_point):
                continue
            intersection = c_plane.find_intersection(p, c_point, p1, p2)
            dist = math.sqrt((intersection.x - p1.x) ** 2 + (intersection.y - p1.y) ** 2)
            # Checks for middle corner point
            c_index = column.index((cx, cy))
            column_copy = column.copy()
            column_copy.pop(c_index)
            if c_plane.do_intersect_exclude_on_segment(column_copy, p, intersection):
                corners_new[dist] = (None, c_point)
                continue
            # Non middle corner point
            corners_new[dist] = (intersection, c_point)
        # Check p1 does not intersect column
        if not c_plane.do_intersect_exclude_on_segment(column, p, p1):
            current.append(p1)
            checked = False
        else:
            checked = True
        # Sort distance
        distance_sorted = sorted(list(corners_new.keys()))
        # Append by distance
        for d in distance_sorted:
            points = corners_new[d]
            if points[0] is None:
                current.append(points[1])
                checked = True
                continue
            if checked:
                current = current + [points[1], points[0]]
                checked = False
            else:
                current = current + [points[0], points[1]]
                checked = True
        # Check p2 does not intersect column
        if not c_plane.do_intersect_exclude_on_segment(column, p, p2):
            current.append(p2)
        for i in range(len(current)):
            first, second = current[i], current[(i + 1) % len(current)]
            view_list_new.append(first)
    return view_list_new


def point_view(room, x, y, obstacles, original):
    """
    Finds the view area polygon of the room considering its view point and the columns/wall inside the room that
    may obscure vision.
    :param room: Room object
    :param x: Integer representing x coordinate of view point
    :param y: Integer representing y coordinate of view point
    :param obstacles: A list of obstacles inside the room
    :param original: A boolean checking whether this function is being used for the point_view_all function or
            the privacy function
    :return: [view_dict] - list of dictionaries where each dictionary holds information about the coordinates of
            the view polygon
    """
    inner_points = room.room_polygon()
    p = c_plane.Point(x, y)
    view_dict = []
    view_list = view_main_loop(p, inner_points)
    ordered = sorted(list(obstacles.keys()), key=lambda i: (i[0]-x)**2 + (i[1] - y)**2, reverse=True)
    for c in ordered:
        current = obstacles[c][0:4]
        view_list = column_helper(current, p, view_list)
    if original:
        for p in view_list:
            view_dict.append({"x": p.x, "z": p.y})
        return view_dict
    else:
        for p in view_list:
            view_dict.append((p.x, p.y))
        return view_dict


def point_view_all(floor, x, y):
    for r in floor.rooms:
        if r.point_is_inside(x, y):
            column_dict = r.column_items()
            walls = floor.rogue_wall()
            for w in walls:
                start_corner = api_manager.corner_by_id(w.get_start(), floor.get_corners())
                end_corner = api_manager.corner_by_id(w.get_end(), floor.get_corners())
                if r.point_is_inside(start_corner.x_pos(), start_corner.z_pos()):
                    column_dict[(start_corner.x_pos(), start_corner.z_pos())] = [(start_corner.x_pos(), start_corner.z_pos()), (end_corner.x_pos(), end_corner.z_pos())]
            return {"polygon_points": point_view(r, x, y, column_dict, True)}


def privacy(room, obstacles):
    """
    Returns information on which parts of the floor plan are more private compared to other locations.
    :param room: Room object
    :param obstacles: A list of obstacles inside the room
    :return: [occurrence] - Dictionary showing how often a node/mesh_point can be viewed from other node/mesh_point in
            the floor plan
    """
    mesh = room.get_mesh_dict()
    occurrence = {i: 0 for i in room.get_id_list()}
    for i in mesh.keys():
        x, y = mesh[i][0], mesh[i][1]
        view_poly = mpltPath.Path(point_view(room, x, y, obstacles, False))
        for j in mesh.keys():
            if view_poly.contains_point(mesh[j]):
                occurrence[j] += 1
    return occurrence


def privacy_all(floor):
    occurrence = {}
    node_list = []
    for r in floor.rooms:
        r.update_mesh()
        column_dict = r.column_items()
        walls = floor.rogue_wall()
        for w in walls:
            start_corner = api_manager.corner_by_id(w.get_start(), floor.get_corners())
            end_corner = api_manager.corner_by_id(w.get_end(), floor.get_corners())
            if r.point_is_inside(start_corner.x_pos(), start_corner.z_pos()):
                column_dict[(start_corner.x_pos(), start_corner.z_pos())] = [(start_corner.x_pos(), start_corner.z_pos()), (end_corner.x_pos(), end_corner.z_pos())]
        room_view = privacy(r, column_dict)
        r_mesh = r.get_mesh_dict()
        for i in r_mesh.keys():
            occurrence[r_mesh[i]] = room_view[i]
    maximum_val = max(list(occurrence.values()))
    for (x, y) in occurrence.keys():
        node_list.append({'position': {'x': x, 'z': y}, 'value': occurrence[(x, y)] / maximum_val})
    return {'nodes': node_list}
