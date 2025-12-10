import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "clientes.csv"
EXPECTED_COLUMNS = [
    "nome",
    "email",
    "telefone",
    "empresa",
    "status",
    "ultima_interacao",
    "valor_estm",
]
DEFAULT_USER = {
    "username": os.getenv("CRM_USER", "admin"),
    "password": os.getenv("CRM_PASSWORD", "admin"),
}


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-key")
app.config["SESSION_COOKIE_HTTPONLY"] = True


def ensure_data_file() -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        sample = pd.DataFrame(
            [
                {
                    "nome": "João Silva",
                    "email": "joao@exemplo.com",
                    "telefone": "+55 11 99999-0000",
                    "empresa": "Silva & Filhos",
                    "status": "Lead",
                    "ultima_interacao": "2024-05-10",
                    "valor_estm": 5500,
                },
                {
                    "nome": "Maria Santos",
                    "email": "maria@empresa.com",
                    "telefone": "+55 21 98888-1111",
                    "empresa": "TechNow",
                    "status": "Cliente",
                    "ultima_interacao": "2024-06-01",
                    "valor_estm": 12900,
                },
            ]
        )
        sample.to_csv(DATA_PATH, index=False)


def normalize_clientes(df: pd.DataFrame) -> pd.DataFrame:
    """Garantir colunas e formatos esperados na planilha."""
    normalized = df.copy()
    for col in EXPECTED_COLUMNS:
        if col not in normalized.columns:
            normalized[col] = "" if col != "valor_estm" else 0

    normalized["status"] = normalized["status"].fillna("Lead")

    normalized["valor_estm"] = (
        pd.to_numeric(normalized["valor_estm"], errors="coerce")
        .fillna(0)
        .astype(float)
    )

    normalized["ultima_interacao"] = pd.to_datetime(
        normalized["ultima_interacao"], errors="coerce"
    ).fillna(pd.Timestamp.today().normalize())
    normalized["ultima_interacao"] = normalized["ultima_interacao"].dt.strftime(
        "%Y-%m-%d"
    )

    ordered_columns = EXPECTED_COLUMNS + [
        col for col in normalized.columns if col not in EXPECTED_COLUMNS
    ]
    return normalized[ordered_columns]


def load_clientes() -> pd.DataFrame:
    ensure_data_file()
    df = pd.read_csv(DATA_PATH)
    return normalize_clientes(df)


def persist_clientes(df: pd.DataFrame) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    normalize_clientes(df).to_csv(DATA_PATH, index=False)


def calculate_metrics(df: pd.DataFrame) -> Dict[str, int]:
    por_status = df["status"].value_counts().to_dict()
    faturamento_estimado = int(df.get("valor_estm", pd.Series(dtype="float")).sum())
    retorno = {
        "total": len(df),
        "leads": por_status.get("Lead", 0),
        "prospects": por_status.get("Prospect", 0),
        "clientes": por_status.get("Cliente", 0),
        "faturamento": faturamento_estimado,
    }
    return retorno


def require_login() -> bool:
    return session.get("user") == DEFAULT_USER["username"]


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == DEFAULT_USER["username"] and password == DEFAULT_USER["password"]:
            session["user"] = username
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        flash("Usuário ou senha inválidos.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("login"))


@app.route("/")
@app.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("login"))

    df = load_clientes()
    metrics = calculate_metrics(df)
    ultimo_contatos = (
        df.sort_values(by="ultima_interacao", ascending=False)
        .head(5)
        .to_dict(orient="records")
    )
    status_series = df["status"].value_counts()
    status_labels: List[str] = status_series.index.tolist()
    status_values: List[int] = status_series.values.tolist()
    return render_template(
        "dashboard.html",
        metrics=metrics,
        clientes=ultimo_contatos,
        status_labels=status_labels,
        status_values=status_values,
    )


@app.route("/clientes/novo", methods=["POST"])
def novo_cliente():
    if not require_login():
        return redirect(url_for("login"))

    df = load_clientes()
    valor_raw = request.form.get("valor_estm")
    try:
        valor_estm = float(valor_raw) if valor_raw else 0
    except ValueError:
        valor_estm = 0
        flash("Valor estimado inválido. Usando 0.", "warning")
    novo = {
        "nome": request.form.get("nome", "").strip(),
        "email": request.form.get("email", "").strip(),
        "telefone": request.form.get("telefone", "").strip(),
        "empresa": request.form.get("empresa", "").strip(),
        "status": request.form.get("status", "Lead"),
        "ultima_interacao": request.form.get("ultima_interacao")
        or datetime.today().strftime("%Y-%m-%d"),
        "valor_estm": valor_estm,
    }
    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
    persist_clientes(df)
    flash("Contato adicionado com sucesso!", "success")
    return redirect(url_for("dashboard"))


@app.route("/clientes/upload", methods=["POST"])
def upload_clientes():
    if not require_login():
        return redirect(url_for("login"))
    uploaded = request.files.get("arquivo")
    if not uploaded or uploaded.filename == "":
        flash("Selecione um arquivo CSV.", "warning")
        return redirect(url_for("dashboard"))
    try:
        df = pd.read_csv(uploaded)
        if "nome" not in df.columns:
            raise ValueError("CSV deve conter coluna 'nome'.")
        df = normalize_clientes(df)
        persist_clientes(df)
        flash("Planilha importada com sucesso!", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Erro ao processar arquivo: {exc}", "danger")
    return redirect(url_for("dashboard"))


@app.route("/clientes/download")
def download_clientes():
    if not require_login():
        return redirect(url_for("login"))
    ensure_data_file()
    return send_file(DATA_PATH, as_attachment=True, download_name="clientes.csv")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
