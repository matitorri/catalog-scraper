# Accesos y permisos

## Directorios accesibles

| Ruta | Acceso |
|---|---|
| `/Users/matiastorrilla/projects/catalog-scraper` | Completo (lectura y escritura) |
| `MEMORY.md` (raíz del proyecto) | Lectura y escritura — leer al abrir sesión, actualizar al cerrar |
| `/Users/matiastorrilla/projects/Meta-Agentic-Agency/docs/experiencias/catalog-scraper/*` | Escritura — registrar experiencias por fase |
| `/Users/matiastorrilla/projects/Meta-Agentic-Agency/operaciones/protocolos/*` | Lectura — protocolos operativos de la Agency |
| `/Users/matiastorrilla/projects/Meta-Agentic-Agency/docs/frameworks/*` | Lectura — frameworks y estándares de la Agency |

## Permisos configurados en `settings.json`

| Permiso | Uso |
|---|---|
| `Bash(git *)` | Commits, status, diff, log, branches |
| `Bash(python3 *)` | Ejecutar scripts y el pipeline |
| `Bash(pip *)` | Gestión de dependencias |
| `Edit(*)` | Edición de archivos dentro del proyecto sin aprobación manual |
| `Write(*)` | Escritura de archivos dentro del proyecto sin aprobación manual |
| `Read(operaciones/protocolos/*)` | Lectura de protocolos operativos de la Agency |
| `Read(docs/frameworks/*)` | Lectura de frameworks de la Agency |
| `Write(docs/experiencias/catalog-scraper/*)` | Escritura de experiencias por fase en la Agency |
