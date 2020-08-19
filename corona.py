import matplotlib.colors as clr
import create_graph
import math
from constants import *

bad = (1, 0, 0)
less = (1, 0.5882352, 0)
decent = (1, 0.917647058, 0)
good = (0, 1, 0.16470588)
cmap = clr.LinearSegmentedColormap.from_list('custom', ['green', 'yellow', 'red'], N=256)


def sanitize(room, updated=False):
    """
    For now, assumes that sanitizer is deployed at first point in the room.
    Finds shortest path of all chairs from the sanitizer and labels chairs different colors depending on the distance.
    :param room: A Room object (floor_plan.py)
    :param updated: A boolean indicating whether mesh has been updated or not
    :return: [score_dict] = Dictionary that has a score assigned to every chair
    """
    # Checks if mesh has been updated or not
    if updated:
        grid_points = room.get_merged_coordinates()
    else:
        grid_points = room.update_mesh()

    id_points = room.get_id_list()
    first_id = id_points[0]
    chair_dict = room.chair_node_items()
    score_dict = {}

    # Creates graph with connections
    graph, connected = create_graph.create_corona(room)
    for c in chair_dict.keys():
        shortest, heuristics = create_graph.shortest_path(graph, room, c, first_id)
        if shortest is not None:
            path_length = shortest[len(shortest) - 1][1]
            if path_length < SANITIZE_FIRST:
                score_dict[c] = 0
            elif path_length < SANITIZE_SECOND:
                score_dict[c] = 0.5
            else:
                score_dict[c] = 1
        else:
            score_dict[c] = 0

    return score_dict


# Entire floor plan with the sanitize algorithm
def sanitize_all(room_list):
    for r in room_list:
        r.update_mesh()


def chair_dist(room):
    """
    If a chair item is within 1.8m of another chair, the chair is labeled red and if there are no other chairs within
    the radius of 1.8m, the chair is labeled green.
    :param room: A Room object (floor_plan.py)
    :return: [score_dict] = A dictionary assigning scores to each chair in the room
    """
    c_dict = room.chair_items()
    chair_key = list(c_dict.keys())
    too_close = []
    for i in range(len(chair_key)):
        for j in range(i + 1, len(chair_key)):
            c = chair_key[i]
            current = chair_key[j]
            c_x, c_y = c_dict[c].x_pos(), c_dict[c].z_pos()
            current_x, current_y = c_dict[current].x_pos(), c_dict[current].z_pos()
            dist = math.sqrt((c_x - current_x) ** 2 + (c_y - current_y) ** 2)
            if dist <= DIST_LEN:
                if current not in too_close:
                    too_close.append(current)
                if c not in too_close:
                    too_close.append(c)
                break
    score_dict = {c: 1 if c in too_close else 0 for c in chair_key}
    return score_dict


# Entire floor plan with the chair_dist algorithm
def chair_dist_all(room_list):
    for r in room_list:
        chair_dist(r)


def chair_radius(room, radius = RAD_LEN):
    """
    If a chair item has 0-1 other chairs within a 1.9m radius then it is labeled green. If it has 2-3 other chairs
    within then its is labeled yellow. 4+, it is labeled red.
    :param room: A Room object
    :return: [score_dict] = A dictionary assigning scores to each chair in the room
    """
    c_dict = room.chair_items()
    chair_key = list(c_dict.keys())
    score_dict = {}
    for c in chair_key:
        count = 0
        for current in chair_key:
            if c == current:
                continue
            else:
                x1, y1, x2, y2 = c_dict[c].x_pos(), c_dict[c].z_pos(), c_dict[current].x_pos(), c_dict[current].z_pos()
                dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                if dist <= RAD_LEN:
                    count = count + 1
        score_dict[c] = 0 if count <= 1 else 0.5 if count <= 3 else 1

    return score_dict


# Entire floor plan with the chair_radius algorithm
def chair_radius_all(room_list):
    for r in room_list:
        chair_radius(r)


