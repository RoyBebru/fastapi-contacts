from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import Date


SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:my-secret@localhost:5432/contacts_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    lastname = Column(String(100))
    email = Column(String(100))
    phone = Column(String(50))
    birthday = Column(Date)
    note = Column(String(250))
    __table_args__ = (UniqueConstraint( 'name',
                                        'lastname',
                                        'email',
                                        name='_contact_uc'),
                                      )


Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
