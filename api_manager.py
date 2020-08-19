import requests
from item import Item
from floor_plan import Room, Corner, Wall, FloorPlan
import matplotlib.pyplot as plt
import analysis
import corona
import time


def get_floor_plan(port_id):
    """
    Extracts floor plan out of json
    :param port_id: A string that represents Archi id of floor plan
    :return: [floor_plan] = json of floor plan
    """
    url = 'https://api.archisketch.com/v1/public/projects/'
    response = requests.get(url + port_id + '/detail')
    response = response.json()['project']
    floor_plan = response['floorplans'][0]
    return floor_plan


def get_room_and_items(port_id):
    """
    Extracts room and item information out of floor plan
    :param port_id: A string that represents Archi id of floor plan
    :return: [corners] = List of dictionaries containing information on corners in the floor plan
             [walls] = List of dictionaries containing information on walls in the floor plan
             [rooms] = List of dictionaries containing information on rooms in the floor plan
             [items] = List of dictionaries containing information on items in the floor plan
    """
    floor_plan = get_floor_plan(port_id)
    if floor_plan is None:
        return [], [], [], []

    corners = [{
        'id': c['archiId'],
        'position': c['position']
    } for c in floor_plan['corners']]

    walls = [{
        'start': w['corners'][0],
        'end': w['corners'][1],
        'height': w['height'],
        'thickness': w['thickness']
    } for w in floor_plan['walls']]

    rooms = [{
        'corners': r['corners'],
        'inner_points': r['innerPoints'],
        'height': r['height'],
        'label': r['label'],
        'type': r['type']
    } for r in floor_plan['rooms']]

    items = [{
        'archi_id': i['archiId'],
        'category': i['meta'].get('categories'),
        'archiCategory': i['meta'].get('archiCategories'),
        'dimensions': i['meta'].get('dimensions'),
        'position': i['position'],
        'code': i['meta'].get('editorType').get('code'),
        'rotation': i['rotation'].get('y'),
        'scale': i['scale']
    } for i in floor_plan['items']]

    return corners, walls, rooms, items


def corner_by_id(corner_id, c_list):
    """
    Finds Corner object by id
    :param corner_id: A string representing Archi id of corner in floor plan
    :param c_list: A list of corners in the floor plan
    :return: A Corner object (floor_plan.py)
    """
    for c in c_list:
        if c.id == corner_id:
            return c


def create_objects(port_id, interval=None):
    """
    Returns list of corner, wall, room, and item objects with information extracted from json
    :param port_id: A string that represents Archi id of floor plan
    :param interval: Interval between mesh points to be created in floor plan
    :return: [corners] = List of Corner objects (floor_plan.py)
             [walls] = List of Wall objects (floor_plan.py)
             [rooms] = List of Room objects (floor_plan.py)
             [items] = List of Item objects (floor_plan.py)
    """
    corners_json, walls_json, rooms_json, items_json = get_room_and_items(port_id)

    corners = [Corner(c['id'], c['position']) for c in corners_json]
    walls = [Wall(w['start'], w['end'], w['height'], w['thickness']) for w in walls_json]
    rooms = [Room(r['corners'], r['inner_points'], r['height'], r['label'], r['type'], interval) for r in rooms_json]
    items = [Item(i['archi_id'], i['category'], i['archiCategory'], i['dimensions'], i['position'], i['code'], i['rotation'], i['scale']) for i in items_json]
    return corners, walls, rooms, items


if __name__ == '__main__':
    # EXAMPLE: 'XOOErmT8302DC3437D34541': test_room 9, 'XN6RiYo132FC530F34C4A01': test_room 1
    corner_list, wall_list, room_list, item_list = create_objects('XN6RiYo132FC530F34C4A01', 500)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, 500, item_list)
    test_room = floor_plan.rooms[1]
    print(analysis.privacy_all(floor_plan))
