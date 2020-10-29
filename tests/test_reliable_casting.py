import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from config import TestingConfig

from app.app import APP, create_app
from auth.auth import AuthError
from models import setup_db, Actor, Movie, drop_db_and_create_new_db, db

from dotenv import load_dotenv, find_dotenv
from flask_migrate import upgrade, Migrate

EXECUTIVE_PRODUCER = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNtOUEydUUxdVRybWI2TVpDczNBZiJ9.eyJpc3MiOiJodHRwczovL2Rldi13cjAtZnpqOS51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWY5OTNhNTQxM2M4ZDAwMDZmM2JiYTAyIiwiYXVkIjpbImh0dHBzOi8vYXBpLnJlbGlhYmxlLWNhc3RpbmcuY29tIiwiaHR0cHM6Ly9kZXYtd3IwLWZ6ajkudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYwMzk2ODIzNywiZXhwIjoxNjA0MDU0NjM3LCJhenAiOiJydjNsbEk4QlBqUklMczhLY0I1OEVXYW9rQTRkNk5IeCIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3IiLCJkZWxldGU6bW92aWUiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9yIiwicGF0Y2g6bW92aWUiLCJwb3N0OmFjdG9ycyIsInBvc3Q6bW92aWVzIl19.rK21qP2U8r7p4qN5k1BIG6d8WND0NvkExWjFYlEqus42aPYJK344_8BwzdWNNONsogF9tD-mPEe1pZ-DBz0_-4onyddTK4eDuGsZp1gTxBACjRMpBbeuI_zmZrnQDFTF9cMoEiHDOkXcwpZ3y1nqMSI1XSiMrpPz0x_wBl1WBsKiHGg_w5mkD-ebqEHob-z6T0OBnBR3RfqiCH6zKFle4qQpVsRK2tazfyvvhuPW2udTd-d2re2D80WMVvpMqXxzDKu98_zi8qNmXhNOxvn1A9shz338mI845hWJKMoas9r9v41hbI_a-SceVTjd7hOw3JfnMxT3NjxzKPza9KO9Bg')
CASTING_DIRECTOR = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNtOUEydUUxdVRybWI2TVpDczNBZiJ9.eyJpc3MiOiJodHRwczovL2Rldi13cjAtZnpqOS51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWY5YWFiODcyOTNiY2MwMDY5NmQ2YjI3IiwiYXVkIjpbImh0dHBzOi8vYXBpLnJlbGlhYmxlLWNhc3RpbmcuY29tIiwiaHR0cHM6Ly9kZXYtd3IwLWZ6ajkudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYwMzk3MjM3MSwiZXhwIjoxNjA0MDU4NzcxLCJhenAiOiJydjNsbEk4QlBqUklMczhLY0I1OEVXYW9rQTRkNk5IeCIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6YWN0b3IiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9yIiwicGF0Y2g6bW92aWUiLCJwb3N0OmFjdG9ycyJdfQ.ZSK74HX-BlosVOIg3vQueK4gHm8pZA34N5wmnLZP3LUqpoGhtxubQZwNv6Eb69LJknlkNI8OyAeNPdzQp7f8x4xBzXim-hEbDvAwICTeLXJIjEmSnjf4sAwIclc0d5eJ7LXz0uNkps12MV8D2jc8mgUsIQaCvhL9B5xVptlgCY0P2Tj8koN-XzpDqhO44UI81ByOsB5hqFG6NmOUVmS0tVHSNXaseBjiX4eHeIK9vFAd7zErvvmQDuYCsY51GNmdg1mghXvY2CUWAGQaIGsKDKvuwYGO_tSPRrYWhxgLEM2xAY97rDcYaJaNovYVq1Dvjsy-RDP4idC4iyU2JQjwHw')
CASTING_ASSISTANT = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNtOUEydUUxdVRybWI2TVpDczNBZiJ9.eyJpc3MiOiJodHRwczovL2Rldi13cjAtZnpqOS51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWY5YWFjMTU3NWIyZjYwMDY5YWNmNWQ2IiwiYXVkIjpbImh0dHBzOi8vYXBpLnJlbGlhYmxlLWNhc3RpbmcuY29tIiwiaHR0cHM6Ly9kZXYtd3IwLWZ6ajkudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTYwMzk3MjI1MywiZXhwIjoxNjA0MDU4NjUzLCJhenAiOiJydjNsbEk4QlBqUklMczhLY0I1OEVXYW9rQTRkNk5IeCIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyJdfQ.qaArTYq2K728YKfHEMgUHW866qPaMWhI6NJWDrYT4uUBx_tlSjriVkf1pehV6jMp2H1_W2loFAMDH8QoGtIU9pOtd-_6ktlH9evnlKSnbptQG8IwhX55MlRIm6dDAilKFpsIv7YNcWTzrw0qTdMJcjvrUs9PV2cspuuXxM-CS1tz4Sn5aVeLvdm8IKHbV-92sS75-zp_O9ENkxk9KbFCZYlRwbTumSsEuT9XzNsK02cgeLfWLEcoA6SKn3iaZdSepdrDmzHPIf_cGBUyBpeiV0AqxCw7xV3kG2m_L8MCRIb9OPHtt8zpBwPRd4Grht4ADwrX8Q6qmUnUKfgPKBXAoA')

