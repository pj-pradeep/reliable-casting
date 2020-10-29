import os
from config import Config
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from datetime import datetime

from flask import redirect
from flask import render_template, make_response
from flask import session
from flask import url_for

from models import Actor, Movie, setup_db
from auth.auth import *
from authlib.integrations.flask_client import OAuth
from werkzeug.exceptions import HTTPException
from six.moves.urllib.parse import urlencode


def create_app(config_file):

    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(config_file)
    setup_db(app)
    # cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app)

    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        api_base_url=AUTH0_BASE_URL,
        access_token_url=AUTH0_BASE_URL + '/oauth/token',
        authorize_url=AUTH0_BASE_URL + '/authorize',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, True')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE')
        return response
           

    @app.route('/')
    def index():
        return render_template('home.html')

    @app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)

    @app.route('/logout')
    def logout():
        session.clear()
        params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    @app.route('/callback')
    def callback_handling():
        # Handles response from token endpoint
        
        result = auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()
        token = result.get('access_token')

        # Store the user information in flask session.
        session['jwt_token'] = token
        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
               
        return redirect('/dashboard')


    @app.route('/dashboard')
    @requires_authenticated_session
    def dashboard():
        return render_template('dashboard.html',
                            userinfo=session['profile'],
                            userinfo_pretty=json.dumps(session['jwt_payload'], indent=4),
                            token=session['jwt_token'])



    @app.route('/api/actors', methods=['POST'])
    @requires_auth('post:actors')
    def create_new_actor(payload):
        request_body = request.get_json()

        if not request_body:
            print('There was no request body. Not a valid request')
            abort(400)

        name = request_body.get('name', None)
        gender = request_body.get('gender', None)
        date_of_birth = request_body.get('date_of_birth', None)

        if(name is None or gender is None or date_of_birth is None):
            print('Request body is missing mandatory fields required to add an actor.')
            abort(422)
        
        actor = Actor()
        actor.name = name
        actor.gender = gender
        actor.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()

        actor.save()

        return jsonify({
            'success': True,
            'actor': actor.format()
        }), 201


    @app.route('/api/actors', methods=['GET'])
    @requires_auth('get:actors')
    def list_all_actors(payload):
        actors = Actor.query.all()

        if actors is None or len(actors) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'actors': [actor.format() for actor in actors]
        }), 200


    @app.route('/api/actors/<int:actor_id>', methods=['GET'])
    @requires_auth('get:actors')
    def get_actor_by_id(payload, actor_id):
        actor = Actor.query.get(actor_id)

        if actor is None:
            print(f'There is no actor with id {actor_id}.')
            abort(404)

        return jsonify({
            'success': True,
            'actor': actor.format()
        }), 200

    @app.route('/api/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(payload, actor_id):
        actor = Actor.query.get(actor_id)

        if actor is None:
            print(f'There is no actor with id {actor_id}.')
            abort(404)

        actor.delete()

        return jsonify({
            'success': True,
            'deleted': actor.id
        }), 200


    @app.route('/api/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actor')
    def update_actor(payload, actor_id):
        actor = Actor.query.get(actor_id)

        if actor is None:
            print(f'There is no actor with id {actor_id}.')
            abort(404)

        request_body = request.get_json()

        if not request_body:
            print('There was no request body. Not a valid request')
            abort(400)

        name = request_body.get('name', None)
        gender = request_body.get('gender', None)
        date_of_birth = request_body.get('date_of_birth', None)

        if name:
            actor.name = name

        if gender:
            actor.gender = gender

        if date_of_birth:
            actor.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()

        actor.update()

        return jsonify({
            'success': True,
            'actor': actor.format()
        }), 200


    @app.route('/api/movies', methods=['POST'])
    @requires_auth('post:movies')
    def create_movie(payload):
        request_body = request.get_json()

        if not request_body:
            print('There was no request body. Not a valid request')
            abort(400)

        title = request_body.get('title', None)
        release_date = request_body.get('release_date', None)

        if title is None or release_date is None:
            print('Request body is missing mandatory fields required to add an actor.')
            abort(422)

        movie = Movie()
        movie.title = title
        movie.release_date = datetime.strptime(release_date, '%Y-%m-%d').date()

        movie.save()

        return jsonify({
            'success': True,
            'movie': movie.format()
        }), 201

    @app.route('/api/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies(payload):
        movies = Movie.query.all()

        if movies is None or len(movies) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'movies': [movie.format() for movie in movies]
        }), 200


    @app.route('/api/movies/<int:movie_id>', methods=['GET'])
    @requires_auth('get:movies')
    def get_movie_by_id(payload, movie_id):
        movie = Movie.query.get(movie_id)

        if movie is None:
            print(f'There is no movie with id {movie_id}.')
            abort(404)

        return jsonify({
            'success': True,
            'movies': movie.format()
        }), 200

    @app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(payload, movie_id):
        movie = Movie.query.get(movie_id)

        if movie is None:
            print(f'There is no actor with id {movie_id}.')
            abort(404)

        movie.delete()

        return jsonify({
            'success': True,
            'deleted': movie.id
        }), 200


    @app.route('/api/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movie')
    def update_movie(payload, movie_id):
        movie = Movie.query.get(movie_id)

        if movie is None:
            print(f'There is no actor with id {movie_id}.')
            abort(404)

        request_body = request.get_json()

        if not request_body:
            print('There was no request body. Not a valid request')
            abort(400)

        title = request_body.get('title', None)
        release_date = request_body.get('release_date', None)

        if title:
            movie.title = title

        if release_date:
            movie.release_date = release_date

        movie.update()

        return jsonify({
            'success': True,
            'movie': movie.format()
        }), 200


    @app.errorhandler(422)
    def unprocessable_error(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable error'
        }), 422

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not Found'
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }), 400

    
    return app

APP = create_app(Config)

@APP.errorhandler(AuthError)
def handle_auth_error(ex):
    return jsonify({
        "success": False,
        "code": ex.error['code'],
        "description": ex.error['description']
    }), ex.status_code

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)