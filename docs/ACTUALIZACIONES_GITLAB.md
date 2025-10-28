# Sistema de Actualizaciones Automáticas con GitLab para StarPDF

## Configuración del Sistema

### 1. Configurar GitLab

Edita el archivo `src/gitlab_config.py`:

```python
# URL de tu instancia de GitLab
GITLAB_URL = "https://gitlab-prod.star-software.net"

# ID del proyecto (formato: usuario/proyecto)
PROJECT_ID = "amacias/starpdf"

# Token de acceso (solo para repos privados)
ACCESS_TOKEN = None  # o "glpat-xxxxxxxxxxxxxxxxxxxx"
```

### 2. Configurar Releases en GitLab

Para que funcione correctamente:

1. **Tags de versión**: `v3.0.1`, `v3.1.0`, etc.
2. **Crear Release**: GitLab → Proyecto → Releases → New Release
3. **Subir assets**: Archivos `.exe` con nombres como:
   - `StarPDF_v3.0.1_Setup.exe`
   - `StarPDF-setup.exe`
   - Cualquier `.exe` que contenga "setup"

### 3. Para Repositorios Privados

Si tu repositorio es privado, necesitas un **Personal Access Token**:

1. Ve a GitLab → Settings → Access Tokens
2. Crea un nuevo token con permisos:
   - `read_api`
   - `read_repository`
3. Copia el token y ponlo en `gitlab_config.py`:
   ```python
   ACCESS_TOKEN = "glpat-xxxxxxxxxxxxxxxxxxxx"
   ```

## Funcionamiento del Sistema

### Verificación Automática

- Se ejecuta al iniciar StarPDF
- Es silenciosa (no molesta si no hay actualizaciones)
- Configurable en `gitlab_config.py`

### Verificación Manual

- Botón "Buscar Actualizaciones" en el sidebar
- Muestra resultado incluso si no hay actualizaciones

### Diálogo de Actualización

Cuando hay actualización disponible:

- Muestra versión actual vs nueva
- Notas de la release de GitLab
- Opciones:
  - **Descargar**: Descarga automática (si hay asset)
  - **Ver en GitLab**: Abre la página de release
  - **Recordar más tarde**: Cierra el diálogo
  - **Omitir versión**: No mostrar más esta versión

## API de GitLab Utilizada

El sistema usa la **GitLab API v4**:

```
GET /api/v4/projects/:id/releases
```

### Ejemplo de respuesta:

```json
[
  {
    "tag_name": "v3.0.1",
    "description": "Correcciones de FPDF...",
    "released_at": "2025-10-28T10:00:00Z",
    "assets": {
      "links": [
        {
          "name": "StarPDF_v3.0.1_Setup.exe",
          "url": "https://gitlab.../uploads/.../setup.exe"
        }
      ]
    },
    "_links": {
      "self": "https://gitlab.../releases/v3.0.1"
    }
  }
]
```

## Flujo de Trabajo para Releases

### 1. Preparar Nueva Versión

```bash
# Actualizar versión en config.yaml
# Probar aplicación
# Compilar con PyInstaller
pyinstaller --noconfirm StarPDF.spec

# Crear instalador con Inno Setup
```

### 2. Crear Release en GitLab

```bash
# Crear y push del tag
git tag v3.0.2
git push origin v3.0.2

# En GitLab Web:
# 1. Ir a Proyecto → Releases → New Release
# 2. Seleccionar tag v3.0.2
# 3. Añadir título: "StarPDF v3.0.2"
# 4. Descripción con notas de cambios
# 5. Subir archivo StarPDF_v3.0.2_Setup.exe
# 6. Publicar release
```

### 3. Los usuarios reciben la notificación automáticamente

## Ventajas del Sistema GitLab

✅ **Integrado**: Usa tu infraestructura existente
✅ **Seguro**: Control total sobre releases y acceso
✅ **Flexible**: Funciona con repos públicos y privados
✅ **API robusta**: GitLab API es muy confiable
✅ **Assets**: Soporte completo para archivos adjuntos
✅ **Historial**: Todas las releases organizadas
✅ **Permisos**: Control granular de acceso

## Configuración Avanzada

### Personalizar patrones de archivos

En `gitlab_config.py`:

```python
INSTALLER_PATTERNS = [
    "StarPDF*.exe",
    "*setup*.exe",
    "*installer*.exe"
]
```

### Configurar timeouts

```python
DOWNLOAD_TIMEOUT = 30  # segundos
CHECK_INTERVAL_DAYS = 7  # días entre verificaciones
```

### Deshabilitar verificaciones automáticas

```python
AUTO_CHECK_ON_STARTUP = False
```

## Troubleshooting

### Error: "No se pudo verificar actualizaciones"

- Verificar conexión a internet
- Comprobar URL de GitLab en config
- Si es repo privado, verificar ACCESS_TOKEN

### Error: "No hay releases disponibles"

- Verificar que existan releases en GitLab
- Comprobar PROJECT_ID en config
- Verificar permisos de acceso al proyecto

### No se descarga automáticamente

- El sistema abrirá GitLab en el navegador
- Descargar manualmente el instalador
- Verificar que el asset sea un archivo .exe

### Repo privado no funciona

- Crear Personal Access Token
- Verificar permisos: `read_api`, `read_repository`
- Configurar ACCESS_TOKEN en gitlab_config.py

## Comparación con Alternativas

| Método               | Pros                        | Contras             |
| -------------------- | --------------------------- | ------------------- |
| **GitLab API**       | Integrado, Seguro, Completo | Requiere GitLab     |
| GitHub API           | Popular, Fácil              | Necesita GitHub     |
| Servidor propio      | Control total               | Más complejo        |
| Auto-updater externo | Especializado               | Dependencia externa |

## Seguridad

- ✅ Descargas desde HTTPS
- ✅ Verificación de versiones
- ✅ Control de acceso con tokens
- ✅ Usuario puede revisar antes de instalar
- ✅ Opción de omitir versiones
- ✅ No ejecuta código automáticamente
