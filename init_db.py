
if __name__ == '__main__':
    from sqlalchemy_utils import database_exists, create_database

    from models import engine, metadata

    if not database_exists(engine.url):
        create_database(engine.url)

    # Creates all tables unless they already exist
    metadata.create_all(engine)
