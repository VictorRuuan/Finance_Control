from pydantic import BaseModel
from datetime import date
from typing import Optional


# Schemas para Usuario
class UsuarioBase(BaseModel):
    nome: str
    email: str


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioLogin(BaseModel):
    email: str
    senha: str


class Usuario(UsuarioBase):
    id: int

    class Config:
        from_attributes = True


# Schemas para Transacao
class TransacaoBase(BaseModel):
    tipo: str
    descricao: str
    valor: float
    categoria: str
    data: date


class TransacaoCreate(TransacaoBase):
    pass


class Transacao(TransacaoBase):
    id: int
    usuario_id: int

    class Config:
        from_attributes = True
