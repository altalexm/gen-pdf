# src/main.py

import os
import sys
import logging
import logging.config
import json  # Para leer configuración base
import yaml  # Para leer configuración de usuario
import customtkinter as ctk
from pathlib import Path

from .app_principal import AppPrincipal
from .controlador import Controlador

def get_base_path() -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # When frozen, first try MEIPASS (where PyInstaller extracts files)
        base_path = Path(sys._MEIPASS)
        logging.info(f"Usando MEIPASS path: {base_path}")
        return base_path
    else:
        base_path = Path(__file__).parent.parent
        logging.info(f"Usando desarrollo path: {base_path}")
        return base_path

def get_user_data_path(app_name="StarPDF") -> Path:
    app_data_path = Path(os.getenv('LOCALAPPDATA', Path.home())) / app_name
    app_data_path.mkdir(exist_ok=True)
    return app_data_path

def get_user_config_path(app_name="StarPDF") -> Path:
    user_docs = Path.home() / "Documents"
    app_config_dir = user_docs / app_name
    app_config_dir.mkdir(exist_ok=True)
    return app_config_dir / "config.json"  # El archivo sigue siendo config.json

def setup_logging(log_path: Path):
    config_log = {
        'version': 1, 'disable_existing_loggers': False,
        'formatters': { 'standard': { 'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'}},
        'handlers': {
            'file': { 'class': 'logging.handlers.RotatingFileHandler', 'level': 'INFO', 'formatter': 'standard',
                      'filename': log_path / 'app.log', 'maxBytes': 1048576, 'backupCount': 5, 'encoding': 'utf-8' },
            'console': { 'class': 'logging.StreamHandler', 'level': 'DEBUG', 'formatter': 'standard'}},
        'loggers': { '': { 'handlers': ['file', 'console'], 'level': 'DEBUG', 'propagate': True }}
    }
    logging.config.dictConfig(config_log)
    logging.info("="*50)
    logging.info("INICIO DE SESIÓN DE LA APLICACIÓN")

def cargar_configuracion(base_path_arg: Path, user_config_path_arg: Path) -> dict:
    base_config_path = base_path_arg / "config.json"  # Base sigue siendo JSON
    logging.info(f"Buscando configuración en:")
    logging.info(f"1. Usuario: {user_config_path_arg}")
    logging.info(f"2. Base: {base_config_path}")
    
    # Cargar configuración base para obtener la versión actual de la aplicación
    base_config = {}
    if base_config_path.exists():
        try:
            with open(base_config_path, 'r', encoding='utf-8') as f:
                base_config = json.load(f) or {}
        except Exception as e:
            logging.error(f"Error al leer config base: {e}")
    
    if user_config_path_arg.exists():
        logging.info(f"Cargando config de usuario: {user_config_path_arg}")
        try:
            with open(user_config_path_arg, 'r', encoding='utf-8') as f: 
                user_config = yaml.safe_load(f) or {}
            
            # Verificar si la versión de la aplicación es más nueva que la del usuario
            app_version = base_config.get('app', {}).get('app_version', '0.0.0')
            user_version = user_config.get('app', {}).get('app_version', '0.0.0')
            
            if app_version != user_version:
                logging.info(f"Actualizando versión en config de usuario: {user_version} -> {app_version}")
                # Actualizar solo la versión, mantener otras configuraciones del usuario
                if 'app' not in user_config:
                    user_config['app'] = {}
                user_config['app']['app_version'] = app_version
                
                # Guardar configuración actualizada en formato YAML
                with open(user_config_path_arg, 'w', encoding='utf-8') as f:
                    yaml.dump(user_config, f, default_flow_style=False, allow_unicode=True)
                logging.info(f"Config de usuario actualizada con nueva versión: {app_version}")
            
            return user_config
        except Exception as e:
            logging.error(f"Error al leer config de usuario: {e}")
            return {}
    elif base_config_path.exists():
        logging.info(f"Cargando config base: {base_config_path}")
        logging.warning(f"No se encontró config de usuario. Creando desde plantilla: {base_config_path}")
        try:
            # Crear config de usuario en formato YAML
            with open(user_config_path_arg, 'w', encoding='utf-8') as f: 
                yaml.dump(base_config, f, default_flow_style=False, allow_unicode=True)
            logging.info(f"Config de usuario creada en: {user_config_path_arg}")
            return base_config
        except Exception as e:
            logging.error(f"Error al procesar config: {e}")
            return {}
    else:
        logging.error(f"¡CRÍTICO! No se encontró el config base en {base_config_path}.")
        return {}

def main():
    base_path = get_base_path()
    
    base_config_path_temp = base_path / "config.json"  # Base sigue siendo JSON
    app_name = "StarPDF" 
    if base_config_path_temp.exists():
        try:
            with open(base_config_path_temp, 'r', encoding='utf-8') as f:
                temp_config = json.load(f) or {}
                app_name = temp_config.get('app', {}).get('app_name', 'StarPDF')
        except json.JSONDecodeError:
            logging.error("Error al leer la configuración inicial")
            
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
        
        vista = AppPrincipal(config, base_path)
        controlador = Controlador(vista, config, user_config_path, base_path)
        
        vista.set_controlador(controlador)
        controlador.iniciar_aplicacion()
        
        logging.info("Mostrando la ventana principal.")
        vista.iniciar()

    except Exception as e:
        logging.critical("Error fatal no controlado al iniciar la aplicación.", exc_info=True)

if __name__ == "__main__":
    main()