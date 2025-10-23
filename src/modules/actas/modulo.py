# src/modules/actas/modulo.py

import os
from datetime import datetime
from fpdf import FPDF
import customtkinter as ctk
from src.documento_base import DocumentoBase
from src.widgets_personalizados import (
    PestañaListaDinamica, DateInput,
    TimeInput
)

class PDFActa(FPDF):
    def __init__(self, company_name="", logo_path=None):
        super().__init__()
        self.company_name = company_name
        self.logo_path = logo_path
        self.set_margins(25, 25, 25)
        self.title_color = (60, 60, 60)

    def header(self):
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, x=self.l_margin, y=15, h=12)
            self.set_y(15)

        self.set_font('Arial', 'B', 18)
        self.set_text_color(*self.title_color)
        self.cell(0, 10, 'Acta de Reunión', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.line(self.l_margin, self.get_y() - 5, self.w - self.r_margin, self.get_y() - 5)
        self.cell(0, 10, self.company_name, 0, 0, 'L')
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

class ModuloActas(DocumentoBase):
    def get_nombre(self) -> str:
        return "Acta de Reunión"

    def get_datos_iniciales(self) -> dict:
        normas = self.config.get('normas_predefinidas', [])
        return {
            'proyecto': '', 'fecha': datetime.now().strftime("%d/%m/%Y"), 'hora': '09:00', 'lugar': '',
            'moderador': '', 'responsable_acta': '', 'normas': normas.copy(),
            'orden_dia': [], 'desarrollos_acuerdos': [],
            'proxima_reunion': {'fecha': '', 'hora': '', 'lugar': ''},
            'firmas': {'moderador': {'nombre': '', 'fecha': ''}, 'responsable_acta': {'nombre': '', 'fecha': ''}}
        }

    def get_nombre_sugerido_pdf(self, datos: dict) -> str:
        fecha_str = datos.get('fecha', '').replace('/', '-')
        proyecto_str = datos.get('proyecto', 'SinTitulo')
        return f"{self.get_nombre()} - {fecha_str} - {proyecto_str}.pdf"


    def crear_frames_ui(self, parent_notebook):
        tab_info = parent_notebook.add("Info Básica")
        frame_info = ctk.CTkFrame(tab_info, fg_color="transparent")
        frame_info.pack(fill="both", expand=True, padx=10, pady=10)
        frame_info.grid_columnconfigure(1, weight=1)

        self.widgets['entries_info'] = {}
        labels_info = {'proyecto': ctk.CTkComboBox, 'fecha': DateInput, 'hora': TimeInput, 'lugar': ctk.CTkComboBox,
                       'moderador': ctk.CTkComboBox, 'responsable_acta': ctk.CTkComboBox}

        for i, (key, widget_class) in enumerate(labels_info.items()):
            label = ctk.CTkLabel(frame_info, text=f"{key.replace('_', ' ').capitalize()}:")
            label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            widget = widget_class(frame_info, values=[]) if widget_class == ctk.CTkComboBox else widget_class(frame_info)
            widget.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            self.widgets['entries_info'][key] = widget

        self.widgets['pestaña_normas'] = PestañaListaDinamica(parent_notebook, "Normas", 'simple', "Escriba aquí la norma...")
        self.widgets['pestaña_orden_dia'] = PestañaListaDinamica(parent_notebook, "Orden del Día", 'complejo')
        self.widgets['pestaña_desarrollo'] = PestañaListaDinamica(parent_notebook, "Desarrollo y Acuerdos", 'complejo')

        tab_prox = parent_notebook.add("Próxima Reunión")
        frame_prox = ctk.CTkFrame(tab_prox, fg_color="transparent")
        frame_prox.pack(fill="both", expand=True, padx=10, pady=10)
        frame_prox.grid_columnconfigure(1, weight=1)
        self.widgets['entries_prox'] = {}
        labels_prox = {'fecha': DateInput, 'hora': TimeInput, 'lugar': ctk.CTkComboBox}
        for i, (key, widget_class) in enumerate(labels_prox.items()):
            label = ctk.CTkLabel(frame_prox, text=f"{key.capitalize()}:")
            label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            widget = widget_class(frame_prox, values=[]) if widget_class == ctk.CTkComboBox else widget_class(frame_prox)
            widget.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            self.widgets['entries_prox'][key] = widget

        tab_firmas = parent_notebook.add("Firmas")
        frame_firmas = ctk.CTkFrame(tab_firmas, fg_color="transparent")
        frame_firmas.pack(fill="both", expand=True, padx=10, pady=10)
        frame_firmas.grid_columnconfigure(1, weight=1)
        self.widgets['entries_firmas'] = {}

        label_mod = ctk.CTkLabel(frame_firmas, text="Moderador", font=ctk.CTkFont(size=14, weight="bold"))
        label_mod.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        self.widgets['entries_firmas']['moderador'] = self._crear_campos_firma(frame_firmas, 1)

        label_resp = ctk.CTkLabel(frame_firmas, text="Responsable de Acta", font=ctk.CTkFont(size=14, weight="bold"))
        label_resp.grid(row=3, column=0, columnspan=2, padx=10, pady=(20,5), sticky="w")
        self.widgets['entries_firmas']['responsable_acta'] = self._crear_campos_firma(frame_firmas, 4)

    def _crear_campos_firma(self, parent_frame, start_row):
        campos = {}
        ctk.CTkLabel(parent_frame, text="Nombre:").grid(row=start_row, column=0, padx=10, pady=5, sticky="w")
        campos['nombre'] = ctk.CTkComboBox(parent_frame, values=[])
        campos['nombre'].grid(row=start_row, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(parent_frame, text="Fecha:").grid(row=start_row+1, column=0, padx=10, pady=5, sticky="w")
        campos['fecha'] = DateInput(parent_frame)
        campos['fecha'].grid(row=start_row+1, column=1, padx=10, pady=5, sticky="ew")
        return campos

    def obtener_datos_desde_ui(self) -> dict:
        datos_vista = {'proxima_reunion': {}, 'firmas': {'moderador': {}, 'responsable_acta': {}}}

        def get_value(widget):
            val = widget.get()
            return "" if isinstance(val, str) and val.startswith("-- ") else val

        for clave, widget in self.widgets['entries_info'].items(): datos_vista[clave] = get_value(widget)
        for clave, widget in self.widgets['entries_prox'].items(): datos_vista['proxima_reunion'][clave] = get_value(widget)
        for persona, campos in self.widgets['entries_firmas'].items():
            for clave, widget in campos.items(): datos_vista['firmas'][persona][clave] = get_value(widget)

        datos_vista.update({
            'normas': self.widgets['pestaña_normas'].obtener_datos_actuales(),
            'orden_dia': self.widgets['pestaña_orden_dia'].obtener_datos_actuales(),
            'desarrollos_acuerdos': self.widgets['pestaña_desarrollo'].obtener_datos_actuales(),
        })
        return datos_vista

    def poblar_ui_desde_datos(self, datos: dict):
        def set_value(widget, value):
            if hasattr(widget, 'set'):
                if value: widget.set(value)
                elif isinstance(widget, ctk.CTkComboBox):
                    values = widget.cget('values')
                    if values: widget.set(values[0])
            else:
                widget.delete(0, "end")
                if value: widget.insert(0, value)

        for clave, widget in self.widgets['entries_info'].items(): set_value(widget, datos.get(clave, ""))
        for clave, widget in self.widgets['entries_prox'].items(): set_value(widget, datos.get('proxima_reunion', {}).get(clave, ""))
        for persona, campos in self.widgets['entries_firmas'].items():
            for clave, widget in campos.items(): set_value(widget, datos.get('firmas', {}).get(persona, {}).get(clave, ""))

        self.widgets['pestaña_normas'].poblar_desde_datos(datos.get('normas', []))
        self.widgets['pestaña_orden_dia'].poblar_desde_datos(datos.get('orden_dia', []))
        self.widgets['pestaña_desarrollo'].poblar_desde_datos(datos.get('desarrollos_acuerdos', []))

    def actualizar_comboboxes(self, proyectos, lugares, personas):
        widgets_info = self.widgets.get('entries_info', {})
        if 'proyecto' in widgets_info: widgets_info['proyecto'].configure(values=proyectos)
        if 'lugar' in widgets_info: widgets_info['lugar'].configure(values=lugares)
        if 'moderador' in widgets_info: widgets_info['moderador'].configure(values=personas)
        if 'responsable_acta' in widgets_info: widgets_info['responsable_acta'].configure(values=personas)
        widgets_prox = self.widgets.get('entries_prox', {})
        if 'lugar' in widgets_prox: widgets_prox['lugar'].configure(values=lugares)
        widgets_firmas = self.widgets.get('entries_firmas', {})
        if 'moderador' in widgets_firmas: widgets_firmas['moderador']['nombre'].configure(values=personas)
        if 'responsable_acta' in widgets_firmas: widgets_firmas['responsable_acta']['nombre'].configure(values=personas)

    def generar_pdf(self, datos: dict, ruta_archivo: str) -> tuple[bool, str | None]:
        try:
            design_config = self.config.get('pdf_design', {})
            logo_path = ""
            if design_config.get('logo_path'):
                logo_path_rel = design_config.get('logo_path')
                if logo_path_rel: 
                    logo_path = str(self.base_path / logo_path_rel)

            pdf = PDFActa(
                company_name=design_config.get('company_name', ''),
                logo_path=logo_path
            )

            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=25)

            self._seccion_titulo(pdf, '1. Información Básica')
            info = datos
            info_labels = {
                'proyecto': 'Proyecto', 'fecha': 'Fecha', 'hora': 'Hora', 'lugar': 'Lugar',
                'moderador': 'Moderador', 'responsable_acta': 'Responsable de Acta'
            }
            for key, label in info_labels.items():
                if info.get(key):
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(40, 8, f"{label}:", border=0)
                    pdf.set_font('Arial', '', 10)
                    pdf.multi_cell(0, 8, info.get(key, ''))

            pdf.ln(5)

            self._crear_seccion_lista_simple(pdf, '2. Normas de la Reunión', datos.get('normas', []))
            self._crear_seccion_lista_compleja(pdf, '3. Orden del Día', datos.get('orden_dia', []))
            self._crear_seccion_lista_compleja(pdf, '4. Desarrollo y Acuerdos', datos.get('desarrollos_acuerdos', []))

            self._seccion_titulo(pdf, '5. Próxima Reunión Programada')
            prox = datos.get('proxima_reunion', {})
            contenido_prox = f"Fecha: {prox.get('fecha', '')} | Hora: {prox.get('hora', '')} | Lugar: {prox.get('lugar', '')}"
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 8, contenido_prox, border=0, align='L')
            pdf.ln(5)

            espacio_restante = float(pdf.h) - float(pdf.get_y())
            REQUIRED_SIGNATURE_HEIGHT = 65
            if espacio_restante < REQUIRED_SIGNATURE_HEIGHT:
                pdf.add_page()

            self._seccion_titulo(pdf, '6. Firmas y Validación')
            firmas = datos.get('firmas', {})
            moderador = firmas.get('moderador', {})
            responsable = firmas.get('responsable_acta', {})
            ancho_util = float(pdf.w) - float(pdf.l_margin) - float(pdf.r_margin)
            gap, ancho_columna = 5.0, (ancho_util - 5.0) / 2.0
            
            y_before_signatures = pdf.get_y()

            # Columna 1 (Moderador)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(ancho_columna, 8, f"\n\n\n\n{moderador.get('nombre', '')}\nModerador", border=0, align='C')
            pdf.line(pdf.l_margin, y_before_signatures + 24, pdf.l_margin + ancho_columna, y_before_signatures + 24)

            # Columna 2 (Responsable)
            pdf.set_y(y_before_signatures)
            pdf.set_x(pdf.l_margin + ancho_columna + gap)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(ancho_columna, 8, f"\n\n\n\n{responsable.get('nombre', '')}\nResponsable de Acta", border=0, align='C')
            x_start_resp = pdf.l_margin + ancho_columna + gap
            pdf.line(x_start_resp, y_before_signatures + 24, x_start_resp + ancho_columna, y_before_signatures + 24)

            pdf.output(str(ruta_archivo))
            return True, None
        except Exception as e:
            return False, str(e)

    def _seccion_titulo(self, pdf: FPDF, titulo: str):
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 10, titulo, 0, 1, 'L')
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 70, pdf.get_y())
        pdf.ln(5)

    def _crear_seccion_lista_simple(self, pdf: FPDF, titulo: str, lista: list):
        self._seccion_titulo(pdf, titulo)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(0, 0, 0)
        if not lista: 
            pdf.cell(0, 6, "- (No hay elementos)", 0, 1)
        else:
            for item in lista: 
                pdf.multi_cell(0, 6, f"{chr(149)} {item}")
        pdf.ln(5)
    
    def _crear_seccion_lista_compleja(self, pdf: FPDF, titulo: str, lista: list):
        self._seccion_titulo(pdf, titulo)
        pdf.set_text_color(0, 0, 0)
        if not lista: 
            pdf.cell(0, 6, "- (No hay elementos)", 0, 1)
        else:
            for i, punto in enumerate(lista, 1):
                pdf.set_font('Arial', 'B', 10)
                pdf.multi_cell(0, 6, f"{i}. {punto.get('titulo', 'Sin título')}")
                pdf.set_font('Arial', '', 10)
                pdf.set_x(float(pdf.l_margin) + 5.0)
                pdf.multi_cell(0, 6, f"{punto.get('descripcion', 'Sin descripción')}")
                pdf.ln(2)
        pdf.ln(5)