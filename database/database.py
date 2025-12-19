from sqlmodel import SQLModel, Session, create_engine 
from contextlib import contextmanager
from .config import get_settings

def get_database_engine():
    """
    Создает и настраивает SQLAlchemy engine.
    
    Returns:
        Engine: Настроенный SQLAlchemy engine
    """
    settings = get_settings()
    
    engine = create_engine(
        url=settings.DATABASE_URL_psycopg,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    return engine

engine = get_database_engine()

def get_session():
    """Получает сессию базы данных"""
    with Session(engine) as session:
        yield session
        
def init_db(drop_all: bool = False) -> None:
    """
    Инициализирует схему базы данных.
    
    Args:
        drop_all: Если True, удаляет все таблицы перед созданием
    
    Raises:
        Exception: Любое исключение, связанное с базой данных
    """
    try:
        engine = get_database_engine()
        if drop_all:
            SQLModel.metadata.drop_all(engine)
        
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        raise

