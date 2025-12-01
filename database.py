from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Verifica se está no ambiente Docker
RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "0") == "1"

if RUNNING_IN_DOCKER:
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "sua_senha")
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_NAME = os.getenv("DB_NAME", "monitoramento")
else:
    # Modo local da Amanda (sem dar erro)
    DB_USER = "root"
    DB_PASS = ""
    DB_HOST = "localhost"
    DB_NAME = "monitoramento"

DATABASE_URL = f"mysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}"


try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    # Testa conexão
    with engine.connect() as conn:
        print("✅ Conectado ao banco com sucesso")
except Exception as e:
    print(f"⚠ Não foi possível conectar ao banco: {e}")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
