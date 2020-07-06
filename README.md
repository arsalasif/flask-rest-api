
# Flask REST API Boilerplate

A better boilerplate for RESTful APIs using Flask.

If you have ever used Flask to build REST APIs, you'd know how cumbersome it can get. This repository aims to change that.

This repository:

1. Aims to fix common pain points with building REST APIs with Flask.
2. Uses pluggable views, blueprints, decorators and pydantic to modularize application and avoid repetition commonly associated with CRUD calls (DRY principle). [See how fast and easy it is to write APIs using this boilerplate](#guide-for-extending-this-boilerplate).
3. Doesn't use any of the Flask-RESTFul (Latest release: 2014), Flask-Restless (Latest release: 2016), or any similar spin-offs of Flask which eventually died out. Instead it relies only on core Flask. This has a huge advantage of always having the latest version of Flask for your application.


#### Tech Stack:

 - **Web framework:** Flask
 - **ORM:** SQLAlchemy
 - **Database:** PostgresSQL
 - **Parsing/Validation:** Pydantic
 - **Containerization:** Docker
 - **Async-Task Queue:** Celery
 - **Message-Broker:** RabbitMQ
 - **WSGI Server:** Gunicorn
 - **Reverse Proxy Server:** NGINX
 - **Documentation:** Swagger-UI

#### Features:

* Containerized Docker build
* Separate docker services for database (**db**), message-broker (**celery-broker**), API (**web**), and documentation (**swagger-ui**).
* Ability to run this API with a different database, or broker, or documentation service. As easy as editing docker-compose and .env files.
* Separate environments and configs for Development, Testing, and Production.
* RESTful API documentation via Swagger and visualization with Swagger UI.
* Easy to write different API versions.
* Authentication via JWT.
* Email Verification.
* OAuth for Github and Facebook.
* Parsing and Validation via Pydantic.
* Database entities integrated with SQLAlchemy.
* Tests covering each of the REST API services, with code coverage.

## Contents

* [Get Started](#get-started)
* [Testing and Coverage](#testing-and-coverage)
* [RESTful endpoints](#restful-endpoints)
* [Guide for extending this Boilerplate](#guide-for-extending-this-boilerplate)

## Get Started

#### Requirements

* Docker
* Docker Compose
* Docker Machine
* Other dependencies are listed in `requirements.txt` and are installed automatically.

Get docker: https://docs.docker.com/get-docker/

Clone all the project from this repository and move to repository folder.

Rename `.env.dev.sample` file to `.env.dev`. All environment variables are set from this file.

Make sure you set the following environment variables:

    GITHUB_CLIENT_ID
    GITHUB_CLIENT_SECRET
    FACEBOOK_CLIENT_ID
    FACEBOOK_CLIENT_SECRET
    MAIL_SERVER
    MAIL_PORT
    MAIL_USERNAME
    MAIL_PASSWORD
    MAIL_DEFAULT_SENDER

Build the images and run the containers.
```bash
docker-compose up --build
```
or if you want to run it in detached (background) mode:
```bash
docker-compose up -d --build
```
Make sure all containers are running:
```bash
docker-compose ps
```
```bash                                                                       
web
db                                                      
broker
docs
```
Check swagger API documentation through http://localhost:8000.
API is available under http://localhost:5000/v1.
You can change the default ports in `docker-compose.yml` file.

#### Database commands

Create all development db tables:

```docker
docker-compose exec web python manage.py create_db
```
Recreate all development db tables:

```docker
docker-compose exec web python manage.py recreate_db
```
Populate seed data into db:

```docker
docker-compose exec web python manage.py seed_db
```
Want to reset everything?
```docker
docker-compose down -v
docker-compose up --build
```

## Testing and Coverage

Finally test that everything works by executing the following curl command that tries to logged in using a default user created in the seed_db command: (default admin **email:** admin@arsal.me, **password:** password).

```bash
curl -X POST "http://0.0.0.0:5000/v1/auth/login" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"email\":\"admin@arsal.me\",\"password\":\"password\"}"
```
> You should get a response like this:
```bash
{
  "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MzAzODEzMTUsImlhdCI6MTUyNzc4OTMxNSwic3ViIjoxfQ.Dzf017g5Qf9Mi24AH-0X3womGW2koTY3c3cCO5p1djE",
  "message": "Successfully logged in."
}
```

Run tests using:
```docker
docker-compose exec web python manage.py test
```
> You should see an output like this:
```bash
...
...
Ensure encoding auth token works ... ok
test_model_user_passwords_are_random (test_model_user.TestUserModel)
Ensure passwords are randomly hashed ... ok
test_user_get (test_user_user.TestUserBlueprint)
Ensure get single user behaves correctly. ... ok

----------------------------------------------------------------------
Ran 80 tests in 13.335s

OK
```

Run coverage using:
```docker
docker-compose exec web python manage.py cov
```


## RESTful endpoints
Different roles: USER, ADMIN.

### Authentication
| Endpoint | HTTP Method | Result |
|:---|:---:|---|
| `/auth/register`  | `POST`  | Registers a new user  |
| `/auth/login`  | `POST`  | Login the user  |
| `/auth/logout`  | `GET`  | User logout  |
| `/auth/status`  | `GET`  | Returns the logged in user's status  |
| `/auth/password_recovery`  | `POST`  | Creates a password_recovery_hash and sends email to user |
| `/auth/password_reset`  | `PUT`  | Reset user password  |
| `/auth/password_change`  | `PUT`  | Changes user password  |
> Endpoints implementation can be found under [/project/api/v1/auth/core.py](./services/web/project/api/v1/auth/core.py).

### Social Auth
| Endpoint | HTTP Method | Result |
|:---|:---:|---|
| `/auth/facebook/login`  | `GET`  | Redirects user to Facebook to authenticate and returns API access token upon success. Works for registration and login. |
| `/auth/github/login`  | `GET`  | Redirects user to Github to authenticate and returns API access token upon success. Works for registration and login. |
> Endpoints implementation can be found under [/project/api/v1/auth/social.py](./services/web/project/api/v1/auth/social.py).

### Email Verification
|Endpoint| HTTP Method | Result |
|:---|:---:|---|
| `/email_verification`  | `PUT`  | Creates a email_token_hash and sends email with token to user |
| `/email_verification/<token>` | `GET` | Verifies email and sets email verified date |
> Endpoints implementation can be found under [/project/api/v1/auth/email_verification.py](./services/web/project/api/v1/auth/email_verification.py).

### Users
**Requires role:** ADMIN

| Endpoint | HTTP Method | Result |
|:---|:---:|---|
| `/users`  | `POST`  | Adds a new user  |
| `/users`  | `GET`  | Gets all users  |
| `/users/{user_id}`  | `GET`  | Gets the given user |
| `/users/{user_id}`  | `PUT`  | Updates the given user |
| `/users/{user_id}`  | `DELETE`  | Deletes the given user |
> Endpoints implementation can be found under [/project/api/v1/admin/users.py](./services/web/project/api/v1/admin/users.py).

### User
**Requires role:** USER

| Endpoint | HTTP Method | Result |
|:---|:---:|---|
| `/user`  | `GET`  | Get user info  |
> Endpoints implementation can be found under [/project/api/v1/user/user.py](./services/web/project/api/v1/user/user.py).


For detailed documentation including request/response data, please check the Swagger-UI at http://localhost:8000.

## Guide for extending this Boilerplate
Extending this boilerplate is very simple.
**Example:** You need to add a new API called *items* which lets normal users CRUD on their items.
1. Create `item` database model in [project/models](./services/web/project/models/).
2. Create `items.py` in [api/v1/user/](./services/web/project/api/v1/user/) folder.
	1.  See [this](./services/web/project/api/v1/admin/users.py) as an example of how-to.
	2. Create an ItemsAPI class and extend this class from BaseAPI and MethodView classes.
	3. Overwrite the CRUD methods inherited from BaseAPI. In most cases, you'll just need to use a one-liner to call the base class method with your validation model, and db class.
3. Create `items.py` in [api/v1/validations/user/](./services/web/project/api/v1/validations/user/) folder.
	1.  See [this](./services/web/project/api/v1/validations/admin/users.py) as an example of how-to.
	2. You will need knowledge of [pydantic](https://pydantic-docs.helpmanual.io/) to write validation models.
4. Create a new test file `test_user_items.py` (convention for this project) in [services/web/tests](./services/web/tests) and write your tests.

**In a nutshell**, your request data is forwarded to BaseAPI, and for POST/PUT methods, you provide validation classes which map to attributes directly in database models. Any fields you provide in your validation classes (which already exist in DB models), are automatically mapped. Moreover, the data is also validated for its type, as well as any custom validators that you define.

For admins, you will follow the same procedure, but instead use the admin folder under api/v1 and api/v1/validations.

Feel free to nudge me if you need help. I'll also improve this writeup pretty soon.
