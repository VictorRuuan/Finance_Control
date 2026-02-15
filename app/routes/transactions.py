from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from ..database import SessionLocal
from ..models import Transacao
from ..config import templates

router = APIRouter()


# =========================
# DEPENDÊNCIA BANCO
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# VERIFICAR USUÁRIO LOGADO
# =========================
def verificar_usuario_logado(request: Request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return usuario_id


# =========================
# DASHBOARD
# =========================
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, usuario_id: int = Depends(verificar_usuario_logado), db: Session = Depends(get_db)):

    # =========================
    # CALCULAR TOTAIS
    # =========================

    total_receitas = db.query(func.sum(Transacao.valor)) \
        .filter(
            Transacao.usuario_id == usuario_id,
            Transacao.tipo == "receita"
        ).scalar() or 0

    total_despesas = db.query(func.sum(Transacao.valor)) \
        .filter(
            Transacao.usuario_id == usuario_id,
            Transacao.tipo == "despesa"
        ).scalar() or 0

    saldo = total_receitas - total_despesas

    # =========================
    # DADOS PARA GRÁFICO (Despesas por categoria)
    # =========================

    resultado = db.query(
        Transacao.categoria,
        func.sum(Transacao.valor)
    ).filter(
        Transacao.usuario_id == usuario_id,
        Transacao.tipo == "despesa"
    ).group_by(Transacao.categoria).all()

    labels = [r[0] for r in resultado]
    valores = [float(r[1]) for r in resultado]

    # =========================
    # RETORNAR TEMPLATE
    # =========================

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_receitas": total_receitas,
            "total_despesas": total_despesas,
            "saldo": saldo,
            "labels": labels,
            "valores": valores
        }
    )
