# Protocolo de Gate — catalog-scraper

Versión específica del gate para este proyecto. Referencia genérica en:
`/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/PROTOCOLO_GATE.md`

---

## Apertura de fase

```bash
git checkout main
git pull origin main          # si hay remoto configurado
git checkout -b fase-{n}
```

Verificar entorno:
```bash
docker build -t catalog-scraper .    # debe buildear sin errores
```

## Cierre de fase

```bash
# 1. Todos los commits de la fase en la rama
git log --oneline main..HEAD

# 2. Tests / ejecución manual verificada
docker run --rm --env-file .env catalog-scraper --manufacturer yamaha --dry-run

# 3. Merge a main
git checkout main
git merge fase-{n} --no-ff -m "feat: fase {n} — {descripción}"
git push origin main

# 4. Limpiar rama
git branch -d fase-{n}
git push origin --delete fase-{n}
```

## Notas

- Los PDFs nunca se commitean — están en `.gitignore`
- Las credenciales van en `.env` — nunca en el repo
- No hay módulo Odoo que actualizar — el scraper es standalone
