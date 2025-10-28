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
        # Configuramos márgenes más conservadores para evitar problemas de espacio
        self.set_margins(20, 20, 20)  # Reducimos un poco los márgenes
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
            
            # Validamos las dimensiones del PDF antes de continuar
            ancho_util = float(pdf.w) - float(pdf.l_margin) - float(pdf.r_margin)
            alto_util = float(pdf.h) - float(pdf.t_margin) - float(pdf.b_margin)
            
            if ancho_util < 50 or alto_util < 50:
                return False, f"Error: Las dimensiones del PDF son insuficientes (ancho: {ancho_util}, alto: {alto_util})"

            self._seccion_titulo(pdf, '1. Información Básica')
            info = datos
            info_labels = {
                'proyecto': 'Proyecto', 'fecha': 'Fecha', 'hora': 'Hora', 'lugar': 'Lugar',
                'moderador': 'Moderador', 'responsable_acta': 'Responsable de Acta'
            }
            for key, label in info_labels.items():
                if info.get(key):
                    # Guardamos la posición Y actual
                    y_inicial = pdf.get_y()
                    
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(40, 8, f"{label}:", border=0)
                    pdf.set_font('Arial', '', 10)
                    
                    # Calculamos el ancho disponible para el contenido
                    ancho_disponible = pdf.w - pdf.l_margin - pdf.r_margin - 40
                    valor = str(info.get(key, ''))
                    
                    try:
                        # Posicionamos el cursor para el contenido
                        pdf.set_xy(pdf.l_margin + 40, y_inicial)
                        
                        # Intentamos usar multi_cell con el ancho calculado
                        if ancho_disponible > 20:  # Aseguramos un mínimo de espacio
                            pdf.multi_cell(ancho_disponible, 8, valor, border=0)
                        else:
                            # Si no hay suficiente espacio, usamos cell normal
                            pdf.cell(ancho_disponible, 8, valor[:50] + "..." if len(valor) > 50 else valor, border=0, ln=1)
                    except Exception:
                        # Fallback: volvemos a posición inicial y usamos cell simple
                        pdf.set_xy(pdf.l_margin + 40, y_inicial)
                        pdf.cell(0, 8, valor[:50] + "..." if len(valor) > 50 else valor, border=0, ln=1)
                    
                    # Aseguramos que estamos en la línea siguiente
                    pdf.ln(2)

            pdf.ln(5)

            self._crear_seccion_lista_simple(pdf, '2. Normas de la Reunión', datos.get('normas', []))
            self._crear_seccion_lista_compleja(pdf, '3. Orden del Día', datos.get('orden_dia', []))
            self._crear_seccion_lista_compleja(pdf, '4. Desarrollo y Acuerdos', datos.get('desarrollos_acuerdos', []))

            self._seccion_titulo(pdf, '5. Próxima Reunión Programada')
            prox = datos.get('proxima_reunion', {})
            contenido_prox = f"Fecha: {prox.get('fecha', '')} | Hora: {prox.get('hora', '')} | Lugar: {prox.get('lugar', '')}"
            pdf.set_font('Arial', '', 10)
            
            try:
                # Guardamos posición inicial y establecemos X al margen izquierdo
                y_inicial = pdf.get_y()
                pdf.set_x(pdf.l_margin)
                
                # Validamos el ancho antes de usar multi_cell
                ancho_disponible = pdf.w - pdf.l_margin - pdf.r_margin
                if ancho_disponible > 30:
                    pdf.multi_cell(ancho_disponible, 8, contenido_prox, border=0, align='L')
                else:
                    pdf.cell(0, 8, contenido_prox[:80] + "..." if len(contenido_prox) > 80 else contenido_prox, border=0, ln=1)
            except Exception:
                # Fallback: posición segura y cell normal
                pdf.set_x(pdf.l_margin)
                pdf.cell(0, 8, contenido_prox[:80] + "..." if len(contenido_prox) > 80 else contenido_prox, border=0, ln=1)
                
            pdf.ln(5)

            espacio_restante = float(pdf.h) - float(pdf.get_y())
            REQUIRED_SIGNATURE_HEIGHT = 65
            if espacio_restante < REQUIRED_SIGNATURE_HEIGHT:
                pdf.add_page()

            self._seccion_titulo(pdf, '6. Firmas y Validación')
            firmas = datos.get('firmas', {})
            moderador = firmas.get('moderador', {})
            responsable = firmas.get('responsable_acta', {})
            
            # Cálculo de anchos con validación
            ancho_util = float(pdf.w) - float(pdf.l_margin) - float(pdf.r_margin)
            gap = 10.0  # Aumentamos el gap para dar más espacio
            
            # Validamos que haya suficiente espacio para las dos columnas
            if ancho_util < 80:  # Si hay menos de 80 unidades, usar una sola columna
                # Firmas en una sola columna
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 8, "Moderador:", border=0, ln=1)
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 6, f"Nombre: {moderador.get('nombre', '')}")
                pdf.multi_cell(0, 6, f"Fecha: {moderador.get('fecha', '')}")
                pdf.ln(5)
                
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 8, "Responsable de Acta:", border=0, ln=1)
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 6, f"Nombre: {responsable.get('nombre', '')}")
                pdf.multi_cell(0, 6, f"Fecha: {responsable.get('fecha', '')}")
            else:
                # Firmas en dos columnas
                ancho_columna = (ancho_util - gap) / 2.0
                
                # Validamos que cada columna tenga un ancho mínimo razonable
                if ancho_columna < 30:
                    ancho_columna = 30
                    gap = max(5, ancho_util - (2 * ancho_columna))
                
                y_before_signatures = pdf.get_y()

                # Columna 1 (Moderador)
                pdf.set_xy(pdf.l_margin, y_before_signatures)
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(ancho_columna, 8, f"\n\n\n\n{moderador.get('nombre', '')}\nModerador", border=0, align='C')
                
                # Línea de firma para moderador
                y_linea = y_before_signatures + 24
                pdf.line(pdf.l_margin, y_linea, pdf.l_margin + ancho_columna, y_linea)

                # Columna 2 (Responsable)
                x_responsable = pdf.l_margin + ancho_columna + gap
                pdf.set_xy(x_responsable, y_before_signatures)
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(ancho_columna, 8, f"\n\n\n\n{responsable.get('nombre', '')}\nResponsable de Acta", border=0, align='C')
                
                # Línea de firma para responsable
                pdf.line(x_responsable, y_linea, x_responsable + ancho_columna, y_linea)
                
                # Nos aseguramos de posicionar el cursor después de las firmas
                pdf.set_y(y_linea + 5)

            pdf.output(str(ruta_archivo))
            return True, None
        except Exception as e:
            return False, str(e)

    def _seccion_titulo(self, pdf: FPDF, titulo: str):
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 10, titulo, 0, 1, 'L')
        
        # Guardamos posición actual para dibujar la línea correctamente
        x_actual = pdf.get_x()
        y_actual = pdf.get_y()
        
        # Dibujamos la línea decorativa
        pdf.line(pdf.l_margin, y_actual, pdf.l_margin + 70, y_actual)
        
        # Restauramos posición y continuamos
        pdf.set_xy(x_actual, y_actual)
        pdf.ln(5)

    def _crear_seccion_lista_simple(self, pdf: FPDF, titulo: str, lista: list):
        self._seccion_titulo(pdf, titulo)
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(0, 0, 0)
        if not lista: 
            pdf.cell(0, 6, "- (No hay elementos)", 0, 1)
        else:
            for item in lista: 
                # Validamos que el item no esté vacío y el ancho sea suficiente
                item_text = str(item) if item else "- (Sin contenido)"
                
                try:
                    # Guardamos la posición Y inicial
                    y_inicial = pdf.get_y()
                    
                    # Establecemos posición X al margen izquierdo
                    pdf.set_x(pdf.l_margin)
                    
                    # Calculamos el ancho disponible
                    ancho_disponible = pdf.w - pdf.l_margin - pdf.r_margin
                    
                    if ancho_disponible > 30:
                        # Usamos multi_cell con el ancho completo disponible
                        pdf.multi_cell(ancho_disponible, 6, f"{chr(149)} {item_text}", border=0)
                    else:
                        # Si hay problemas de espacio, usamos cell normal
                        pdf.cell(0, 6, f"{chr(149)} {item_text[:50]}...", 0, 1)
                        
                except Exception:
                    # Si hay problemas con multi_cell, usamos cell normal
                    pdf.set_x(pdf.l_margin)
                    pdf.cell(0, 6, f"{chr(149)} {item_text[:50]}...", 0, 1)
                
                # Pequeño espacio entre elementos
                pdf.ln(1)
        pdf.ln(5)
    
    def _crear_seccion_lista_compleja(self, pdf: FPDF, titulo: str, lista: list):
        self._seccion_titulo(pdf, titulo)
        pdf.set_text_color(0, 0, 0)
        if not lista: 
            pdf.cell(0, 6, "- (No hay elementos)", 0, 1)
        else:
            for i, punto in enumerate(lista, 1):
                try:
                    # Guardamos posición inicial
                    y_inicial = pdf.get_y()
                    
                    pdf.set_font('Arial', 'B', 10)
                    titulo_punto = punto.get('titulo', 'Sin título')
                    pdf.cell(0, 6, f"{i}. {titulo_punto}", 0, 1)
                    
                    pdf.set_font('Arial', '', 10)
                    # Establecemos correctamente la posición X con indentación
                    pdf.set_x(pdf.l_margin + 5.0)
                    descripcion_punto = punto.get('descripcion', 'Sin descripción')
                    
                    # Calculamos el ancho disponible con la indentación
                    ancho_disponible = pdf.w - pdf.l_margin - pdf.r_margin - 5.0
                    
                    if ancho_disponible > 20:
                        pdf.multi_cell(ancho_disponible, 6, descripcion_punto, border=0)
                    else:
                        pdf.cell(0, 6, descripcion_punto[:50] + "..." if len(descripcion_punto) > 50 else descripcion_punto, 0, 1)
                    
                    pdf.ln(2)
                except Exception:
                    # Si hay problemas, usamos cell normal
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(0, 6, f"{i}. {titulo_punto[:50]}...", 0, 1)
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(0, 6, f"   {descripcion_punto[:50]}...", 0, 1)
                    pdf.ln(2)
        pdf.ln(5)