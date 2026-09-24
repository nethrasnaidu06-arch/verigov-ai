from .db import Base, engine
from . import models  # noqa: F401  (registers the tables)

Base.metadata.create_all(engine)
print("Database created with tables:", ", ".join(Base.metadata.tables))