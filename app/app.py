import os
from config import Config
from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import setup_db

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

    return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)