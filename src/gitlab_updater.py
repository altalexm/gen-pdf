"""
Sistema de actualizaciones automáticas para StarPDF usando GitLab
"""

import requests
import json
import subprocess
import os
import tempfile
import threading
from packaging import version
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
from . import gitlab_config as config


class GitLabUpdateChecker:
    def __init__(self, current_version, gitlab_url, project_id, access_token=None):
        self.current_version = current_version
        self.gitlab_url = gitlab_url.rstrip('/')
        self.project_id = project_id
        self.access_token = access_token
        self.api_url = f"{self.gitlab_url}/api/v4/projects/{project_id}/releases"
        
        # Headers para la API
        self.headers = {}
        if self.access_token:
            self.headers['Authorization'] = f'Bearer {self.access_token}'
    
    def check_for_updates(self, show_no_updates=True):
        """Verifica si hay actualizaciones disponibles"""
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            releases = response.json()
            if not releases:
                if show_no_updates:
                    messagebox.showinfo("Actualizaciones", "No hay releases disponibles.")
                return {'available': False}
            
            # Obtener la release más reciente
            latest_release = releases[0]
            latest_version = latest_release['tag_name'].lstrip('v')
            
            if version.parse(latest_version) > version.parse(self.current_version):
                return {
                    'available': True,
                    'version': latest_version,
                    'download_url': self._get_download_url(latest_release),
                    'release_notes': latest_release.get('description', ''),
                    'released_at': latest_release.get('released_at', ''),
                    'web_url': latest_release.get('_links', {}).get('self', '')
                }
            else:
                if show_no_updates:
                    messagebox.showinfo("Actualizaciones", "Tu versión de StarPDF está actualizada.")
                return {'available': False}
                
        except requests.RequestException as e:
            if show_no_updates:
                messagebox.showerror("Error", f"No se pudo verificar actualizaciones:\n{str(e)}")
            return {'available': False, 'error': str(e)}
    
    def _get_download_url(self, release_data):
        """Obtiene la URL de descarga del instalador desde GitLab"""
        # En GitLab, los assets están en 'assets.links'
        for link in release_data.get('assets', {}).get('links', []):
            if link['name'].endswith('.exe') and 'setup' in link['name'].lower():
                return link['url']
        
        # Si no hay assets, construir URL basada en tags
        tag_name = release_data['tag_name']
        return f"{self.gitlab_url}/{self.project_id}/-/releases/{tag_name}"
    
    def show_update_dialog(self, update_info):
        """Muestra diálogo de actualización disponible"""
        dialog = GitLabUpdateDialog(update_info, self)
        return dialog.result
    
    def download_and_install(self, download_url, version_str, progress_callback=None):
        """Descarga e instala la actualización"""
        try:
            # Si la URL no es un archivo directo, abrir en navegador
            if not download_url.endswith('.exe'):
                webbrowser.open(download_url)
                messagebox.showinfo("Descarga", 
                                  "Se ha abierto la página de descargas en tu navegador.\n"
                                  "Descarga el instalador manualmente.")
                return True
            
            # Descargar archivo
            temp_dir = tempfile.mkdtemp()
            filename = f"StarPDF_v{version_str}_Setup.exe"
            filepath = os.path.join(temp_dir, filename)
            
            response = requests.get(download_url, stream=True, headers=self.headers)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            # Ejecutar instalador
            subprocess.Popen([filepath])
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al descargar la actualización:\n{str(e)}")
            return False


