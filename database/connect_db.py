from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DB_PATH = "database/affineurs.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_connection():
    with SessionLocal() as db: 
        yield db