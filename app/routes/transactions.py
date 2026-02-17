from fastapi import APIRouter, Request, Depends, HTTPException, Form
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
    # DADOS PARA GRÁFICOS
    # =========================

    # Gráfico 1: Receitas vs Despesas por categoria
    resultado_receitas = db.query(
        Transacao.categoria,
        func.sum(Transacao.valor)
    ).filter(
        Transacao.usuario_id == usuario_id,
        Transacao.tipo == "receita"
    ).group_by(Transacao.categoria).all()

    resultado_despesas = db.query(
        Transacao.categoria,
        func.sum(Transacao.valor)
    ).filter(
        Transacao.usuario_id == usuario_id,
        Transacao.tipo == "despesa"
    ).group_by(Transacao.categoria).all()

    # Obter todas as categorias únicas
    todas_categorias = set()
    for r in resultado_receitas:
        todas_categorias.add(r[0])
    for r in resultado_despesas:
        todas_categorias.add(r[0])
    
    todas_categorias = sorted(list(todas_categorias))

    # Mapear valores
    mapa_receitas = {r[0]: float(r[1]) for r in resultado_receitas}
    mapa_despesas = {r[0]: float(r[1]) for r in resultado_despesas}

    valores_receitas = [mapa_receitas.get(cat, 0) for cat in todas_categorias]
    valores_despesas = [mapa_despesas.get(cat, 0) for cat in todas_categorias]

    # Gráfico 2: Resumo Receitas vs Despesas
    grafico_resumo_labels = ["Receitas", "Despesas"]
    grafico_resumo_valores = [float(total_receitas), float(total_despesas)]

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
            "categorias": todas_categorias,
            "valores_receitas": valores_receitas,
            "valores_despesas": valores_despesas,
            "grafico_resumo_labels": grafico_resumo_labels,
            "grafico_resumo_valores": grafico_resumo_valores
        }
    )


    # =========================
    # ROTA PARA TRANSAÇÃO
    # =========================

@router.get("/transactions", response_class=HTMLResponse)
def pagina_transacoes(request: Request, db: Session = Depends(get_db)):

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return RedirectResponse(url="/login", status_code=303)

    transacoes = db.query(Transacao).filter(
        Transacao.usuario_id == usuario_id
    ).all()

    return templates.TemplateResponse(
        "transactions.html",
        {
            "request": request,
            "transacoes": transacoes
        }
    )



    # =========================
    # ROTA PAR NOVA TRANSAÇÃO
    # =========================

@router.get("/transactions/new", response_class=HTMLResponse)
def nova_transacao(request: Request):
    if not request.session.get("usuario_id"):
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "new_transaction.html",
        {"request": request}
    )


    # =========================
    # ROTA PARA ADICIONAR TRANSAÇÃO
    # =========================

@router.post("/transactions/add")
def adicionar_transacao(
    request: Request,
    tipo: str = Form(...),
    descricao: str = Form(...),
    valor: float = Form(...),
    categoria: str = Form(...),
    data: str = Form(...),
    db: Session = Depends(get_db)
):
    from datetime import datetime

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return RedirectResponse(url="/login", status_code=303)

    nova = Transacao(
        tipo=tipo,
        descricao=descricao,
        valor=valor,
        categoria=categoria,
        data=datetime.strptime(data, "%Y-%m-%d"),
        usuario_id=usuario_id
    )

    db.add(nova)
    db.commit()

    return RedirectResponse(url="/transactions", status_code=303)


# =========================
# ROTA PARA EDITAR TRANSAÇÃO
# =========================
@router.get("/transactions/edit/{transacao_id}", response_class=HTMLResponse)
def editar_transacao(request: Request, transacao_id: int, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return RedirectResponse(url="/login", status_code=303)

    transacao = db.query(Transacao).filter(
        Transacao.id == transacao_id,
        Transacao.usuario_id == usuario_id
    ).first()

    if not transacao:
        return RedirectResponse(url="/transactions", status_code=303)

    return templates.TemplateResponse(
        "edit_transaction.html",
        {"request": request, "transacao": transacao}
    )


# =========================
# ROTA PARA ATUALIZAR TRANSAÇÃO
# =========================
@router.post("/transactions/update/{transacao_id}")
def atualizar_transacao(
    request: Request,
    transacao_id: int,
    tipo: str = Form(...),
    descricao: str = Form(...),
    valor: float = Form(...),
    categoria: str = Form(...),
    data: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return RedirectResponse(url="/login", status_code=303)

    transacao = db.query(Transacao).filter(
        Transacao.id == transacao_id,
        Transacao.usuario_id == usuario_id
    ).first()

    if not transacao:
        return RedirectResponse(url="/transactions", status_code=303)

    transacao.tipo = tipo
    transacao.descricao = descricao
    transacao.valor = valor
    transacao.categoria = categoria
    transacao.data = datetime.strptime(data, "%Y-%m-%d")

    db.commit()

    return RedirectResponse(url="/transactions", status_code=303)


# =========================
# ROTA PARA DELETAR TRANSAÇÃO
# =========================
@router.get("/transactions/delete/{transacao_id}")
def deletar_transacao(
    request: Request,
    transacao_id: int,
    db: Session = Depends(get_db)
):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return RedirectResponse(url="/login", status_code=303)

    transacao = db.query(Transacao).filter(
        Transacao.id == transacao_id,
        Transacao.usuario_id == usuario_id
    ).first()

    if transacao:
        db.delete(transacao)
        db.commit()

    return RedirectResponse(url="/transactions", status_code=303)
