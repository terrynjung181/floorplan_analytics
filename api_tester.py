import application
from floor_plan import Room, Corner, Wall, FloorPlan
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import api_manager
import requests
import json

cmap = clr.LinearSegmentedColormap.from_list('custom', ['red', 'yellow', 'green'], N=256)
cmap2 = clr.LinearSegmentedColormap.from_list('custom', ['green', 'yellow', 'red'], N=256)


def workstations_test(port_id):
    response = requests.get('http://localhost:5000/workstations/' + port_id)
    info = response.json()['work_stations']
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, item_list=item_list)
    floor_plan.draw_all()
    xs, ys = [], []
    for desk in info:
        xs.append(desk['position'].get('x'))
        ys.append(desk['position'].get('z'))
    plt.plot(xs, ys, 'go')
    plt.show()
    return


def probability_test(port_id):
    response = requests.get('http://localhost:5000/probability/' + port_id)
    info = response.json()['rooms']
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, item_list=item_list)
    xs, ys, color_bar = [], [], []
    fig, ax = plt.subplots()
    floor_plan.draw_rooms_all()
    for chair in info:
        for c in chair['chairs']:
            xs.append(c['position'].get('x'))
            ys.append(c['position'].get('z'))
            color_bar.append(c['probability'])
    im = ax.scatter(xs, ys, c=color_bar, cmap=cmap)
    im.set_clim(0.0, 1.0)
    plt.show()
    return


def covid_test(port_id):
    response = requests.get('http://localhost:5000/covid/' + port_id)
    info = response.json()['covid_rooms']
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id, 500)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, interval=500, item_list=item_list)
    xs, ys, color_bar = [], [], []
    fig, ax = plt.subplots()
    floor_plan.draw_rooms_all()
    for chair in info:
        for c in chair['chairs']:
            xs.append(c['position'].get('x'))
            ys.append(c['position'].get('z'))
            color_bar.append(c['total_score'])
    im = ax.scatter(xs, ys, c=color_bar, cmap=cmap2)
    im.set_clim(0.0, 1.0)
    plt.show()
    return


def movement_test(port_id):
    response = requests.get('http://localhost:5000/movement/' + port_id)
    info = response.json()['nodes']
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id, 450)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, interval=450, item_list=item_list)
    xs, ys, color_bar = [], [], []
    fig, ax = plt.subplots()
    floor_plan.draw_all()
    for n in info:
        xs.append(n['position'].get('x'))
        ys.append(n['position'].get('z'))
        color_bar.append(n['value'])
    im = ax.scatter(xs, ys, c=color_bar, cmap=cmap)
    im.set_clim(0.0, 1.0)
    plt.show()
    return


def field_of_view_test(port_id):
    url = 'http://localhost:5000/viewpoint/' + port_id
    response = requests.get(url, data=json.dumps({"x": 12565, "z": 22166}))
    info = response.json()['polygon_points']
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, item_list=item_list)
    xs, ys = [], []
    floor_plan.draw_rooms_all()
    for point in info:
        xs.append(point['x'])
        ys.append(point['z'])
    plt.fill(xs, ys, alpha=0.5)
    plt.show()
    return


def privacy_test(port_id):
    response = requests.get('http://localhost:5000/privacy/' + port_id)
    info = response.json()['nodes']
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id, 450)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, interval=450, item_list=item_list)
    xs, ys, color_bar = [], [], []
    fig, ax = plt.subplots()
    floor_plan.draw_all()
    for n in info:
        xs.append(n['position'].get('x'))
        ys.append(n['position'].get('z'))
        color_bar.append(n['value'])
    im = ax.scatter(xs, ys, c=color_bar, cmap=cmap)
    im.set_clim(0.0, 1.0)
    plt.show()
    return


if __name__ == '__main__':
    workstations_test('XN6RiYo132FC530F34C4A01')
