from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..database import SessionLocal
from ..models import Usuario
from ..config import templates

router = APIRouter()

# Configuração para criptografar senha
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# Dependência para pegar sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependência para verificar se usuário está logado
def verificar_usuario_logado(request: Request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return usuario_id


# =========================
# TELA DE LOGIN
# =========================
@router.get("/login", response_class=HTMLResponse)
def pagina_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# =========================
# PROCESSAR LOGIN
# =========================
@router.post("/login")
def realizar_login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario or not pwd_context.verify(senha, usuario.senha_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "erro": "Email ou senha inválidos"}
        )

    # Criar sessão
    request.session["usuario_id"] = usuario.id

    return RedirectResponse(url="/dashboard", status_code=303)


# =========================
# TELA DE REGISTRO
# =========================
@router.get("/register", response_class=HTMLResponse)
def pagina_registro(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# =========================
# PROCESSAR REGISTRO
# =========================
@router.post("/register")
def realizar_registro(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()

    if usuario_existente:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "erro": "Email já cadastrado"}
        )

    senha_hash = pwd_context.hash(senha)

    novo_usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=senha_hash
    )

    db.add(novo_usuario)
    db.commit()

    return RedirectResponse(url="/login", status_code=303)


# =========================
# LOGOUT
# =========================
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# =========================
# ROTA RAIZ
# =========================
@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    usuario_id = request.session.get("usuario_id")
    if usuario_id:
        return RedirectResponse(url="/dashboard", status_code=303)
    return RedirectResponse(url="/login", status_code=303)
