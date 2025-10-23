# src/controlador.py

import json
import logging
import yaml
import importlib
from tkinter import filedialog
from pathlib import Path
from .app_principal import AppPrincipal
from .documento_base import DocumentoBase

logger = logging.getLogger(__name__)

class Controlador:
    def __init__(self, vista: AppPrincipal, config: dict, user_config_path: Path, base_path: Path):
        self.vista = vista
        self.config = config
        self.user_config_path = user_config_path
        self.base_path = base_path
        self.modulos_cargados = {}
        self.modulo_activo: DocumentoBase | None = None

    def iniciar_aplicacion(self):
        documentos = self.config.get('documentos', [])
        for doc_config in documentos:
            modulo_nombre = doc_config.get("modulo")
            if modulo_nombre:
                self.cargar_un_modulo(modulo_nombre)
        
        self.vista.post_inicializacion()
        
        listas = self.config.get('listas_predefinidas', {})
        self.vista.poblar_ajustes(listas.get('proyectos', []), listas.get('lugares', []), listas.get('personas', []))

        self.mostrar_frame("dashboard")

    def cargar_un_modulo(self, modulo_nombre: str):
        if modulo_nombre in self.modulos_cargados:
            return self.modulos_cargados[modulo_nombre]
        try:
            modulo_python = importlib.import_module(f"src.modules.{modulo_nombre}.modulo")
            ClaseModulo = getattr(modulo_python, f"Modulo{modulo_nombre.capitalize()}")
            instancia_modulo = ClaseModulo(self.config, self.base_path)
            self.modulos_cargados[modulo_nombre] = instancia_modulo
            logger.info(f"Módulo '{modulo_nombre}' pre-cargado.")
            return instancia_modulo
        except ModuleNotFoundError:
             logger.warning(f"Módulo '{modulo_nombre}' definido en config.yaml pero no encontrado. Saltando.")
             return None
        except (ImportError, AttributeError):
            logger.error(f"Error al cargar la clase del módulo '{modulo_nombre}'.", exc_info=True)
            return None

    def modulo_existe(self, modulo_nombre: str) -> bool:
        return modulo_nombre in self.modulos_cargados and self.modulos_cargados[modulo_nombre] is not None

    def mostrar_frame(self, nombre_frame: str):
        self.modulo_activo = self.modulos_cargados.get(nombre_frame)
        self.vista.mostrar_frame(nombre_frame)
        if self.modulo_activo:
            self.cargar_datos_iniciales_modulo()

    def cargar_datos_iniciales_modulo(self):
        if not self.modulo_activo: return
        listas = self.config.get('listas_predefinidas', {})
        self.vista.actualizar_comboboxes_modulo(
            self.modulo_activo, 
            listas.get('proyectos', []), 
            listas.get('lugares', []), 
            listas.get('personas', [])
        )
        datos_iniciales = self.modulo_activo.get_datos_iniciales()
        self.modulo_activo.poblar_ui_desde_datos(datos_iniciales)

    def guardar_ajustes(self):
        logger.info(f"Guardando ajustes en: {self.user_config_path}")
        try:
            nuevas_listas = self.vista.obtener_datos_ajustes()
            if 'listas_predefinidas' not in self.config: self.config['listas_predefinidas'] = {}
            self.config['listas_predefinidas'].update(nuevas_listas)
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            for modulo in self.modulos_cargados.values():
                if modulo:
                    self.vista.actualizar_comboboxes_modulo(
                        modulo,
                        nuevas_listas.get('proyectos', []),
                        nuevas_listas.get('lugares', []),
                        nuevas_listas.get('personas', [])
                    )
            self.vista.mostrar_mensaje('info', 'Éxito', f"Ajustes guardados en:\n{self.user_config_path.parent}")
            logger.info("Ajustes guardados y UI actualizada.")
        except Exception as e:
            logger.exception("Error al guardar ajustes."); self.vista.mostrar_mensaje('error', 'Error', f"No se pudieron guardar los ajustes:\n{e}")

    def generar_pdf(self):
        if not self.modulo_activo:
            self.vista.mostrar_mensaje('warning', 'Acción no disponible', 'Por favor, seleccione un módulo de documento desde el panel lateral.')
            return
        logger.info(f"Iniciando PDF para: {self.modulo_activo.get_nombre()}")
        datos = self.modulo_activo.obtener_datos_desde_ui()
        if hasattr(self.modulo_activo, 'get_nombre_sugerido_pdf'):
            nombre_sugerido = self.modulo_activo.get_nombre_sugerido_pdf(datos)
        else:
            nombre_sugerido = f"{self.modulo_activo.get_nombre()} - {datos.get('proyecto', 'SinTitulo')}.pdf"
        ruta_archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Documentos PDF", "*.pdf")], initialfile=nombre_sugerido, title="Guardar Documento como PDF")
        if not ruta_archivo: logger.warning("Generación de PDF cancelada."); return
        exito, mensaje = self.modulo_activo.generar_pdf(datos, ruta_archivo)
        if exito: self.vista.mostrar_mensaje('info', 'Éxito', f"PDF generado correctamente en:\n{ruta_archivo}")
        else: self.vista.mostrar_mensaje('error', 'Error', f"No se pudo generar el PDF:\n{mensaje}")

    def guardar_sesion(self):
        if not self.modulo_activo:
            self.vista.mostrar_mensaje('warning', 'Acción no disponible', 'Por favor, seleccione un módulo de documento para guardar.')
            return
        logger.info("Iniciando guardado de sesión.")
        datos = self.modulo_activo.obtener_datos_desde_ui()
        app_name = self.config.get('app', {}).get('app_name', 'StarPDF')
        ruta_archivo = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[(f"Sesiones {app_name}", "*.json")], title="Guardar Sesión")
        if not ruta_archivo: logger.warning("Guardado de sesión cancelado."); return
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f: json.dump(datos, f, ensure_ascii=False, indent=4)
            self.vista.mostrar_mensaje('info', 'Éxito', "La sesión se ha guardado correctamente.")
        except Exception as e:
            logger.exception("Error al guardar sesión."); self.vista.mostrar_mensaje('error', 'Error', f"No se pudo guardar la sesión:\n{e}")

    def cargar_sesion(self):
        if not self.modulo_activo:
            self.vista.mostrar_mensaje('warning', 'Acción no disponible', 'Por favor, seleccione un módulo de documento para cargar una sesión.')
            return
        logger.info("Iniciando carga de sesión.")
        app_name = self.config.get('app', {}).get('app_name', 'StarPDF')
        ruta_archivo = filedialog.askopenfilename(filetypes=[(f"Sesiones {app_name}", "*.json")], title="Cargar Sesión")
        if not ruta_archivo: logger.warning("Carga de sesión cancelada."); return
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f: datos_cargados = json.load(f)
            self.modulo_activo.poblar_ui_desde_datos(datos_cargados)
            self.vista.mostrar_mensaje('info', 'Éxito', "La sesión se ha cargado correctamente.")
        except Exception as e:
            logger.exception("Error al cargar sesión."); self.vista.mostrar_mensaje('error', 'Error', f"No se pudo cargar la sesión:\n{e}")