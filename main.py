from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess, tempfile, hashlib, os, requests

app = FastAPI(title="Rainmeter Helper Actions", version="1.0.0")

# ---------- /run ----------
class RunReq(BaseModel):
    language: str
    code: str
    stdin: str | None = None
    timeoutMs: int = 5000

@app.post("/run")
def run_code(req: RunReq):
    """
    Exécute un snippet court.
    Par sécurité on autorise python/powershell/batch (pas de réseau, timeout court).
    """
    lang = req.language.lower()
    if lang not in ("python", "powershell", "batch"):
        raise HTTPException(400, "language must be one of: python, powershell, batch")
    try:
        if lang == "python":
            cmd = ["python", "-c", req.code]
        elif lang == "powershell":
            cmd = ["pwsh", "-NoLogo", "-NoProfile", "-Command", req.code]
        else:  # batch
            cmd = ["cmd", "/c", req.code]

        proc = subprocess.run(
            cmd,
            input=(req.stdin or "").encode(),
            capture_output=True,
            timeout=max(0.1, req.timeoutMs/1000)
        )
        return {
            "stdout": proc.stdout.decode(errors="replace"),
            "stderr": proc.stderr.decode(errors="replace"),
            "exitCode": proc.returncode
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(408, "timeout")
    except Exception as e:
        raise HTTPException(500, f"execution error: {e}")

# ---------- /write ----------
class FileReq(BaseModel):
    path: str
    content: str
    overwrite: bool = True

@app.post("/write")
def file_gen(req: FileReq):
    """
    Écrit un fichier texte dans un espace temporaire isolé du serveur.
    Retourne le chemin absolu côté serveur + bytes + SHA256.
    """
    base = tempfile.gettempdir()
    safe = req.path.replace("..", "").lstrip("/\\")
    full = os.path.join(base, "rainmeter_out", safe)
    os.makedirs(os.path.dirname(full), exist_ok=True)

    if (not req.overwrite) and os.path.exists(full):
        raise HTTPException(409, "file exists")

    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(req.content)

    sha = hashlib.sha256(req.content.encode("utf-8")).hexdigest()
    return {"path": full, "bytesWritten": len(req.content.encode("utf-8")), "sha256": sha}

# ---------- /search ----------
class SearchReq(BaseModel):
    query: str
    scope: str = "manual"   # manual | forum | all
    maxResults: int = 5

@app.post("/search")
def search_docs(req: SearchReq):
    """
    Démo gratuite: lit les sitemaps docs/forum Rainmeter et filtre des URLs contenant la query.
    (Pas un moteur de recherche complet, mais suffisant pour valider une option/terme)
    """
    if req.scope not in ("manual", "forum", "all"):
        raise HTTPException(400, "scope must be manual|forum|all")

    sitemaps = []
    if req.scope in ("manual", "all"):
        sitemaps.append("https://docs.rainmeter.net/sitemap.xml")
    if req.scope in ("forum", "all"):
        sitemaps.append("https://forum.rainmeter.net/sitemap.xml")

    results = []
    for sm in sitemaps:
        try:
            r = requests.get(sm, timeout=5)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    if "<loc>" in line:
                        url = line.split("<loc>")[1].split("</loc>")[0].strip()
                        if req.query.lower() in url.lower():
                            title = url.rstrip("/").split("/")[-1].replace("-", " ").title()
                            results.append({"title": title, "url": url, "snippet": f"...{req.query}..."})
                            if len(results) >= req.maxResults:
                                return {"results": results}
        except Exception:
            pass
    return {"results": results}
