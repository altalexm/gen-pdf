import os
from datetime import datetime
from fpdf import FPDF
import logging

logger = logging.getLogger(__name__)

NORMAS_PREDEFINIDAS = [
    "Durante la presentación inicial, los participantes deben mantenerse en silencio, salvo que se les pida intervenir.",
    "Para abrir un debate sobre cualquier tema, se deberá presentar previamente una propuesta concreta.",
    "El debate formal se realizará únicamente en el punto designado como 'Debate abierto sobre los puntos'.",
    "El rol del moderador debe ser ejemplar. Su principal función es mantener el espacio al nivel adecuado de formalidad y estar pendiente de cualquier solicitud para hablar de los participantes."
]
REQUIRED_SIGNATURE_HEIGHT = 65

class PDF(FPDF):
    def __init__(self, company_name="", logo_path=None, watermark_path=None):
        super().__init__()
        self.company_name = company_name
        self.logo_path = logo_path
        self.watermark_path = watermark_path

    def header(self):
        # --- 1. Marca de Agua (Opcional) ---
        # Solo se dibuja si la ruta existe y no está vacía
        if self.watermark_path and os.path.exists(self.watermark_path):
            img_w = float(self.w) / 1.5
            img_h = 0 
            x_coord = (float(self.w) - img_w) / 2
            y_coord = (float(self.h) / 4) 
            self.image(self.watermark_path, x=x_coord, y=y_coord, w=img_w, h=img_h)
        
        # --- 2. Logo de la Empresa ---
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, x=self.l_margin, y=8, h=15)
        
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Acta de Reunión', border=0, ln=1, align='C')
        
        self.ln(5)
        self.line(float(self.l_margin), self.get_y(), float(self.w) - float(self.r_margin), self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        
        y_linea = self.get_y() - 3.0
        self.line(float(self.l_margin), y_linea, float(self.w) - float(self.r_margin), y_linea)
        
        self.cell(0, 10, self.company_name, 0, 0, 'L')
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

class ActaReunion:
    def __init__(self):
        self.datos = {
            'proyecto': '', 'fecha': datetime.now().strftime("%d/%m/%Y"), 'hora': '', 'lugar': '',
            'moderador': '', 'responsable_acta': '', 'normas': NORMAS_PREDEFINIDAS.copy(),
            'orden_dia': [], 'desarrollos_acuerdos': [],
            'proxima_reunion': {'fecha': '', 'hora': '', 'lugar': ''},
            'firmas': { 'moderador': {'nombre': '', 'fecha': ''}, 'responsable_acta': {'nombre': '', 'fecha': ''} }
        }

    def actualizar_datos(self, nuevos_datos: dict):
        self.datos = nuevos_datos

    def generar_pdf(self, ruta_archivo: str, design_config: dict) -> tuple[bool, str | None]:
        try:
            pdf = PDF(
                company_name=design_config.get('company_name', ''),
                logo_path=design_config.get('logo_path'),
                watermark_path=design_config.get('watermark_path')
            )
            
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=25)

            self._seccion_titulo(pdf, '1. Información Básica')
            info = self.datos
            contenido_info = (f"Proyecto: {info['proyecto']}\n"
                            f"Fecha: {info['fecha']} a las {info['hora']}\n"
                            f"Lugar: {info['lugar']}\n"
                            f"Moderador: {info['moderador']}\n"
                            f"Responsable de Acta: {info['responsable_acta']}")
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, contenido_info, border=1, align='L')
            pdf.ln(10)
            
            self._crear_seccion_lista_simple(pdf, '2. Normas de la Reunión', self.datos['normas'])
            self._crear_seccion_lista_compleja(pdf, '3. Orden del Día', self.datos['orden_dia'])
            self._crear_seccion_lista_compleja(pdf, '4. Desarrollo y Acuerdos', self.datos['desarrollos_acuerdos'])
            self._seccion_titulo(pdf, '5. Próxima Reunión Programada')
            prox = self.datos['proxima_reunion']
            contenido_prox = f"Fecha: {prox['fecha']} | Hora: {prox['hora']} | Lugar: {prox['lugar']}"
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 8, contenido_prox, border=1, align='C')
            pdf.ln(10)

            espacio_restante = float(pdf.h) - float(pdf.get_y())
            if espacio_restante < REQUIRED_SIGNATURE_HEIGHT:
                pdf.add_page()
                
            self._seccion_titulo(pdf, '6. Firmas y Validación')
            firmas = self.datos['firmas']
            
            ancho_util = float(pdf.w) - float(pdf.l_margin) - float(pdf.r_margin)
            gap = 5.0
            ancho_columna = (ancho_util - gap) / 2.0
            y_inicial = float(pdf.get_y())
            
            contenido_mod = f"\nModerador\n\nNombre: {firmas['moderador']['nombre']}\nFecha: {firmas['moderador']['fecha']}\n "
            pdf.multi_cell(ancho_columna, 8, contenido_mod, border=1, align='C')
            
            pdf.set_y(y_inicial)
            pdf.set_x(float(pdf.l_margin) + ancho_columna + gap)
            
            contenido_resp = f"\nResponsable de Acta\n\nNombre: {firmas['responsable_acta']['nombre']}\nFecha: {firmas['responsable_acta']['fecha']}\n "
            pdf.multi_cell(ancho_columna, 8, contenido_resp, border=1, align='C')

            pdf.output(ruta_archivo)
            return True, None

        except Exception as e:
            return False, str(e)

    def _seccion_titulo(self, pdf: FPDF, titulo: str):
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, titulo, border=0, ln=1, align='L')

    def _crear_seccion_lista_simple(self, pdf: FPDF, titulo: str, lista: list):
        self._seccion_titulo(pdf, titulo)
        pdf.set_font('Arial', '', 10)
        if not lista:
            pdf.cell(0, 6, "- (No hay elementos)", border=0, ln=1)
        else:
            for item in lista:
                pdf.multi_cell(0, 6, f"- {item}", ln=1)
        pdf.ln(5)
    
    def _crear_seccion_lista_compleja(self, pdf: FPDF, titulo: str, lista: list):
        self._seccion_titulo(pdf, titulo)
        if not lista:
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, "- (No hay elementos)", border=0, ln=1)
        else:
            for i, punto in enumerate(lista, 1):
                pdf.set_font('Arial', 'B', 10)
                pdf.multi_cell(0, 6, f"{i}. {punto.get('titulo', 'Sin título')}")
                pdf.set_font('Arial', '', 10)
                pdf.set_x(float(pdf.l_margin) + 5.0)
                pdf.multi_cell(0, 6, f"{punto.get('descripcion', 'Sin descripción')}")
                pdf.ln(2)
        pdf.ln(5)