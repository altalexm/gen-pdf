# src/widgets_personalizados.py

import customtkinter as ctk
from datetime import datetime
from tkcalendar import Calendar
from PIL import Image
from pathlib import Path

class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Input", prompt=""):
        super().__init__(parent)
        self.title(title); self.transient(parent); self.grab_set()
        self._input_text = ""
        self.grid_columnconfigure(0, weight=1)
        self.label = ctk.CTkLabel(self, text=prompt, wraplength=250)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry = ctk.CTkEntry(self, width=250)
        self.entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.ok_button = ctk.CTkButton(self.button_frame, text="OK", command=self._on_ok)
        self.ok_button.pack(side="left", padx=(0, 5))
        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancelar", command=self._on_cancel)
        self.cancel_button.pack(side="left")
        self.after(50, self._center_window); self.bind("<Return>", self._on_ok); self.bind("<Escape>", self._on_cancel)
        self.entry.focus_set()

    def _center_window(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _on_ok(self, event=None):
        self._input_text = self.entry.get(); self.destroy()
    def _on_cancel(self, event=None):
        self._input_text = None; self.destroy()
    def get_input(self):
        self.wait_window(); return self._input_text

class FilaItemSimple(ctk.CTkFrame):
    def __init__(self, parent, texto="", eliminar_callback=None, placeholder="Escriba aquí..."):
        super().__init__(parent, fg_color="transparent")
        self.eliminar_callback = eliminar_callback
        self.grip_handle = ctk.CTkLabel(self, text="☰", font=ctk.CTkFont(size=16), cursor="hand2")
        self.grip_handle.pack(side="left", padx=(0, 10))
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        if texto: self.entry.insert(0, texto)
        self.btn_eliminar = ctk.CTkButton(self, text="X", width=30, command=self._eliminar)
        self.btn_eliminar.pack(side="left")

    def get_text(self): return self.entry.get()
    def _eliminar(self):
        if self.eliminar_callback: self.eliminar_callback(self)

class FilaItemComplejo(ctk.CTkFrame):
    def __init__(self, parent, titulo="", descripcion="", eliminar_callback=None):
        super().__init__(parent, fg_color=("gray90", "gray20"), corner_radius=8)
        self.eliminar_callback = eliminar_callback
        self.grid_columnconfigure(2, weight=1)
        self.grip_handle = ctk.CTkLabel(self, text="☰", font=ctk.CTkFont(size=20), cursor="hand2")
        self.grip_handle.grid(row=0, column=0, rowspan=3, padx=(10, 5), sticky="ns")
        ctk.CTkLabel(self, text="Título:").grid(row=0, column=1, padx=(0,10), pady=(10, 5), sticky="w")
        self.entry_titulo = ctk.CTkEntry(self, placeholder_text="Título del punto...")
        self.entry_titulo.grid(row=0, column=2, padx=10, pady=(10, 5), sticky="ew")
        if titulo: self.entry_titulo.insert(0, titulo)
        ctk.CTkLabel(self, text="Descripción:").grid(row=1, column=1, padx=(0,10), pady=5, sticky="nw")
        self.textbox_desc = ctk.CTkTextbox(self, height=80, wrap="word")
        self.textbox_desc.grid(row=1, column=2, padx=10, pady=5, sticky="ew")
        if descripcion: self.textbox_desc.insert("1.0", descripcion)
        self.btn_eliminar = ctk.CTkButton(self, text="Eliminar Punto", command=self._eliminar)
        self.btn_eliminar.grid(row=2, column=1, columnspan=2, padx=10, pady=(5, 10), sticky="e")

    def get_data(self):
        return {"titulo": self.entry_titulo.get(), "descripcion": self.textbox_desc.get("1.0", "end-1c")}
    def _eliminar(self):
        if self.eliminar_callback: self.eliminar_callback(self)

class PestañaListaDinamica:
    def __init__(self, parent_notebook, nombre_pestaña, tipo_item='simple', placeholder=""):
        self.tab = parent_notebook.add(nombre_pestaña)
        self.tipo_item = tipo_item
        self.items_widgets = []
        self.placeholder = placeholder
        self.drag_widget = None
        self.drag_start_y = 0
        self.placeholder_frame = None

        frame_controles = ctk.CTkFrame(self.tab)
        frame_controles.pack(fill="x", padx=10, pady=10)
        self.btn_add_uno = ctk.CTkButton(frame_controles, text="Añadir Nuevo Campo", command=self.añadir_fila_vacia)
        self.btn_add_uno.pack(side="left")
        self.scroll_frame = ctk.CTkScrollableFrame(self.tab, label_text=f"Lista de {nombre_pestaña}")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _bind_drag_events(self, fila):
        fila.grip_handle.bind("<ButtonPress-1>", lambda event, w=fila: self._start_drag(event, w))
        fila.grip_handle.bind("<B1-Motion>", self._on_drag)
        fila.grip_handle.bind("<ButtonRelease-1>", self._stop_drag)

    def _start_drag(self, event, widget):
        if self.drag_widget: return
        self.drag_widget = widget
        self.drag_start_y = event.y
        self.placeholder_frame = ctk.CTkFrame(self.scroll_frame, height=widget.winfo_height(), fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0], corner_radius=8)
        self.drag_widget.lift()

    def _on_drag(self, event):
        if not self.drag_widget: return
        
        container_height = self.scroll_frame.winfo_height()
        widget_height = self.drag_widget.winfo_height()
        
        y = self.drag_widget.winfo_y() - self.drag_start_y + event.y
        y = max(0, min(y, container_height - widget_height))
        self.drag_widget.place(x=0, y=y, relwidth=1)
        
        self._update_placeholder(y)

    def _update_placeholder(self, drag_y):
        if not self.drag_widget: return
        
        other_widgets = [w for w in self.items_widgets if w is not self.drag_widget]
        drop_index = 0
        
        for i, widget in enumerate(other_widgets):
            if drag_y > widget.winfo_y() + widget.winfo_height() / 2:
                drop_index = i + 1
        
        temp_list = other_widgets[:]
        temp_list.insert(drop_index, self.placeholder_frame)
        
        for widget in self.scroll_frame.winfo_children():
            widget.pack_forget()

        for widget in temp_list:
            widget.pack(fill="x", expand=True, padx=5, pady=5)

    def _stop_drag(self, event):
        if not self.drag_widget: return
        
        if self.placeholder_frame: self.placeholder_frame.destroy()
        self.placeholder_frame = None
        self.drag_widget.place_forget()

        drop_index = 0
        final_y = self.drag_widget.winfo_y()
        other_widgets = [w for w in self.items_widgets if w is not self.drag_widget]

        for i, widget in enumerate(other_widgets):
            if final_y > widget.winfo_y():
                drop_index = i + 1
        
        self.items_widgets.remove(self.drag_widget)
        self.items_widgets.insert(drop_index, self.drag_widget)
        
        self._redraw_list()
        self.drag_widget = None

    def _redraw_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.pack_forget()
        for widget in self.items_widgets:
            widget.pack(fill="x", expand=True, padx=5, pady=5)
    
    def on_item_deleted(self, widget_fila):
        if widget_fila in self.items_widgets:
            self.items_widgets.remove(widget_fila)
        widget_fila.destroy()
        self._redraw_list()

    def añadir_fila_vacia(self):
        self._create_and_add_fila()

    def _create_and_add_fila(self, data=None):
        if self.tipo_item == 'simple':
            fila = FilaItemSimple(self.scroll_frame, texto=data or "", eliminar_callback=self.on_item_deleted, placeholder=self.placeholder)
        else:
            fila = FilaItemComplejo(self.scroll_frame, titulo=data.get("titulo", "") if data else "", 
                                    descripcion=data.get("descripcion", "") if data else "", 
                                    eliminar_callback=self.on_item_deleted)
        self._bind_drag_events(fila)
        self.items_widgets.append(fila)
        self._redraw_list()

    def limpiar_campos(self):
        for widget in self.items_widgets: widget.destroy()
        self.items_widgets.clear()
        
    def poblar_desde_datos(self, lista_datos):
        self.limpiar_campos()
        for dato in lista_datos:
            self._create_and_add_fila(dato)

    def obtener_datos_actuales(self):
        return [w.get_text() if self.tipo_item == 'simple' else w.get_data()
                for w in self.items_widgets
                if (self.tipo_item == 'simple' and w.get_text().strip()) or \
                   (self.tipo_item == 'complejo' and w.get_data()['titulo'].strip())]

