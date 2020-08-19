from flask import Flask, request
import api_manager
from floor_plan import Room, Corner, Wall, FloorPlan
import analysis
import corona
import json

application = Flask(__name__)


@application.route('/')
def root():
    return "Hello Archisketch"


@application.route('/<port_id>')
def show_floor_plan_id(port_id):
    return api_manager.get_floor_plan(port_id)


@application.route('/workstations/<port_id>')
def get_work_stations(port_id):
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, item_list=item_list)
    return analysis.work_station_all(floor_plan.rooms)


@application.route('/covid/<port_id>')
def get_covid_score(port_id):
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id, 500)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, interval=500, item_list=item_list)
    return corona.score_all(floor_plan.rooms)


@application.route('/probability/<port_id>')
def get_probability(port_id):
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, item_list=item_list)
    return analysis.probability_all(floor_plan.rooms)


@application.route('/movement/<port_id>')
def get_human_movement(port_id):
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id, 450)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, interval=450, item_list=item_list)
    return analysis.human_movement(floor_plan)


@application.route('/viewpoint/<port_id>')
def get_field_of_view(port_id):
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, item_list=item_list)
    data = request.data.decode('utf-8')
    try:
        data = json.loads(data)
        return analysis.point_view_all(floor_plan, data['x'], data['z'])

    except:
        message = 'The input is not JSON format'
        return json.dumps({'status': 'FAILED', 'message': message})


@application.route('/privacy/<port_id>')
def get_privacy(port_id):
    corner_list, wall_list, room_list, item_list = api_manager.create_objects(port_id, 450)
    floor_plan = FloorPlan(corner_list, wall_list, room_list, interval=450, item_list=item_list)
    return analysis.privacy_all(floor_plan)

if __name__ == '__main__':
    application.debug = True
    application.run(host='0.0.0.0')
