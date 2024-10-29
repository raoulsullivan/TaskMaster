from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from taskmaster.models import Base

DATABASE_URL = "sqlite:///./taskmaster.sqlite"

engine = create_engine(
    DATABASE_URL,
    echo=True
)


# Listen for the SQLite connection and set PRAGMA foreign_keys=ON
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine,
                            expire_on_commit=False)

Base.metadata.create_all(bind=engine)
