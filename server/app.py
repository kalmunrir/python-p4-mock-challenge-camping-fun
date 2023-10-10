#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = [camper.to_dict(only=('id', 'name', 'age')) for camper in Camper.query.all()]

        return make_response(campers, 200)
    
    def post(self):
        try:
            new_camper = Camper(
                name=request.get_json()['name'],
                age=request.get_json()['age']
            )
        except ValueError as e:
            return make_response({"errors": str(e)}, 400)
            

        db.session.add(new_camper)
        db.session.commit()

        return make_response(new_camper.to_dict(), 200)
api.add_resource(Campers, '/campers')

class CamperById(Resource):
    def get(self, id):
        try:
            body = Camper.query.filter_by(id=id).first().to_dict()
            status = 200
        except Exception:
            body = {"error": "Camper not found"}
            status = 404
        
        return make_response(body, status)
    
    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()

        if camper:
            dtp = request.get_json()
            errors = []
            for attr in dtp:
                try:
                    setattr(camper, attr, dtp[attr])
                except ValueError as e:
                    errors.append(e.__repr__())
            if len(errors) != 0:
                return make_response({"errors": errors}, 400)
            else:
                db.session.add(camper)
                db.session.commit()
                return make_response(camper.to_dict(), 202)
        
        return make_response({"error": "Camper not found"}, 404)
api.add_resource(CamperById, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        activities = [activity.to_dict(only=('id', 'name', 'difficulty')) for activity in Activity.query.all()]
        return make_response(activities, 200)
api.add_resource(Activities, '/activities')

class ActivityById(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()

        if activity:
            db.session.delete(activity)
            db.session.commit()
            return make_response('', 204)
        else:
            return make_response({"error": "Activity not found"}, 404)
api.add_resource(ActivityById, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        try:
            new_signup = Signup(
                camper_id=request.get_json()['camper_id'],
                activity_id=request.get_json()['activity_id'],
                time=request.get_json()['time']
            )
        except ValueError as e:
            return make_response({"errors": str(e)}, 400)
            

        db.session.add(new_signup)
        db.session.commit()

        return make_response(new_signup.to_dict(), 200)

api.add_resource(Signups, '/signups')
if __name__ == '__main__':
    app.run(port=5555, debug=True)
