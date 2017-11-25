from contextlib import contextmanager

from sqlalchemy import (
    Column,
    create_engine,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker

import config


db_conf = config.get_database_config()

db_url = URL(
    drivername=db_conf.dbn,
    username=db_conf.user,
    password=db_conf.pw,
    database=db_conf.db,
)
engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
db_session = scoped_session(Session)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    query = db_session.query_property()

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))

    company_name = Column(String(length=255), nullable=True)
    phone_number = Column(String(length=255), nullable=True)
    email = Column(String(length=255), nullable=True)

    bank_name = Column(String(length=255), nullable=True)
    branch = Column(String(length=255), nullable=True)
    account_number = Column(String(length=255), nullable=True)
    btc_wallet_address = Column(String(length=255), nullable=True)

    work = relationship('Work', backref='user')


class Job(Base):
    __tablename__ = 'jobs'
    query = db_session.query_property()

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))
    rate = Column(Integer)

    invoice_address_to = Column(String(length=255), nullable=True)

    work = relationship('Work', backref='job')

    def __init__(self, name, rate, invoice_address_to=None):
        self.name = name
        self.invoice_address_to = invoice_address_to

        if rate <= 0:
            raise ValueError('rate should not be less than or equal to 0')

        self.rate = rate

    def __repr__(self):
        return '<Job(name=%s, rate=%d)>' % (self.name, self.rate)


class Work(Base):
    __tablename__ = 'work'
    query = db_session.query_property()

    id = Column(Integer, primary_key=True)
    start = Column(DateTime)
    duration = Column(Integer)

    job_id = Column(Integer, ForeignKey('jobs.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return '<Work({job.name} - {user.name})>'.format(
            job=self.job,
            user=self.user
        )


metadata = Base.metadata


@contextmanager
def sqlalchemy_db():
    try:
        yield db_session
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.commit()
