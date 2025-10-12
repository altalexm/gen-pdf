import os
import sys
import logging
import logging.config
import yaml
import customtkinter as ctk
from pathlib import Path
from .modelo import ActaReunion
from .vista import Vista
from .controlador import Controlador

def get_base_path() -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent

def get_user_data_path(app_name="StarPDF") -> Path:
    app_data_path = Path(os.getenv('LOCALAPPDATA', Path.home())) / app_name
    app_data_path.mkdir(exist_ok=True)
    return app_data_path

def get_user_config_path(app_name="StarPDF") -> Path:
    user_docs = Path.home() / "Documents"
    app_config_dir = user_docs / app_name
    app_config_dir.mkdir(exist_ok=True)
    return app_config_dir / "config.yaml"

def setup_logging(log_path: Path):
    config = {
        'version': 1, 'disable_existing_loggers': False,
        'formatters': { 'standard': { 'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'}},
        'handlers': {
            'file': { 'class': 'logging.handlers.RotatingFileHandler', 'level': 'INFO', 'formatter': 'standard',
                      'filename': log_path / 'app.log', 'maxBytes': 1048576, 'backupCount': 5, 'encoding': 'utf-8' },
            'console': { 'class': 'logging.StreamHandler', 'level': 'DEBUG', 'formatter': 'standard'}},
        'loggers': { '': { 'handlers': ['file', 'console'], 'level': 'DEBUG', 'propagate': True }}
    }
    logging.config.dictConfig(config)
    logging.info("="*50)
    logging.info("INICIO DE SESIÓN DE LA APLICACIÓN")

def cargar_configuracion(base_path: Path, user_config_path: Path) -> dict:
    base_config_path = base_path / "config.yaml"
    if user_config_path.exists():
        logging.info(f"Cargando config de usuario: {user_config_path}")
        with open(user_config_path, 'r', encoding='utf-8') as f: return yaml.safe_load(f)
    elif base_config_path.exists():
        logging.warning(f"No se encontró config de usuario. Creando desde plantilla: {base_config_path}")
        with open(base_config_path, 'r', encoding='utf-8') as f: config = yaml.safe_load(f)
        try:
            with open(user_config_path, 'w', encoding='utf-8') as f: yaml.dump(config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            logging.info(f"Config de usuario creada en: {user_config_path}")
        except Exception as e:
            logging.error(f"No se pudo escribir el config de usuario: {e}")
        return config
    else:
        logging.error(f"¡CRÍTICO! No se encontró el config base en {base_config_path}.")
        return {}

def main():
    base_path = get_base_path()
    
    temp_config = {}
    if (base_path / "config.yaml").exists():
        with open(base_path / "config.yaml", 'r', encoding='utf-8') as f:
            temp_config = yaml.safe_load(f)
    
    app_name = temp_config.get('app', {}).get('app_name', 'StarPDF')
    
    user_data_path = get_user_data_path(app_name)
    user_config_path = get_user_config_path(app_name)
    
    setup_logging(user_data_path)
    
    config = cargar_configuracion(base_path, user_config_path)
    
    app_config = config.get('app', {})
    app_version = app_config.get('app_version', '?.?')
    
    ctk.set_appearance_mode(app_config.get('default_theme', 'System'))
    ctk.set_default_color_theme(app_config.get('default_color_theme', 'blue'))
    
    try:
        logging.info(f"Iniciando {app_name} v{app_version}...")
        logging.info(f"Ruta base: {base_path}")
        logging.info(f"Ruta de datos del usuario (logs): {user_data_path}")
        logging.info(f"Ruta de configuración del usuario: {user_config_path}")
        
        modelo = ActaReunion()
        vista = Vista(config, base_path)
        controlador = Controlador(modelo, vista, config, user_config_path)
        
        vista.set_controlador(controlador)
        controlador.cargar_datos_iniciales()
        
        logging.info("Mostrando la ventana principal.")
        vista.iniciar()

    except Exception as e:
        logging.critical("Error fatal no controlado al iniciar la aplicación.", exc_info=True)

if __name__ == "__main__":
    main()