from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal

app = FastAPI()

# ------------------------------
# Schemas des requêtes existantes
# ------------------------------

class RunReq(BaseModel):
    language: str
    code: str
    stdin: str | None = None
    timeoutMs: int = 5000

class FileReq(BaseModel):
    path: str
    content: str
    overwrite: bool = True

class SearchReq(BaseModel):
    query: str
    scope: str = "manual"
    maxResults: int = 5

# ------------------------------
# Endpoints de base (déjà existants)
# ------------------------------

@app.post("/run")
def run_code(req: RunReq):
    # Exemple simplifié
    return {"stdout": f"Executed {req.language} code", "stderr": "", "exitCode": 0}

@app.post("/write")
def file_gen(req: FileReq):
    return {"status": "written", "path": req.path}

@app.post("/search")
def search_docs(req: SearchReq):
    return {"results": [f"Found {req.query} in {req.scope}"]}

# ------------------------------
# Nouveau dispatcher unique
# ------------------------------

class ActionReq(BaseModel):
    mode: Literal["run", "write", "search"]
    language: str | None = None
    code: str | None = None
    stdin: str | None = None
    timeoutMs: int = 5000
    path: str | None = None
    content: str | None = None
    overwrite: bool = True
    query: str | None = None
    scope: str = "manual"
    maxResults: int = 5

@app.post("/action")
def dispatcher(req: ActionReq):
    """
    Dispatcher unique : appelle /run, /write ou /search
    selon le champ `mode`.
    """
    if req.mode == "run":
        return run_code(RunReq(
            language=req.language or "",
            code=req.code or "",
            stdin=req.stdin or "",
            timeoutMs=req.timeoutMs
        ))
    elif req.mode == "write":
        return file_gen(FileReq(
            path=req.path or "",
            content=req.content or "",
            overwrite=req.overwrite
        ))
    elif req.mode == "search":
        return search_docs(SearchReq(
            query=req.query or "",
            scope=req.scope,
            maxResults=req.maxResults
        ))
    else:
        raise HTTPException(status_code=400, detail="mode must be run|write|search")
