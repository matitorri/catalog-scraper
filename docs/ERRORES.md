# Errores conocidos — catalog-scraper

---

## ERR-01 — XML-RPC no puede serializar None

**Síntoma:** `TypeError: cannot marshal None unless allow_none is enabled` al enviar el primer batch a Odoo.

**Causa:** `xmlrpc.client.ServerProxy` no serializa `None` por defecto. Los campos opcionales del schema de Odoo (ej: `serial_to`, `notes`) llegan como `None` desde el normalizer cuando no aplican.

**Solución:** `allow_none=True` en el ServerProxy del modelo:
```python
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
```

**Regla:** En cualquier cliente XML-RPC contra Odoo, siempre usar `allow_none=True` — los schemas de Odoo tienen campos opcionales y siempre habrá `None` en los payloads.

**Detectado:** Runtime — WP3, primer test contra Odoo dev.
