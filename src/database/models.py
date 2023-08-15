from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import Date


Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    lastname = Column(String(100))
    email = Column(String(100), unique=True)
    phone = Column(String(50))
    birthday = Column(Date)
    note = Column(String(250))
    __table_args__ = (UniqueConstraint( 'name',
                                        'lastname',
                                        name='_contact_uc'),
                     )
