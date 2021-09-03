import sqlalchemy
from .db_session import SqlAlchemyBase

class Users(SqlAlchemyBase):
    __tablename__ = "users"

    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, primary_key=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    authorized = sqlalchemy.Column(sqlalchemy.Boolean, default = False)
    day = sqlalchemy.Column(sqlalchemy.Integer,default=1)