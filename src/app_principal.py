# src/app_principal.py

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from pathlib import Path
from datetime import datetime
from .widgets_personalizados import PestañaListaDinamica, ThemeAnimator, ModuleCard

class AppPrincipal(ctk.CTk):
    def __init__(self, config: dict, base_path: Path):
        super().__init__()
        self.controlador = None
        self.config = config
        self.base_path = base_path
        
        app_config = self.config.get('app', {})
        self.app_name = app_config.get('app_name', 'StarPDF')
        self.app_version = app_config.get('app_version', '?.?')
        
        self.title(self.app_name)
        self.geometry("1100x750")
        self.minsize(900, 600)
        
        self._set_app_icon()
        self._cargar_iconos()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        
        self.main_content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content_container.grid_columnconfigure(0, weight=1)
        self.main_content_container.grid_rowconfigure(0, weight=1)
        
        self.frames = {}

    def set_controlador(self, controlador):
        self.controlador = controlador

    def post_inicializacion(self):
        self._create_dashboard_frame()
        self._create_settings_frame()
        self._populate_sidebar()
        if hasattr(self, 'btn_guardar_ajustes'):
            self.btn_guardar_ajustes.configure(command=self.controlador.guardar_ajustes)

    def _populate_sidebar(self):
        logo_label = ctk.CTkLabel(self.sidebar_frame, text=self.app_name, font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        hover_color = ("gray85", "gray19")
        
        home_button = ctk.CTkButton(self.sidebar_frame, text="Inicio", image=self.icon_home, anchor="w",
                                    hover_color=hover_color,
                                    command=lambda: self.controlador.mostrar_frame("dashboard"))
        home_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(self.sidebar_frame, text="Módulos", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        
        documentos = self.config.get('documentos', [])
        for i, doc_config in enumerate(documentos):
            modulo_nombre = doc_config.get("modulo")
            if modulo_nombre:
                try: icon = ctk.CTkImage(Image.open(self.base_path / doc_config.get("icon")), size=(20, 20))
                except: icon = None
                
                is_enabled = self.controlador.modulo_existe(modulo_nombre) if self.controlador else False
                
                btn = ctk.CTkButton(self.sidebar_frame, text=doc_config.get("nombre_corto"),
                                    image=icon, anchor="w", hover_color=hover_color,
                                    command=lambda m=modulo_nombre: self.controlador.mostrar_frame(m))
                
                if not is_enabled:
                    btn.configure(state="disabled", text_color="gray")
                
                btn.grid(row=3+i, column=0, padx=20, pady=5, sticky="ew")

        # Botón para buscar actualizaciones en GitLab
        update_button = ctk.CTkButton(self.sidebar_frame, text="Buscar Actualizaciones", 
                                     anchor="w", hover_color=hover_color,
                                     command=lambda: self.controlador.verificar_actualizaciones() if self.controlador else None)
        update_button.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        settings_button = ctk.CTkButton(self.sidebar_frame, text="Ajustes", image=self.icon_settings, anchor="w",
                                        hover_color=hover_color,
                                        command=lambda: self.controlador.mostrar_frame("settings"))
        settings_button.grid(row=6, column=0, padx=20, pady=10, sticky="s")
        
        self.btn_theme = ctk.CTkButton(self.sidebar_frame, text="", image=self.icon_sun, width=30,
                                       fg_color="transparent", hover_color=("gray70", "gray30"),
                                       command=self.toggle_theme_with_animation)
        self.btn_theme.grid(row=7, column=0, padx=20, pady=(5, 10), sticky="s")
        if ctk.get_appearance_mode() == "Dark":
            self.btn_theme.configure(image=self.icon_moon)
        
        copyright_text = self.config.get('pdf_design', {}).get('company_name', 'Desarrollador')
        footer_label = ctk.CTkLabel(self.sidebar_frame, text=f"v{self.app_version}\n© {datetime.today().year} {copyright_text.split('|')[0].strip()}",
                                    font=ctk.CTkFont(size=10), text_color="gray")
        footer_label.grid(row=8, column=0, padx=10, pady=(0, 10), sticky="s")

    def _create_dashboard_frame(self):
        dashboard_frame = ctk.CTkFrame(self.main_content_container, fg_color="transparent")
        dashboard_frame.grid(row=0, column=0, sticky="nsew")
        self.frames["dashboard"] = dashboard_frame
        dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1)
        dashboard_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(dashboard_frame, text="Bienvenido", font=ctk.CTkFont(size=32, weight="bold")).grid(row=0, column=0, columnspan=3, padx=20, pady=(0, 5), sticky="w")
        ctk.CTkLabel(dashboard_frame, text="Seleccione una herramienta para comenzar.", font=ctk.CTkFont(size=14), text_color="gray").grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="w")
        
        card_grid = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        card_grid.grid(row=2, column=0, columnspan=3, sticky="nsew")
        card_grid.grid_columnconfigure((0, 1, 2), weight=1)

        documentos = self.config.get('documentos', [])
        for i, doc in enumerate(documentos):
            is_enabled = self.controlador.modulo_existe(doc.get("modulo")) if self.controlador else False
            card = ModuleCard(card_grid, self.base_path, doc.get("icon", ""), doc.get("nombre", "N/A"),
                              doc.get("nombre_corto", ""), doc.get("descripcion", ""),
                              lambda m=doc.get("modulo"): self.controlador.mostrar_frame(m),
                              enabled=is_enabled)
            card.grid(row=i//3, column=i%3, padx=15, pady=15, sticky="nsew")

    def _create_settings_frame(self):
        settings_frame = ctk.CTkFrame(self.main_content_container, fg_color="transparent")
        settings_frame.grid(row=0, column=0, sticky="nsew")
        self.frames["settings"] = settings_frame

        ctk.CTkLabel(settings_frame, text="Ajustes Generales", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 20), padx=20, anchor="w")
        
        notebook_ajustes = ctk.CTkTabview(settings_frame, anchor="nw")
        notebook_ajustes.pack(fill="both", expand=True, padx=20, pady=0)

        self.pestaña_ajustes_proyectos = PestañaListaDinamica(notebook_ajustes, "Proyectos", 'simple', "Nombre del nuevo proyecto...")
        self.pestaña_ajustes_lugares = PestañaListaDinamica(notebook_ajustes, "Lugares", 'simple', "Nombre del nuevo lugar...")
        self.pestaña_ajustes_personas = PestañaListaDinamica(notebook_ajustes, "Personas", 'simple', "Nombre de la nueva persona...")

        self.btn_guardar_ajustes = ctk.CTkButton(settings_frame, text="Guardar Ajustes", font=ctk.CTkFont(weight="bold"))
        self.btn_guardar_ajustes.pack(pady=20, padx=20, side="bottom", fill="x")

    def mostrar_frame(self, nombre_frame: str):
        if nombre_frame not in self.frames:
            modulo = self.controlador.modulos_cargados.get(nombre_frame)
            if modulo:
                frame_modulo = ctk.CTkFrame(self.main_content_container, fg_color="transparent")
                frame_modulo.grid(row=0, column=0, sticky="nsew")
                frame_modulo.modulo = modulo
                
                frame_acciones_modulo = ctk.CTkFrame(frame_modulo, corner_radius=0)
                frame_acciones_modulo.pack(fill="x", padx=0, pady=10)
                ctk.CTkButton(frame_acciones_modulo, text="Guardar Sesión", command=self.controlador.guardar_sesion).pack(side="left", padx=(0, 5))
                ctk.CTkButton(frame_acciones_modulo, text="Cargar Sesión", command=self.controlador.cargar_sesion).pack(side="left", padx=5)
                ctk.CTkButton(frame_acciones_modulo, text="Generar PDF", font=ctk.CTkFont(weight="bold"), command=self.controlador.generar_pdf).pack(side="left", padx=5)
                
                notebook = ctk.CTkTabview(frame_modulo)
                notebook.pack(fill="both", expand=True)
                
                modulo.crear_frames_ui(notebook)
                self.frames[nombre_frame] = frame_modulo
            else:
                self.mostrar_mensaje('error', 'Error de Módulo', f'No se pudo encontrar o cargar el módulo "{nombre_frame}".')
                return

        frame = self.frames.get(nombre_frame)
        if frame:
            frame.tkraise()
            title = self.app_name
            if hasattr(frame, 'modulo'):
                title += f" - {frame.modulo.get_nombre()}"
            elif nombre_frame == "settings":
                title += " - Ajustes"
            self.title(title)

    def _set_app_icon(self):
        try:
            icon_path_rel = self.config.get('app', {}).get('app_icon')
            if icon_path_rel:
                icon_path_abs = self.base_path / icon_path_rel
                if icon_path_abs.exists():
                    self.iconbitmap(str(icon_path_abs))
        except Exception as e:
            print(f"Error al establecer el icono: {e}")

    def _cargar_iconos(self):
        app_config = self.config.get('app', {})
        def load_icon(key):
            try:
                path = self.base_path / app_config.get(key)
                return ctk.CTkImage(Image.open(path), size=(20, 20))
            except: return None
        
        self.icon_home = load_icon('icon_home')
        self.icon_settings = load_icon('icon_settings')
        self.icon_sun = load_icon('icon_sun')
        self.icon_moon = load_icon('icon_moon')

    def toggle_theme_with_animation(self):
        new_theme = "Light" if ctk.get_appearance_mode() == "Dark" else "Dark"
        def on_animation_finish():
            icon = self.icon_moon if new_theme == "Dark" else self.icon_sun
            self.btn_theme.configure(image=icon)
        animator = ThemeAnimator(self)
        animator.run(new_theme, on_finish_callback=on_animation_finish)

    def poblar_ajustes(self, proyectos, lugares, personas):
        self.pestaña_ajustes_proyectos.poblar_desde_datos(proyectos)
        self.pestaña_ajustes_lugares.poblar_desde_datos(lugares)
        self.pestaña_ajustes_personas.poblar_desde_datos(personas)

    def actualizar_comboboxes_modulo(self, modulo, proyectos, lugares, personas):
        if not modulo: return
        placeholder_proy = ["-- Selecciona un Proyecto --"] + proyectos
        placeholder_lugar = ["-- Selecciona un Lugar --"] + lugares
        placeholder_pers = ["-- Selecciona una Persona --"] + personas
        if hasattr(modulo, 'actualizar_comboboxes'):
            modulo.actualizar_comboboxes(placeholder_proy, placeholder_lugar, placeholder_pers)
        
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