class ReliableCastingTestCase(unittest.TestCase):
    # https://blog.k-nut.eu/flask-alembic-test
    @classmethod
    def setUpClass(cls):
        APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres@localhost:5432/reliable-casting-test'
        APP.config['TESTING'] = True
        migrate = Migrate(APP, db)
        with APP.app_context():
            upgrade()   

    
    @classmethod
    def tearDownClass(cls):
        db.drop_all()
        db.engine.execute("DROP TABLE alembic_version")
    

        
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres@localhost:5432/reliable-casting-test'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client
              
        self.db = SQLAlchemy()
        self.db.init_app(self.app)
        

    def tearDown(self):
        for table in reversed(db.metadata.sorted_tables):
            db.engine.execute(table.delete())        
        db.session.commit()
        db.session.remove()
        

    #### Helper methods ###
    def create_new_actor(self):
        request_payload = {
            'name': 'Pierce Brosnan',
            'gender': 'male',
            'date_of_birth': '1965-01-01'
        }
        return self.client().post(
            '/api/actors',
            json=request_payload,
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )

    def test_post_new_actor_as_executive_producer_success(self):
        request_payload = {
            'name': 'Pierce Brosnan',
            'gender': 'male',
            'date_of_birth': '1965-01-01'
        }
        response = self.client().post(
            '/api/actors',
            json=request_payload,
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor'])
        self.assertEqual(data['actor']['name'], 'Pierce Brosnan')

    def test_post_new_actor_as_executive_producer_with_invalid_request_body_should_return_400(self):
        request_payload = {}
        response = self.client().post(
            '/api/actors',
            json=request_payload,
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_post_new_actor_as_executive_producer_with_missing_information_should_return_422(self):
        request_payload = {
            'name': 'Pierce Brosnan'
        }
        response = self.client().post(
            '/api/actors',
            json=request_payload,
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_post_new_actor_as_executive_producer_with_missing_authorization_header_should_return_401(self):
        request_payload = {
            'name': 'Pierce Brosnan',
            'gender': 'male',
            'date_of_birth': '1965-01-01'
        }
        with self.assertRaises(AuthError) as cm:
            response = self.client().post(
                '/api/actors',
                json=request_payload,
                headers={'Authorization': ''}
            )

        auth_exception = cm.exception
        self.assertEqual(auth_exception.status_code, 401)
        self.assertTrue(auth_exception.error)

    def test_post_new_actor_as_casting_assistant_return_401(self):
        request_payload = {
            'name': 'Pierce Brosnan',
            'gender': 'male',
            'date_of_birth': '1965-01-01'
        }
        with self.assertRaises(AuthError) as cm:
            response = self.client().post(
                '/api/actors',
                json=request_payload,
                headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
            )

        auth_exception = cm.exception
        self.assertEqual(auth_exception.status_code, 401)
        self.assertTrue(auth_exception.error)
        self.assertEqual(auth_exception.error['code'], 'Unauthorized Action')


    def test_get_actors_as_casting_assistant_returns_200(self):
        # first create an actor as executive producer
        new_actor = self.create_new_actor()
        
        # get actor as casting assistant
        response = self.client().get(
            '/api/actors',
            headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actors'][0]['name'], 'Pierce Brosnan')

    
    def test_get_actors_as_casting_assistant_returns_404(self):
        response = self.client().get(
            '/api/actors',
            headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_actor_by_id_returns_success(self):
        # first create an actor as executive producer
        new_actor = self.create_new_actor()
        data = json.loads(new_actor.data)
        actor_id = data['actor']['id']
        
        # get actor as casting assistant
        response = self.client().get(
            '/api/actors/' + str(actor_id),
            headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor']['name'], 'Pierce Brosnan')
        
    def test_delete_actor_as_casting_assistant_returns_auth_error(self):
        new_actor = self.create_new_actor()
        data = json.loads(new_actor.data)
        actor_id = data['actor']['id']

        with self.assertRaises(AuthError) as cm:
            response = self.client().delete(
                '/api/actors/' + str(actor_id),
                headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
            )

        auth_exception = cm.exception
        self.assertEqual(auth_exception.status_code, 401)
        self.assertTrue(auth_exception.error)
        self.assertEqual(auth_exception.error['code'], 'Unauthorized Action')

    def test_delete_actor_as_casting_director_returns_200(self):
        new_actor = self.create_new_actor()
        data = json.loads(new_actor.data)
        actor_id = data['actor']['id']

        response = self.client().delete(
                '/api/actors/' + str(actor_id),
                headers={'Authorization': f'Bearer {CASTING_DIRECTOR}'}
            )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], actor_id)

    def test_delete_actor_as_casting_director_returns_404(self):
        response = self.client().delete(
                '/api/actors/100',
                headers={'Authorization': f'Bearer {CASTING_DIRECTOR}'}
            )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)        
        

    def test_update_actor_as_casting_director_returns_200(self):
        new_actor = self.create_new_actor()
        data = json.loads(new_actor.data)
        actor_id = data['actor']['id']
        actor_name = data['actor']['name']

        request_payload = {
            'name': 'Pierce Brosnan Jr.',
            'gender': 'male',
            'date_of_birth': '1965-01-01'
        }
        
        response = self.client().patch(
                '/api/actors/' + str(actor_id),
                json=request_payload,
                headers={'Authorization': f'Bearer {CASTING_DIRECTOR}'}
            )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(data['actor']['name'], actor_name)

    def test_update_actor_as_casting_director_without_request_body_returns_400(self):
        new_actor = self.create_new_actor()
        data = json.loads(new_actor.data)
        actor_id = data['actor']['id']
        actor_name = data['actor']['name']

        request_payload = {}
        
        response = self.client().patch(
                '/api/actors/' + str(actor_id),
                json=request_payload,
                headers={'Authorization': f'Bearer {CASTING_DIRECTOR}'}
            )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)       

    def test_update_actor_as_casting_assistant_returns_auth_error(self):
        new_actor = self.create_new_actor()
        data = json.loads(new_actor.data)
        actor_id = data['actor']['id']
        actor_name = data['actor']['name']

        request_payload = {
            'name': 'Pierce Brosnan Jr.',
            'gender': 'male',
            'date_of_birth': '1965-01-01'
        }

        with self.assertRaises(AuthError) as cm:
            response = self.client().patch(
                '/api/actors/' + str(actor_id),
                json=request_payload,
                headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
            )

        auth_exception = cm.exception
        self.assertEqual(auth_exception.status_code, 401)
        self.assertTrue(auth_exception.error)
        self.assertEqual(auth_exception.error['code'], 'Unauthorized Action')

    def create_new_movie(self):
        request_payload = {
            'title': 'Cast Away',
            'release_date': '1995-01-01'
        }
        return self.client().post(
            '/api/movies',
            json=request_payload,
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )

    def test_post_new_movie_as_casting_assistant_returns_auth_error(self):
        request_payload = {
            'title': 'Cast Away',
            'release_date': '1995-01-01'
        }        

        with self.assertRaises(AuthError) as cm:
            response = self.client().post(
            '/api/movies',
            json=request_payload,
            headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
        )

        auth_exception = cm.exception
        self.assertEqual(auth_exception.status_code, 401)
        self.assertTrue(auth_exception.error)
        self.assertEqual(auth_exception.error['code'], 'Unauthorized Action')

    def test_post_new_movie_as_casting_director_returns_auth_error(self):
        request_payload = {
            'title': 'Cast Away',
            'release_date': '1995-01-01'
        }        

        with self.assertRaises(AuthError) as cm:
            response = self.client().post(
                '/api/movies',
                json=request_payload,
                headers={'Authorization': f'Bearer {CASTING_DIRECTOR}'}
            )

        auth_exception = cm.exception
        self.assertEqual(auth_exception.status_code, 401)
        self.assertTrue(auth_exception.error)
        self.assertEqual(auth_exception.error['code'], 'Unauthorized Action')

    def test_post_new_movie_as_executive_producer_returns_200(self):
        new_movie = self.create_new_movie()

        data = json.loads(new_movie.data)
        self.assertEqual(new_movie.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie'])
        self.assertEqual(data['movie']['title'], 'Cast Away')


    def test_post_new_movie_as_executive_producer_returns_400(self):
        response = self.client().post(
                '/api/movies',
                json={},
                headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
            )
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)


    def test_patch_new_movie_as_casting_assistant_returns_auth_error(self):
        new_movie = self.create_new_movie()
        
        with self.assertRaises(AuthError) as cm:
            response = self.client().patch(
                '/api/movies/23',
                json={},
                headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
            )

        auth_exception = cm.exception
        self.assertEqual(auth_exception.status_code, 401)
        self.assertTrue(auth_exception.error)
        self.assertEqual(auth_exception.error['code'], 'Unauthorized Action')

    def test_patch_movie_as_casting_director_returns_200(self):
        new_movie = self.create_new_movie()
        data = json.loads(new_movie.data)
        movie_id = data['movie']['id']
                
        response = self.client().patch(
            '/api/movies/' + str(movie_id),
            json={'title': 'test'},
            headers={'Authorization': f'Bearer {CASTING_DIRECTOR}'}
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie']['title'], 'test')
        
    def test_patch_new_movie_as_executive_director_returns_200(self):
        new_movie = self.create_new_movie()
        data = json.loads(new_movie.data)
        movie_id = data['movie']['id']

        response = self.client().patch(
                '/api/movies/' + str(movie_id),
                json={'title': 'test'},
                headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
            )
            
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie']['title'], 'test')


    def test_get_movies_returns_200_for_existing_movies(self):
        new_movie = self.create_new_movie()

        response = self.client().get(
                '/api/movies',
                headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
            )
        
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(data['success'], True)
        self.assertTrue(data['movies'][0]['title'], 'Cast Away')


    def test_get_movie_returns_404_if_movie_does_not_exist(self):
        response = self.client().get(
                '/api/movies',
                headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
            )
        
        data = json.loads(response.data)
        self.assertTrue(response.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_movie_as_casting_assistant_returns_auth_error(self):
        with self.assertRaises(AuthError) as cm:
            response = self.client().delete(
                '/api/movies/2',
                headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
            )

        auth_exception = cm.exception
        self.assertEqual(auth_exception.status_code, 401)
        self.assertTrue(auth_exception.error)
        self.assertEqual(auth_exception.error['code'], 'Unauthorized Action')

    def test_delete_movie_as_casting_director_returns_auth_error(self):
        with self.assertRaises(AuthError) as cm:
            response = self.client().delete(
                '/api/movies/2',
                headers={'Authorization': f'Bearer {CASTING_DIRECTOR}'}
            )

        auth_exception = cm.exception
        self.assertEqual(auth_exception.status_code, 401)
        self.assertTrue(auth_exception.error)
        self.assertEqual(auth_exception.error['code'], 'Unauthorized Action')

    def test_delete_movie_as_executive_producer_returns_200(self):
        new_movie = self.create_new_movie()
        data = json.loads(new_movie.data)
        movie_id = data['movie']['id']
            
        response = self.client().delete(
            '/api/movies/' + str(movie_id),
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )

        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], movie_id)