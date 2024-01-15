SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:postgres@postgres:5432/sud'


def get_current_db(app):
    """
    Return db for current app
    :return: database
    """
    with app.app_context():
        return app.db
