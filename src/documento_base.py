from abc import ABC, abstractmethod

class DocumentoBase(ABC):
    """
    Clase Base Abstracta (ABC) que define la interfaz ("el contrato") que cada
    módulo de documento debe implementar.

    Esto garantiza que el Controlador y la Vista genéricos puedan interactuar
    con cualquier tipo de documento de una manera estandarizada, haciendo que el
    sistema sea modular y fácilmente extensible.
    """
    def __init__(self, config: dict, base_path):
        """
        El constructor de cada módulo debe aceptar la configuración y la ruta base.
        """
        self.config = config
        self.base_path = base_path
        self.widgets = {} # Diccionario donde cada módulo guardará sus propios widgets de UI

    @abstractmethod
    def get_nombre(self) -> str:
        """
        Debe devolver el nombre completo y legible del tipo de documento.
        Ejemplo: "Acta de Reunión"
        """
        pass

    @abstractmethod
    def get_datos_iniciales(self) -> dict:
        """
        Debe devolver un diccionario que representa la estructura de datos
        vacía o por defecto para este tipo de documento.
        """
        pass

    @abstractmethod
    def crear_frames_ui(self, parent_notebook):
        """
        Debe construir la interfaz de usuario específica para este documento.
        Normalmente, esto implica añadir pestañas y widgets al `parent_notebook`
        proporcionado por la ventana principal.

        Es crucial que el módulo guarde las referencias a sus widgets importantes
        (campos de entrada, listas, etc.) en el diccionario `self.widgets` para
        que los otros métodos puedan acceder a ellos.
        """
        pass

    @abstractmethod
    def obtener_datos_desde_ui(self) -> dict:
        """
        Debe leer los valores actuales de todos los widgets de la UI (almacenados
        en `self.widgets`) y devolverlos en un diccionario con la misma estructura
        que `get_datos_iniciales`.
        """
        pass

    @abstractmethod
    def poblar_ui_desde_datos(self, datos: dict):
        """
        Debe tomar un diccionario de datos y rellenar los widgets de la UI
        (almacenados en `self.widgets`) con esos valores.
        Esencial para la función de "Cargar Sesión".
        """
        pass

    @abstractmethod
    def generar_pdf(self, datos: dict, ruta_archivo: str) -> tuple[bool, str | None]:
        """
        Debe tomar un diccionario de datos y generar el documento PDF final
        en la `ruta_archivo` especificada.

        Debe devolver una tupla: (True, None) en caso de éxito, o
        (False, "mensaje de error") en caso de fallo.
        """
        pass