class GitLabUpdateDialog:
    def __init__(self, update_info, updater):
        self.update_info = update_info
        self.updater = updater
        self.result = None
        self.progress_window = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """Crea el diálogo de actualización"""
        self.root = tk.Toplevel()
        self.root.title("Actualización Disponible - StarPDF")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.grab_set()
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
        
        # Marco principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="¡Nueva versión disponible!", 
                         font=("Arial", 14, "bold"))
        title.pack(pady=(0, 10))
        
        # Información de versión
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(version_frame, text="Versión actual:").pack(anchor="w")
        ttk.Label(version_frame, text=f"v{self.updater.current_version}", 
                 font=("Arial", 10, "bold")).pack(anchor="w")
        
        ttk.Label(version_frame, text="Nueva versión:").pack(anchor="w", pady=(10, 0))
        ttk.Label(version_frame, text=f"v{self.update_info['version']}", 
                 font=("Arial", 10, "bold"), foreground="green").pack(anchor="w")
        
        # Notas de la versión
        notes_label = ttk.Label(main_frame, text="Notas de la versión:")
        notes_label.pack(anchor="w", pady=(0, 5))
        
        # Text widget con scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        self.notes_text = tk.Text(text_frame, wrap="word", height=10, 
                                 font=("Arial", 9))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", 
                                 command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=scrollbar.set)
        
        self.notes_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Insertar notas
        self.notes_text.insert("1.0", self.update_info.get('release_notes', 
                                                          'No hay notas disponibles.'))
        self.notes_text.config(state="disabled")
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Descargar", 
                  command=self.download_update).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Ver en GitLab", 
                  command=self.open_gitlab).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Recordar más tarde", 
                  command=self.remind_later).pack(side="right")
        ttk.Button(button_frame, text="Omitir esta versión", 
                  command=self.skip_version).pack(side="right", padx=(0, 5))
        
        self.root.protocol("WM_DELETE_WINDOW", self.remind_later)
        self.root.wait_window()
    
    def download_update(self):
        """Inicia la descarga de la actualización"""
        self.result = "download"
        self.root.destroy()
        
        if self.update_info.get('download_url'):
            threading.Thread(target=self._download_thread, daemon=True).start()
        else:
            self.open_gitlab()
    
    def open_gitlab(self):
        """Abre la página de GitLab"""
        self.result = "gitlab"
        self.root.destroy()
        webbrowser.open(self.update_info.get('web_url', 
                       f"{self.updater.gitlab_url}/{self.updater.project_id}/-/releases"))
    
    def remind_later(self):
        """Recordar más tarde"""
        self.result = "later"
        self.root.destroy()
    
    def skip_version(self):
        """Omitir esta versión"""
        self.result = "skip"
        self.root.destroy()
    
    def _download_thread(self):
        """Hilo de descarga"""
        success = self.updater.download_and_install(
            self.update_info['download_url'], 
            self.update_info['version']
        )
        
        if success:
            messagebox.showinfo("Actualización", 
                              "La descarga ha comenzado. Sigue las instrucciones del navegador.")


class StarPDFAutoUpdater:
    def __init__(self, config_manager):
        self.config = config_manager
        
        self.checker = GitLabUpdateChecker(
            current_version=self.config.get("app_version", "3.0.1"),
            gitlab_url=config.GITLAB_URL,
            project_id=config.PROJECT_ID,
            access_token=config.ACCESS_TOKEN
        )
    
    def check_startup_updates(self):
        """Verifica actualizaciones al inicio (silencioso)"""
        if self.config.get("auto_check_updates", config.AUTO_CHECK_ON_STARTUP):
            threading.Thread(target=self._silent_check, daemon=True).start()
    
    def check_manual_updates(self):
        """Verificación manual de actualizaciones"""
        threading.Thread(target=self._manual_check, daemon=True).start()
    
    def _silent_check(self):
        """Verificación silenciosa"""
        update_info = self.checker.check_for_updates(show_no_updates=False)
        if update_info.get('available'):
            result = self.checker.show_update_dialog(update_info)
            if result == "skip":
                self.config.set(f"skip_version_{update_info['version']}", True)
    
    def _manual_check(self):
        """Verificación manual"""
        update_info = self.checker.check_for_updates(show_no_updates=True)
        if update_info.get('available'):
            self.checker.show_update_dialog(update_info)


def setup_gitlab_updater(app, config_manager):
    """Configura el sistema de actualizaciones automáticas con GitLab"""
    updater = StarPDFAutoUpdater(config_manager)
    
    # Verificar al inicio
    updater.check_startup_updates()
    
    return updater