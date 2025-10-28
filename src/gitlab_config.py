# Configuración del sistema de actualizaciones con GitLab

# URL de tu instancia de GitLab
GITLAB_URL = "https://gitlab-prod.star-software.net"

# ID del proyecto (formato: usuario/proyecto o grupo/proyecto)
PROJECT_ID = "amacias/starpdf"

# Token de acceso personal (requerido para repos internos)
# Para obtenerlo: GitLab → Settings → Access Tokens → Personal Access Tokens
# Permisos necesarios: read_api, read_repository
ACCESS_TOKEN = "glpat-XIxW0tFuiHBV1kpzjIfTGW86MQp1OjQH.01.0w1warukq"  # Reemplazar con tu token real

# Configuración de verificaciones automáticas
AUTO_CHECK_ON_STARTUP = True      # Verificar al iniciar la aplicación
CHECK_INTERVAL_DAYS = 7           # Verificar cada X días
SILENT_CHECK = True               # Verificación silenciosa

# Configuración de descarga
DOWNLOAD_TIMEOUT = 30             # Timeout en segundos
CHUNK_SIZE = 8192                 # Tamaño de chunk para descarga

# Configuración de assets en releases
# Los nombres de archivos que se buscarán automáticamente
INSTALLER_PATTERNS = [
    "StarPDF-*-setup.exe",  # Basado en tu setup_script.iss
    "StarPDF*.exe",
    "*setup*.exe",
    "setup.exe",
    "installer.exe"
]

# Configuración de notificaciones
SHOW_UPDATE_NOTIFICATIONS = True
SHOW_SUCCESS_MESSAGES = True
SHOW_ERROR_MESSAGES = True

# Configuración para repos internos
# Si tu repo es interno, necesitarás configurar un Access Token
PRIVATE_REPO = True  # Cambiado a True para repos internos