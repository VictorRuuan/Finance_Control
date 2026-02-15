from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL do banco SQLite
DATABASE_URL = "sqlite:///./finance.db"

# Criar conexão
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Criar sessão do banco
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para criação dos modelos
Base = declarative_base()
