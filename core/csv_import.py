import pandas as pd

CANON = {
  "protocolo": ["protocolo","protocol","numero","n_protocolo"],
  "nome": ["nome","cidadao","solicitante","name"],
  "documento": ["documento","cpf","rg"],
  "assunto": ["assunto","tema","subject","categoria"],
  "status": ["status","situacao"],
  "prioridade": ["prioridade","priority"],
  "data_evento": ["data","data_evento","dt","date"],
}

def parse_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    cols = {c.strip().lower(): c for c in df.columns}

    def col_of(key):
        for a in CANON[key]:
            if a in cols: return cols[a]
        return None

    used = []
    def take(key, default=None):
        c = col_of(key)
        if c:
            used.append(c)
            return df[c]
        return default

    out = pd.DataFrame()
    out["protocolo"] = take("protocolo")
    out["nome"] = take("nome")
    out["documento"] = take("documento")
    out["assunto"] = take("assunto")

    stc = take("status")
    out["status"] = (stc.fillna("aberto").astype(str).str.lower() if stc is not None else "aberto")

    pr = take("prioridade")
    out["prioridade"] = (pr.fillna("media").astype(str).str.lower() if pr is not None else "media")

    dt = take("data_evento")
    out["data_evento"] = (pd.to_datetime(dt, errors="coerce").dt.date if dt is not None else None)

    extra = df[[c for c in df.columns if c not in set(used)]].copy()
    out["payload"] = extra.to_dict(orient="records")
    return out

