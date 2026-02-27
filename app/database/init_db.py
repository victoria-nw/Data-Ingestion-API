from app.database.session import engine
from app.database.base import Base


def init_db():
    from app.models import Order

    Base.metadata.create_all(bind=engine)