class DateInput(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(self, placeholder_text="dd/mm/aaaa")
        self.entry.grid(row=0, column=0, sticky="ew")
        self.btn = ctk.CTkButton(self, text="🗓️", width=30, command=self.open_calendar)
        self.btn.grid(row=0, column=1, padx=(5, 0))
        self.calendar_window = None

    def open_calendar(self):
        if self.calendar_window and self.calendar_window.winfo_exists():
            self.calendar_window.focus(); return
        self.calendar_window = ctk.CTkToplevel(self)
        self.calendar_window.title("Seleccionar Fecha")
        self.calendar_window.transient(self.winfo_toplevel())
        self.calendar_window.grab_set()
        try: current_date = datetime.strptime(self.entry.get(), "%d/%m/%Y")
        except ValueError: current_date = datetime.now()
        cal = Calendar(self.calendar_window, selectmode='day', date_pattern='dd/mm/yyyy',
                       year=current_date.year, month=current_date.month, day=current_date.day)
        cal.pack(pady=10, padx=10)
        def select_date():
            self.entry.delete(0, "end"); self.entry.insert(0, cal.get_date())
            self.calendar_window.destroy()
        btn_ok = ctk.CTkButton(self.calendar_window, text="Seleccionar", command=select_date)
        btn_ok.pack(pady=10)

    def get(self): return self.entry.get()
    def set(self, date_str):
        self.entry.delete(0, "end"); self.entry.insert(0, date_str)

class TimeInput(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        hours = [f"{h:02d}" for h in range(24)]
        minutes = [f"{m:02d}" for m in range(0, 60, 15)]
        self.hour_menu = ctk.CTkOptionMenu(self, values=hours); self.hour_menu.pack(side="left")
        ctk.CTkLabel(self, text=":", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=5)
        self.minute_menu = ctk.CTkOptionMenu(self, values=minutes); self.minute_menu.pack(side="left")

    def get(self): return f"{self.hour_menu.get()}:{self.minute_menu.get()}"
    def set(self, time_str):
        try:
            hour, minute = time_str.split(":")
            minute_int = int(minute)
            closest_minute = f"{15 * round(minute_int / 15):02d}"
            if closest_minute == "60": closest_minute = "45"
            self.hour_menu.set(hour); self.minute_menu.set(closest_minute)
        except (ValueError, AttributeError):
            self.hour_menu.set("00"); self.minute_menu.set("00")

class ThemeAnimator(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent); self.lift(); self.grab_set()
        self.overrideredirect(True)
        self.geometry(f"{parent.winfo_width()}x{parent.winfo_height()}+{parent.winfo_x()}+{parent.winfo_y()}")
        self.attributes("-alpha", 0.0)
        self.current_alpha = 0.0
        self.target_theme = None
        self.on_finish_callback = None
        
    def run(self, target_theme, on_finish_callback=None):
        self.target_theme = target_theme
        self.on_finish_callback = on_finish_callback
        self._fade_in()

    def _fade_in(self):
        self.current_alpha += 0.1
        if self.current_alpha >= 1.0:
            self.attributes("-alpha", 1.0)
            ctk.set_appearance_mode(self.target_theme)
            self.after(50, self._fade_out)
        else:
            self.attributes("-alpha", self.current_alpha)
            self.after(20, self._fade_in)

    def _fade_out(self):
        self.current_alpha -= 0.1
        if self.current_alpha <= 0.0:
            self.attributes("-alpha", 0.0)
            if self.on_finish_callback: self.on_finish_callback()
            self.destroy()
        else:
            self.attributes("-alpha", self.current_alpha)
            self.after(20, self._fade_out)

class ModuleCard(ctk.CTkFrame):
    def __init__(self, parent, base_path: Path, icon_path: str, title: str, short_name: str, description: str, command, enabled=True):
        super().__init__(parent, corner_radius=10, border_width=2)
        
        self.command = command if enabled else None
        self.enabled = enabled
        
        self.original_fg_color = self.cget("fg_color")
        self.hover_fg_color = ("gray85", "gray19")
        self.border_hover_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"][0]
        self.configure(border_color=self.original_fg_color)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        if self.enabled:
            self.bind_events(self)

        try:
            full_icon_path = base_path / icon_path
            if not full_icon_path.is_file(): raise FileNotFoundError()
            icon_image = ctk.CTkImage(Image.open(full_icon_path), size=(56, 56))
            self.icon_label = ctk.CTkLabel(self, image=icon_image, text="")
        except:
            self.icon_label = ctk.CTkLabel(self, text="📄", font=ctk.CTkFont(size=48))
        self.icon_label.grid(row=0, column=0, pady=(20, 10))
        if self.enabled: self.bind_events(self.icon_label)

        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=10, pady=0)
        if self.enabled: self.bind_events(self.title_label)
        
        self.short_name_label = ctk.CTkLabel(self, text=short_name.upper(), font=ctk.CTkFont(size=10, weight="bold"), text_color="gray")
        self.short_name_label.grid(row=2, column=0, padx=10, pady=(0, 10))
        if self.enabled: self.bind_events(self.short_name_label)

        self.desc_label = ctk.CTkLabel(self, text=description, wraplength=180, text_color=("gray20", "gray80"))
        self.desc_label.grid(row=3, column=0, padx=15, pady=(0, 20), sticky="nsew")
        if self.enabled: self.bind_events(self.desc_label)
        
        if not self.enabled:
            self.configure(fg_color=("gray90", "gray20"))
            self.title_label.configure(text_color="gray")
            self.desc_label.configure(text=f"{description}\n\n(Próximamente)")

    def bind_events(self, widget):
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        widget.bind("<Button-1>", self._on_click)

    def _on_enter(self, event):
        self.configure(fg_color=self.hover_fg_color, border_color=self.border_hover_color)

    def _on_leave(self, event):
        self.configure(fg_color=self.original_fg_color, border_color=self.original_fg_color)
        
    def _on_click(self, event):
        if self.command:
            self.command()