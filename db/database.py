from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



Base = declarative_base()
engine = None
SessionLocal = None

def perform_connection(params):
    global engine, SessionLocal
    DATABASE_URL = f"postgresql://{params['DB_USER']}:{params['DB_PASSWORD']}@{params['DB_HOST']}:{params['DB_PORT']}/{params['DB_NAME']}"

    engine = create_engine(DATABASE_URL, echo=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("Подключение к базе данных успешно")
    except Exception as exc:
        print("Ошибка при подключении к базе данных:", repr(exc))

        return False
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.bind = engine

    return True


def perform_recreate_tables():
    try:
        metadata = Base.metadata
        metadata.drop_all(bind=engine)
        metadata.create_all(bind=engine)
        print("drop_all и create_all выполнены успешно.")
        return True
    except Exception as exc:
        print("ошибка при пересоздании таблиц:", exc)
        return False


