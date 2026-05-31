# ============================================
# database.py - Configuração SQLite
# ============================================

from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date

DATABASE_URL = "sqlite:///./plantas.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── Modelo da tabela ──────────────────────
class PlantaDB(Base):
    __tablename__ = "plantas"

    id            = Column(Integer, primary_key=True, index=True)
    nome          = Column(String, nullable=False)
    tipo          = Column(String, nullable=False)
    data_plantio  = Column(String, nullable=False)   # formato: YYYY-MM-DD
    foto_url      = Column(String, nullable=True)    # caminho da imagem salva

# Cria a tabela se não existir
Base.metadata.create_all(bind=engine)

# Dependency para injetar sessão nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()