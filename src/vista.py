import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from PIL import Image
from pathlib import Path
from .widgets_personalizados import (PestañaListaDinamica, DateInput, 
                                     TimeInput, ThemeAnimator)

class Vista(ctk.CTk):
    def __init__(self, config: dict, base_path: Path):
        super().__init__()
        self.controlador = None
        self.config = config
        self.base_path = base_path

        app_config = self.config.get('app', {})
        app_name = app_config.get('app_name', 'StarPDF')
        app_version = app_config.get('app_version', '2.5')
        self.title(f"{app_name} - Generador de Actas v{app_version}")
        
        self.geometry("950x700")
        self.minsize(850, 600)
        
        self._set_app_icon()
        self._cargar_iconos_tema()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.frame_acciones = ctk.CTkFrame(self, corner_radius=0)
        self.frame_acciones.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self._crear_acciones_globales()
        self.notebook = ctk.CTkTabview(self, anchor="nw")
        self.notebook.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self._crear_pestaña_info_basica()
        self.pestaña_normas = PestañaListaDinamica(self.notebook, "Normas", 'simple', "Escriba aquí la norma...")
        self.pestaña_orden_dia = PestañaListaDinamica(self.notebook, "Orden del Día", 'complejo')
        self.pestaña_desarrollo = PestañaListaDinamica(self.notebook, "Desarrollo y Acuerdos", 'complejo')
        self._crear_pestaña_proxima_reunion()
        self._crear_pestaña_firmas()
        self._crear_pestaña_ajustes()

    def _set_app_icon(self):
        try:
            icon_path_rel = self.config.get('app', {}).get('app_icon')
            if icon_path_rel:
                icon_path_abs = self.base_path / icon_path_rel
                if icon_path_abs.exists():
                    self.iconbitmap(str(icon_path_abs))
                else:
                    print(f"Advertencia: No se encontró el archivo de icono en: {icon_path_abs}")
        except Exception as e:
            print(f"Error al establecer el icono de la aplicación: {e}")

    def _cargar_iconos_tema(self):
        try:
            app_config = self.config.get('app', {})
            path_sun = self.base_path / app_config.get('icon_sun')
            path_moon = self.base_path / app_config.get('icon_moon')
            
            self.icon_sun = ctk.CTkImage(Image.open(path_sun), size=(24, 24))
            self.icon_moon = ctk.CTkImage(Image.open(path_moon), size=(24, 24))
        except Exception as e:
            print(f"Error al cargar iconos de tema: {e}. Usando emojis."); self.icon_sun, self.icon_moon = None, None

    def set_controlador(self, controlador):
        self.controlador = controlador
        self.btn_guardar_sesion.configure(command=self.controlador.guardar_sesion)
        self.btn_cargar_sesion.configure(command=self.controlador.cargar_sesion)
        self.btn_generar_pdf.configure(command=self.controlador.generar_pdf)
        self.btn_guardar_ajustes.configure(command=self.controlador.guardar_ajustes)

    def _crear_acciones_globales(self):
        self.btn_guardar_sesion = ctk.CTkButton(self.frame_acciones, text="Guardar Sesión")
        self.btn_guardar_sesion.pack(side="left", padx=(10, 5), pady=10)
        self.btn_cargar_sesion = ctk.CTkButton(self.frame_acciones, text="Cargar Sesión")
        self.btn_cargar_sesion.pack(side="left", padx=5, pady=10)
        self.btn_generar_pdf = ctk.CTkButton(self.frame_acciones, text="Generar PDF", font=ctk.CTkFont(weight="bold"))
        self.btn_generar_pdf.pack(side="left", padx=5, pady=10)
        
        initial_icon = self.icon_moon if ctk.get_appearance_mode() == "Dark" else self.icon_sun
        self.btn_theme = ctk.CTkButton(self.frame_acciones, text="", image=initial_icon, width=40,
                                       fg_color="transparent", hover_color=("gray70", "gray30"),
                                       command=self.toggle_theme_with_animation)
        if not self.icon_sun:
            initial_text = "🌙" if ctk.get_appearance_mode() == "Dark" else "☀️"
            self.btn_theme.configure(text=initial_text, image=None)
        
        self.btn_theme.pack(side="right", padx=10, pady=10)

    def toggle_theme_with_animation(self):
        new_theme = "Light" if ctk.get_appearance_mode() == "Dark" else "Dark"
        def on_animation_finish():
            icon = self.icon_moon if new_theme == "Dark" else self.icon_sun
            text = "🌙" if new_theme == "Dark" else "☀️"
            self.btn_theme.configure(image=icon, text="" if icon else text)
        animator = ThemeAnimator(self)
        animator.run(new_theme, on_finish_callback=on_animation_finish)

    def _crear_pestaña_info_basica(self):
        tab = self.notebook.add("Info Básica")
        frame_info = ctk.CTkFrame(tab, fg_color="transparent")
        frame_info.pack(fill="both", expand=True, padx=10, pady=10)
        frame_info.grid_columnconfigure(1, weight=1)
        self.entries_info = {}
        labels = {'proyecto': ctk.CTkComboBox, 'fecha': DateInput, 'hora': TimeInput, 'lugar': ctk.CTkComboBox, 
                  'moderador': ctk.CTkComboBox, 'responsable_acta': ctk.CTkComboBox}
        for i, (key, widget_class) in enumerate(labels.items()):
            label = ctk.CTkLabel(frame_info, text=f"{key.replace('_', ' ').capitalize()}:")
            label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            widget = widget_class(frame_info, values=[]) if widget_class == ctk.CTkComboBox else widget_class(frame_info)
            widget.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            self.entries_info[key] = widget
        self.entries_info['fecha'].set(datetime.now().strftime("%d/%m/%Y"))

    def _crear_pestaña_proxima_reunion(self):
        tab = self.notebook.add("Próxima Reunión")
        frame_prox = ctk.CTkFrame(tab, fg_color="transparent")
        frame_prox.pack(fill="both", expand=True, padx=10, pady=10)
        frame_prox.grid_columnconfigure(1, weight=1)
        self.entries_prox = {}
        labels = {'fecha': DateInput, 'hora': TimeInput, 'lugar': ctk.CTkComboBox}
        for i, (key, widget_class) in enumerate(labels.items()):
            label = ctk.CTkLabel(frame_prox, text=f"{key.capitalize()}:")
            label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            widget = widget_class(frame_prox, values=[]) if widget_class == ctk.CTkComboBox else widget_class(frame_prox)
            widget.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            self.entries_prox[key] = widget

    def _crear_pestaña_firmas(self):
        tab = self.notebook.add("Firmas")
        frame_firmas = ctk.CTkFrame(tab, fg_color="transparent")
        frame_firmas.pack(fill="both", expand=True, padx=10, pady=10)
        frame_firmas.grid_columnconfigure(1, weight=1)
        self.entries_firmas = {}
        label_mod = ctk.CTkLabel(frame_firmas, text="Moderador", font=ctk.CTkFont(size=14, weight="bold"))
        label_mod.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        self.entries_firmas['moderador'] = self._crear_campos_firma(frame_firmas, 1)
        label_resp = ctk.CTkLabel(frame_firmas, text="Responsable de Acta", font=ctk.CTkFont(size=14, weight="bold"))
        label_resp.grid(row=3, column=0, columnspan=2, padx=10, pady=(20,5), sticky="w")
        self.entries_firmas['responsable_acta'] = self._crear_campos_firma(frame_firmas, 4)

    def _crear_campos_firma(self, parent_frame, start_row):
        campos = {}
        ctk.CTkLabel(parent_frame, text="Nombre:").grid(row=start_row, column=0, padx=10, pady=5, sticky="w")
        campos['nombre'] = ctk.CTkComboBox(parent_frame, values=[])
        campos['nombre'].grid(row=start_row, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(parent_frame, text="Fecha:").grid(row=start_row+1, column=0, padx=10, pady=5, sticky="w")
        campos['fecha'] = DateInput(parent_frame)
        campos['fecha'].grid(row=start_row+1, column=1, padx=10, pady=5, sticky="ew")
        return campos
        
    def _crear_pestaña_ajustes(self):
        tab_ajustes = self.notebook.add("Ajustes")
        frame_ajustes = ctk.CTkFrame(tab_ajustes, fg_color="transparent")
        frame_ajustes.pack(fill="both", expand=True)
        notebook_ajustes = ctk.CTkTabview(frame_ajustes, anchor="nw")
        notebook_ajustes.pack(fill="both", expand=True, padx=10, pady=10)
        self.pestaña_ajustes_proyectos = PestañaListaDinamica(notebook_ajustes, "Proyectos", 'simple', "Nombre del nuevo proyecto...")
        self.pestaña_ajustes_lugares = PestañaListaDinamica(notebook_ajustes, "Lugares", 'simple', "Nombre del nuevo lugar...")
        self.pestaña_ajustes_personas = PestañaListaDinamica(notebook_ajustes, "Personas", 'simple', "Nombre de la nueva persona...")
        self.btn_guardar_ajustes = ctk.CTkButton(frame_ajustes, text="Guardar Ajustes", font=ctk.CTkFont(weight="bold"))
        self.btn_guardar_ajustes.pack(pady=(0, 10), padx=10, side="bottom", fill="x")

    def poblar_ajustes(self, proyectos, lugares, personas):
        self.pestaña_ajustes_proyectos.poblar_desde_datos(proyectos)
        self.pestaña_ajustes_lugares.poblar_desde_datos(lugares)
        self.pestaña_ajustes_personas.poblar_desde_datos(personas)

    def actualizar_comboboxes(self, proyectos, lugares, personas):
        placeholder_proy = ["-- Selecciona un Proyecto --"] + proyectos
        placeholder_lugar = ["-- Selecciona un Lugar --"] + lugares
        placeholder_pers = ["-- Selecciona una Persona --"] + personas
        self.entries_info['proyecto'].configure(values=placeholder_proy)
        self.entries_info['lugar'].configure(values=placeholder_lugar)
        self.entries_prox['lugar'].configure(values=placeholder_lugar)
        self.entries_info['moderador'].configure(values=placeholder_pers)
        self.entries_info['responsable_acta'].configure(values=placeholder_pers)
        self.entries_firmas['moderador']['nombre'].configure(values=placeholder_pers)
        self.entries_firmas['responsable_acta']['nombre'].configure(values=placeholder_pers)
        
    def obtener_datos_ajustes(self):
        return {
            'proyectos': self.pestaña_ajustes_proyectos.obtener_datos_actuales(),
            'lugares': self.pestaña_ajustes_lugares.obtener_datos_actuales(),
            'personas': self.pestaña_ajustes_personas.obtener_datos_actuales()
        }
        
    def mostrar_mensaje(self, tipo, titulo, mensaje):
        if tipo == 'info': messagebox.showinfo(titulo, mensaje)
        elif tipo == 'error': messagebox.showerror(titulo, mensaje)
        elif tipo == 'warning': messagebox.showwarning(titulo, mensaje)

    def iniciar(self):
        self.mainloop()