def chair_per_sq(room):
    """
    If there are less than 1 chair per square meter, label room green. 2-3, label room yellow, 4+, label room red.
    :param room: A Room object (floor_plan.py)
    :return: [score_dict] = A dictionary assigning scores to each chair in the room
    """
    c_dict = room.chair_items()
    chair_key = c_dict.keys()
    sq_m = room.area() * 0.000004
    per_sq = len(c_dict) / sq_m
    score_dict = {c: 0 if per_sq <= 0.5 else 0.5 if per_sq <= 1 else 1 for c in chair_key}
    return score_dict


# Entire floor plan with the chair_per_sq algorithm
def chair_per_sq_all(room_list):
    for r in room_list:
        chair_per_sq(r)


# If there are less than 10 chairs in a room, label room green. If 11-15 chairs, label room yellow.
# If there are are 16+ chairs, label room red
def num_chair(room):
    """
    If there are less than 10 chairs in a room, label room green. If 11-15 chairs, label room yellow.
    If there are are 16+ chairs, label room red
    :param room: A Room object (floor_plan.py)
    :return: [score_dict] = A dictionary assigning scores to each chair in the room
    """
    c_dict = room.chair_items()
    chair_key = c_dict.keys()
    num = len(c_dict)
    score_dict = {c: 0 if num <= 10 else 0.5 if num <= 15 else 1 for c in chair_key}
    return score_dict


# Entire floor plan with the num_chair algorithm
def num_chair_all(room_list):
    for r in room_list:
        num_chair(r)


def score(room):
    """
    Takes score from all functions above and produces a final score for each chair regarding
    COVID-19 protocols and criterion. This function only maps out one room.
    Color legend: Red to green - Bad to good
    :param room: A Room object (floor_plan.py)
    :param fig: A Matplotlib figure
    :param ax: Matplotlib axes
    :return: None
    """
    c_dict = room.chair_items()
    score_list = []
    room.update_mesh()
    if len(room.get_id_list()) == 0:
        sanitize_score = None
    else:
        sanitize_score = sanitize(room, True)
    rad_score = chair_radius(room)
    sq_score = chair_per_sq(room)
    num_score = num_chair(room)
    dist_score = chair_dist(room)
    if sanitize_score is not None:
        for c in c_dict.keys():
            c_id = c_dict[c]
            total_score = 0.1 * sanitize_score[c] + 0.2 * dist_score[c] + 0.4 * rad_score[c] + 0.2 * sq_score[c] + 0.1 * num_score[c]
            score_list.append({'chair_id': c_id.get_archi_id(),
                               'position': {'x': c_id.x_pos(),
                                            'y': c_id.y_pos(),
                                            'z': c_id.z_pos()},
                               'total_score': total_score,
                               'scores': {'santizer': sanitize_score[c],
                                          'chair_distance': dist_score[c],
                                          'chairs_in_radius': rad_score[c],
                                          'square_footage': sq_score[c],
                                          'number_of_chairs': num_score[c]
                                          }})
    else:
        for c in c_dict.keys():
            total_score = 0.2 * dist_score[c] + 0.4 * rad_score[c] + 0.2 * sq_score[c] + 0.1 * num_score[c]
            c_id = c_dict[c]
            score_list.append({'chair_id': c_id.get_archi_id(),
                               'position': {'x': c_id.x_pos(),
                                            'y': c_id.y_pos(),
                                            'z': c_id.z_pos()},
                               'total_score': total_score,
                               'scores': {'santizer': sanitize_score[c],
                                          'chair_distance': dist_score[c],
                                          'chairs_in_radius': rad_score[c],
                                          'square_footage': sq_score[c],
                                          'number_of_chairs': num_score[c]
                                          }})
    return {'chairs': score_list}


# Plots the entire floor plan with the score algorithm
def score_all(room_list):
    score_list = []
    for r in room_list:
        r_score = score(r)
        if r_score is not None:
            score_list.append(r_score)
    return {'covid_rooms': score_list}
