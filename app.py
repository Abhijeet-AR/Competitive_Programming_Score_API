from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)


class Details(Resource):
    def _interview_bit(self, username, platform):
        data = {'username': username, 'platform': platform.title()}

        url = 'https://www.interviewbit.com/profile/{}'.format(username)




    def get(self, platform, username):

        if platform == 'interviewbit':



            return {
                'username': username,
                'platform': platform
            }

        return '<h1>404 NOT FOUND<\h1>'


api.add_resource(Details,'/api/<string:platform>/<string:username>')

if __name__ == '__main__':
    app.run(debug=True)