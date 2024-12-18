from models import Base
from connect_db import engine


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

