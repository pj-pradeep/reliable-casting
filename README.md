# reliable-casting

Reliable Casting is a project that models a company that is responsible for creating movies and managing and assigning actors to those movies. The application provides a REST based API to manage actors and movies within the system which simplifies and streamlines the process.

Application also uses Auth0 to authenticate and authorize users. Roles and permission tables are configured in Auth0. Access of roles is limited and includes three roles with different permissions. The JWT includes the RBAC permission claims. 

## Motivation

The project is an attempt to design and build databases for software applications, create and deploy database-backed web APIs, secure and manage user authentication and access control for an application backend. To make the API accessible over internet, the application had to be deployed to the cloud using Heroku.


## Getting Started

### Installing Dependencies

#### Python 3.8

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

- [PostgreSQL](https://www.postgresql.org/download/) The application uses PostgreSQL as the backend data store. Follow the link to install PostgreSQL for testing on your local machine

## Running the server

To access the application hosted on Heroku, you can skip this section. To run application locally, follow below steps.

From within the root project directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

The application uses Auth0 for authentication and authorization of the api calls. Set below environment variables. You will be able to find the information in your Auth0 account that was setup. For documentation on setting up Auth0, refer to https://auth0.com/docs/quickstart/spa/react#configure-auth0

```bash
createdb reliable-casting # or any databasename of your choice. Update the DB connection url in setup.sh before running
source setup.sh # this will setup all the environment variables required to run application successfully
python manage.py db upgrade # This will run the migrations and creates all the required DB tables
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## Running Unit tests

From within the root project directory first ensure you are working using your created virtual environment.

```bash
createdb reliable-casting-test
source setup.sh # this will setup all the environment variables required to run application successfully
python -m unittest # this will run all the unit tests. At the end as part of the teardown all the tables will be deleted
```

## REST API Reference

### General

* **Base URL** - The application is currently implemented to run locally under the standard port 5000. The API base url http://localhost:5000/
* **Heroku Hosted URL** - The application is also hosted on Heroku. The API base url is https://reliable-casting.herokuapp.com/. The home page of the application has instructions and login details for all 3 roles. Click on Login and use one of the credentials to get the access token
* **Authentication** - The application uses Auth0 for authentication and authorization. The application uses bearer token based authenticating and authorizing approach to give access to the REST api endpoints. From the above step, once you get the access token import the POSTMAN api collection. Update the authorization token and run the api for testing

Below are the roles that are configured and their permissions
* Casting Assistant
  * Can view actors and movies
* Casting Director - can perform all actions
  * All permissions a Casting Assistant has and
  * Add or delete an actor from the database
  * Modify actors or movies
* Executive Producer 
  * All permissions a Casting Director has and…
  * Add or delete a movie from the database

### Errors

The applicatoin uses convential HTTP response codes to indicate the success or failure of an API request. In general: Codes in 2xx range indicate success. Codes in the 4xx range indicate an error that failed given the information provided. Below json response will be returned for any failed API request:

```
{
    "success": False,
    "error": 404,
    "message": "Resource Not Found"
}
```

List of errors to expect:


Error Code | Error Message
---------- | -------------
404 | Resource Not Found
400 | Bad Request
422 | Unprocessable Error
405 | method not allowed
401 | Authorization header is expected
401 | Authorization header must be in the format Bearer token
401 | Authorization header must start with Bearer
401 | Operation not allowed. Check your permissions.
401 | Authorization malformed.
401 | token is expired
401 | incorrect claims, please check the audience adn issuer
401 | Unable to parse authentication token.
401 | Unable to find appropriate key


### API Endpoints


GET /movies
- Fetches all movies on the platform
- Request Arguments: None
- Allowed users: Executive Producer, Casting Assistant and casting Director
- Required permission (get:movies)

Sample request/response
`
curl http://127.0.0.1:5000/api/movies

{
    "movies": [
        {
            "id": 1,
            "release_date": "Fri, 01 Dec 2006 00:00:00 GMT",
            "title": "Cast Away"
        },
        {
            "id": 2,
            "release_date": "Mon, 01 Jan 2007 00:00:00 GMT",
            "title": "Oceans 11"
        }
    ],
    "success": true
}
`





Import the postman collection https://github.com/pj-pradeep/reliable-casting/blob/master/reliable-casting.postman_collection.json

The collection has all the api endpoints setup. The collection has the required authorization tokens setup. 
If the tokens have expired, we need to get new token and update PostMan for the endpoints to work
To test the end points with Postman:
1. Navigate to https://reliable-casting.herokuapp.com/ on your browser. This will load the application home page.
2. Click on the "Try Me" button to view login credentials
3. Click the "Log In to Explore" button. This will redirect to Auth0 login page.
4. Use the sample login credentials. This will redirect to dashboard page with the access token
5. Right-clicking the collection folder for corresponding role, navigate to the authorization tab, and update the JWT in the token field.
6. Run the api in the collection
