from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)

    transacoes = relationship("Transacao", back_populates="usuario")


class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # receita ou despesa
    descricao = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    categoria = Column(String, nullable=False)
    data = Column(Date, nullable=False)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="transacoes")
