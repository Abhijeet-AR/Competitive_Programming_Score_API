from flask import Flask, render_template
from flask_restful import Api, Resource
from flask_cors import CORS

from details_soup import UserData, UsernameError, PlatformError, BrokenChangesError
from send_mail import Mail

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
            return {'status': 'Failed', 'details': 'Invalid Platform'}
        
        except BrokenChangesError:
            return {'status': 'Failed', 'details': 'API broken due to site changes'}


api.add_resource(Details,'/api/<string:platform>/<string:username>')


@app.errorhandler(404)
def invalid_route(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run()
