import os
from config import Config
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from datetime import datetime

from models import Actor, Movie, setup_db
from auth.auth import AuthError, requires_auth

def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(Config)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, True')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE')
        response.headers.add('Content-Type', 'application/json')
        return response
           

    @app.route('/')
    def index():
        return jsonify({
            'message': 'Reliable Casting Agency - a Udacity capstone project',
            'success': True
        })

    @app.route('/api/actors', methods=['POST'])
    def create_new_actor():
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
    def list_all_actors():
        actors = Actor.query.all()

        if actors is None or len(actors) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'actors': [actor.format() for actor in actors]
        }), 200


    @app.route('/api/actors/<int:actor_id>', methods=['GET'])
    def get_actor_by_id(actor_id):
        actor = Actor.query.get(actor_id)

        if actor is None:
            print(f'There is no actor with id {actor_id}.')
            abort(404)

        return jsonify({
            'success': True,
            'actor': actor.format()
        }), 200

    @app.route('/api/actors/<int:actor_id>', methods=['DELETE'])
    def delete_actor(actor_id):
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
    def update_actor(actor_id):
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
    def create_movie():
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
            'movies': movie.format()
        }), 201

    @app.route('/api/movies', methods=['GET'])
    def get_movies():
        movies = Movie.query.all()

        if movies is None or len(movies) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'movies': [movie.format() for movie in movies]
        }), 200


    @app.route('/api/movies/<int:movie_id>', methods=['GET'])
    def get_movie_by_id(movie_id):
        movie = Movie.query.get(movie_id)

        if movie is None:
            print(f'There is no movie with id {movie_id}.')
            abort(404)

        return jsonify({
            'success': True,
            'movies': movie.format()
        }), 200

    @app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
    def delete_movie(movie_id):
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
    def update_movie(movie_id):
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
            'movies': movie.format()
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

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)