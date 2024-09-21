from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

DATABASE_URL = "sqlite:///./taskmaster.sqlite"  

engine = create_engine(
    DATABASE_URL,
)

# Listen for the SQLite connection and set PRAGMA foreign_keys=ON
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from taskmaster.models import Base
Base.metadata.create_all(bind=engine)