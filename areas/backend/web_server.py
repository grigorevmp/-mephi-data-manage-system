from flask import Flask, make_response, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask_sqlalchemy import SQLAlchemy

import app_db
from exceptions.exceptions import AlreadyExistsError


def create_app(testing=False, db_uri=app_db.SQLALCHEMY_DATABASE_URI):
    """
    Creating a Flask app with necessary modules
    :return: Flask app
    """
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    SWAGGER_UI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Cloud service"
        }
    )

    app = Flask(__name__)
    CORS(app, origins="http://localhost:3000", supports_credentials=True, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    app.config['TESTING'] = testing
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    with app.app_context():
        db = SQLAlchemy(app)
        app.db = db

        from rest.routes import user, admin

        app.register_blueprint(user.get_blueprint())
        app.register_blueprint(admin.get_blueprint())
        app.register_blueprint(SWAGGER_UI_BLUEPRINT, url_prefix=SWAGGER_URL)
        db.create_all()
        db.session.commit()

        # Добавление админа
        from controller.user_controller import UserController
        from core.role import Role
        user_controller = UserController()
        try:
            email = 'admin@mail.ru'
            password = 'admin'
            user_controller.registration(
                email=email,
                password=password,
                role=Role.Admin,
                username='admin'
            )
            print(f'Admin account created! Credentials: {email} / {password}')
        except AlreadyExistsError:
            print(f'Admin already exists! Credentials: {email} / {password}')

    @app.errorhandler(400)
    def handle_400_error(_error):
        """Return a http 400 error to client"""  # pragma: no cover
        return make_response(jsonify({'error': 'Misunderstood'}), 400)  # pragma: no cover

    @app.errorhandler(401)
    def handle_401_error(_error):
        """Return a http 401 error to client"""  # pragma: no cover
        return make_response(jsonify({'error': 'Unauthorised'}), 401)  # pragma: no cover

    @app.errorhandler(403)
    def handle_403_error(_error):
        """Return a http 403 error to client"""  # pragma: no cover
        return make_response(jsonify({'error': 'Forbidden'}), 403)  # pragma: no cover

    @app.errorhandler(404)
    def handle_404_error(_error):
        """Return a http 404 error to client"""  # pragma: no cover
        return make_response(jsonify({'error': 'Not found'}), 404)  # pragma: no cover

    @app.errorhandler(500)
    def handle_500_error(_error):
        """Return a http 500 error to client"""  # pragma: no cover
        return make_response(jsonify({'error': 'Server error'}), 500)  # pragma: no cover

    return app


if __name__ == '__main__':
    app = create_app()  # pragma: no cover
    app.run(host='0.0.0.0')  # pragma: no cover # TODO USE PRODUCTION SERVER
