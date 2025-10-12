import json
import logging
import yaml
from tkinter import filedialog
from pathlib import Path
from .modelo import ActaReunion
from .vista import Vista
import customtkinter as ctk

logger = logging.getLogger(__name__)

class Controlador:
    def __init__(self, modelo: ActaReunion, vista: Vista, config: dict, user_config_path: Path):
        self.modelo = modelo
        self.vista = vista
        self.config = config
        self.user_config_path = user_config_path

    def cargar_datos_iniciales(self):
        logger.info("Cargando datos iniciales en la aplicación.")
        normas_iniciales = self.config.get('normas_predefinidas', [])
        self.modelo.datos['normas'] = normas_iniciales
        self.vista.pestaña_normas.poblar_desde_datos(normas_iniciales)

        listas_predefinidas = self.config.get('listas_predefinidas', {})
        proyectos = listas_predefinidas.get('proyectos', [])
        lugares = listas_predefinidas.get('lugares', [])
        personas = listas_predefinidas.get('personas', [])
        
        self.vista.poblar_ajustes(proyectos, lugares, personas)
        self.vista.actualizar_comboboxes(proyectos, lugares, personas)
        
        self._actualizar_vista_desde_modelo()

    def guardar_ajustes(self):
        logger.info(f"Guardando ajustes del usuario en: {self.user_config_path}")
        try:
            nuevas_listas = self.vista.obtener_datos_ajustes()
            
            if 'listas_predefinidas' not in self.config:
                self.config['listas_predefinidas'] = {}
            self.config['listas_predefinidas'].update(nuevas_listas)

            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
            self.vista.actualizar_comboboxes(
                proyectos=nuevas_listas.get('proyectos', []),
                lugares=nuevas_listas.get('lugares', []),
                personas=nuevas_listas.get('personas', [])
            )
            
            self.vista.mostrar_mensaje('info', 'Éxito', f"Los ajustes se han guardado correctamente en:\n{self.user_config_path.parent}")
            logger.info("Ajustes guardados y UI actualizada.")

        except Exception as e:
            logger.exception("Error al guardar los ajustes.")
            self.vista.mostrar_mensaje('error', 'Error', f"No se pudieron guardar los ajustes:\n{e}")

    def generar_pdf(self):
        logger.info("Iniciando proceso de generación de PDF.")
        self._actualizar_modelo_desde_vista()
        design_config = self.config.get('pdf_design', {})
        app_name = self.config.get('app', {}).get('app_name', 'StarPDF')
        nombre_sugerido = f"ACTA - {self.modelo.datos['proyecto'] or 'SinProyecto'} - {self.modelo.datos['fecha'].replace('/', '-')}.pdf"
        ruta_archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Documentos PDF", "*.pdf")], initialfile=nombre_sugerido, title="Guardar Acta como PDF")
        if not ruta_archivo:
            logger.warning("Generación de PDF cancelada."); return
        exito, mensaje = self.modelo.generar_pdf(ruta_archivo, design_config)
        if exito:
            self.vista.mostrar_mensaje('info', 'Éxito', f"PDF generado correctamente en:\n{ruta_archivo}")
        else:
            self.vista.mostrar_mensaje('error', 'Error', f"No se pudo generar el PDF:\n{mensaje}")

    def guardar_sesion(self):
        logger.info("Iniciando guardado de sesión."); self._actualizar_modelo_desde_vista()
        app_name = self.config.get('app', {}).get('app_name', 'StarPDF')
        ruta_archivo = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[(f"Sesiones {app_name}", "*.json")], title="Guardar Sesión de Acta")
        if not ruta_archivo:
            logger.warning("Guardado de sesión cancelado."); return
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f: json.dump(self.modelo.datos, f, ensure_ascii=False, indent=4)
            self.vista.mostrar_mensaje('info', 'Éxito', "La sesión se ha guardado correctamente.")
        except Exception as e:
            logger.exception("Error al guardar la sesión."); self.vista.mostrar_mensaje('error', 'Error', f"No se pudo guardar la sesión:\n{e}")

    def cargar_sesion(self):
        logger.info("Iniciando carga de sesión.")
        app_name = self.config.get('app', {}).get('app_name', 'StarPDF')
        ruta_archivo = filedialog.askopenfilename(filetypes=[(f"Sesiones {app_name}", "*.json")], title="Cargar Sesión de Acta")
        if not ruta_archivo:
            logger.warning("Carga de sesión cancelada."); return
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f: datos_cargados = json.load(f)
            self.modelo.actualizar_datos(datos_cargados)
            self._actualizar_vista_desde_modelo()
            self.vista.mostrar_mensaje('info', 'Éxito', "La sesión se ha cargado correctamente.")
        except Exception as e:
            logger.exception("Error al cargar la sesión."); self.vista.mostrar_mensaje('error', 'Error', f"No se pudo cargar la sesión:\n{e}")

    def _actualizar_modelo_desde_vista(self):
        datos_vista = {'proxima_reunion': {}, 'firmas': {'moderador': {}, 'responsable_acta': {}}}
        
        def get_value(widget):
            val = widget.get()
            return "" if isinstance(val, str) and val.startswith("-- ") else val

        for clave, widget in self.vista.entries_info.items(): datos_vista[clave] = get_value(widget)
        for clave, widget in self.vista.entries_prox.items(): datos_vista['proxima_reunion'][clave] = get_value(widget)
        for persona, campos in self.vista.entries_firmas.items():
            for clave, widget in campos.items(): datos_vista['firmas'][persona][clave] = get_value(widget)
        
        datos_vista.update({
            'normas': self.vista.pestaña_normas.obtener_datos_actuales(),
            'orden_dia': self.vista.pestaña_orden_dia.obtener_datos_actuales(),
            'desarrollos_acuerdos': self.vista.pestaña_desarrollo.obtener_datos_actuales(),
        })
        self.modelo.actualizar_datos(datos_vista)
        logger.debug("Modelo actualizado con los datos de la vista.")

    def _actualizar_vista_desde_modelo(self):
        datos_modelo = self.modelo.datos
        
        def set_value(widget, value):
            if hasattr(widget, 'set'):
                if value:
                    widget.set(value)
                elif isinstance(widget, ctk.CTkComboBox):
                    values = widget.cget('values')
                    if values:
                        widget.set(values[0])
            else:
                widget.delete(0, "end")
                if value:
                    widget.insert(0, value)

        for clave, widget in self.vista.entries_info.items(): set_value(widget, datos_modelo.get(clave, ""))
        for clave, widget in self.vista.entries_prox.items(): set_value(widget, datos_modelo.get('proxima_reunion', {}).get(clave, ""))
        for persona, campos in self.vista.entries_firmas.items():
            for clave, widget in campos.items(): set_value(widget, datos_modelo.get('firmas', {}).get(persona, {}).get(clave, ""))
        
        self.vista.pestaña_normas.poblar_desde_datos(datos_modelo.get('normas', []))
        self.vista.pestaña_orden_dia.poblar_desde_datos(datos_modelo.get('orden_dia', []))
        self.vista.pestaña_desarrollo.poblar_desde_datos(datos_modelo.get('desarrollos_acuerdos', []))
        
        logger.debug("Vista actualizada con los datos del modelo.")