# Copilot Instructions for rainmeter-actions-server

## Vue d'ensemble
Ce projet est un mini serveur FastAPI exposant trois endpoints principaux pour automatiser des tâches liées à Rainmeter :
- **POST /run** : Exécute un snippet court (Python, PowerShell, Batch) avec timeout et sans accès réseau.
- **POST /write** : Génère un fichier texte (ex : Clock.ini, .inc, .lua) dans un dossier temporaire isolé.
- **POST /search** : Recherche des URLs Rainmeter dans les sitemaps docs/forum selon une query.

## Architecture & Points clés
- **main.py** : Contient toute la logique serveur, les modèles Pydantic, et les endpoints FastAPI.
- **Endpoints** : Chaque endpoint est documenté et isolé dans une fonction dédiée.
- **Sécurité** : L'exécution de code (/run) est limitée à trois langages, sans accès réseau, avec timeout court.
- **Fichiers temporaires** : Les fichiers générés sont stockés dans un sous-dossier de l'espace temporaire du serveur (`rainmeter_out`).
- **Recherche** : La recherche lit les sitemaps XML distants, filtre les URLs contenant la query, et retourne des extraits.

## Dépendances & Démarrage
- **Dépendances** : Listées dans `requirements.txt` (FastAPI, Uvicorn, Requests).
- **Démarrage local** :
  ```powershell
  pip install -r requirements.txt
  uvicorn main:app --host 0.0.0.0 --port 10000
  ```
- **Déploiement Render** : Configuré via `render.yaml` (build et start commands).

## Conventions spécifiques
- **Endpoints REST** : Toujours POST, avec payloads typés (voir modèles Pydantic dans `main.py`).
- **Timeouts** : Par défaut 5s pour l'exécution de code.
- **Chemins de fichiers** : Nettoyés pour éviter les traversées de répertoires (`..` supprimé, slashs enlevés).
- **Réponses** : Toujours structurées (stdout, stderr, exitCode pour /run ; path, bytesWritten, sha256 pour /write ; liste d'objets pour /search).

## Exemples d'intégration
- Pour ajouter un nouveau langage à /run, adapter la logique de sélection de commande dans `run_code()`.
- Pour changer le dossier temporaire, modifier la base dans `file_gen()`.
- Pour enrichir la recherche, ajouter des sources dans la liste `sitemaps` de `search_docs()`.

## Fichiers de référence
- `main.py` : Toute la logique serveur et conventions.
- `requirements.txt` : Dépendances Python.
- `render.yaml` : Configuration Render.
- `README.md` : Résumé des endpoints et usages.

---
**Pour toute modification, respecter la structure REST, la sécurité d'exécution, et la gestion des fichiers temporaires.**
