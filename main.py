from flask import Flask
from flask_restful import Api, Resource
from flask_cors import CORS

from details_soup import UserData, UsernameError, PlatformError

app = Flask(__name__)
CORS(app)
api = Api(app)


class Details(Resource):
    def get(self, platform, username):

        user_data = UserData(username)

        try:
            return user_data.get_details(platform)

        except UsernameError:
            return {'status': 'Failed', 'details': 'Invalid username'}

        except PlatformError:
            return {'stats': 'Failed', 'details': 'Invalid Platform'}


api.add_resource(Details,'/api/<string:platform>/<string:username>')

if __name__ == '__main__':
    app.run()