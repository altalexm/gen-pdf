# StarPDF - Generador Profesional de Actas v2.5

_Una aplicación de escritorio moderna y elegante para crear, gestionar y exportar actas de reunión en formato PDF de alta calidad, desarrollada por STAR Software._

![Python](https://img.shields.io/badge/python-3.9+-blue?logo=python)
![Framework](https://img.shields.io/badge/framework-CustomTkinter-green)
![Copyright](https://img.shields.io/badge/copyright-%C2%A9%20STAR%20Software-lightgrey)

---

![Captura de pantalla de la aplicación StarPDF](assets/screenshot.png)

## 📖 Sobre el Proyecto

**StarPDF** es una solución de software propietaria desarrollada por **STAR Software**. Nació de la necesidad de simplificar y profesionalizar la creación de actas de reunión en entornos corporativos. En lugar de depender de plantillas de texto genéricas, esta aplicación ofrece una interfaz gráfica de usuario intuitiva que guía al usuario a través de cada sección del acta, permitiendo una edición en línea fluida y una exportación a un documento PDF con un diseño corporativo impecable.

Este proyecto está construido siguiendo las mejores prácticas de desarrollo, con una arquitectura Modelo-Vista-Controlador (MVC), gestión de configuración externa y un enfoque en la experiencia de usuario.

## ✨ Características Principales

- **Interfaz Moderna:** Construida con CustomTkinter para una apariencia limpia y profesional.
- **Temas Personalizables:** Incluye un selector de tema (claro/oscuro) con una suave animación de transición.
- **Generación de PDF Profesional:** Exporta actas con encabezado, pie de página, logo de empresa y numeración de páginas.
- **Edición Dinámica en Línea:** Añade, edita y elimina normas, puntos del día y acuerdos directamente en la interfaz, sin ventanas emergentes.
- **Persistencia de Sesiones:** Guarda tu trabajo en un archivo `.json` y cárgalo más tarde para continuar donde lo dejaste.
- **Configuración Centralizada:** Personaliza listas predefinidas (proyectos, lugares, personas) y el diseño del PDF a través de un archivo de configuración fácil de editar.
- **Gestión de Ajustes de Usuario:** La configuración personalizada se guarda de forma segura en la carpeta "Documentos" del usuario.

## 🛠️ Tecnologías Utilizadas

- **Python 3.9+**
- **CustomTkinter:** Para la interfaz gráfica moderna.
- **FPDF2 (fpdf):** Para la generación de documentos PDF.
- **PyYAML:** Para la gestión de archivos de configuración `.yaml`.
- **tkcalendar:** Para el widget de calendario emergente.
- **Pillow (PIL):** Para el manejo de imágenes (iconos, logo).

## 🚀 Instalación y Uso

**Para Usuarios Finales (Instalador):**

1.  Descarga la última versión del instalador proporcionado por STAR Software.
2.  Ejecuta el archivo `StarPDF_v2.5_Setup.exe`.
3.  Sigue las instrucciones del instalador. La aplicación se iniciará automáticamente al finalizar.

**Para Desarrolladores (Acceso Interno):**

El acceso al código fuente está restringido al personal de desarrollo de STAR Software. Si eres un desarrollador autorizado, sigue estos pasos:

1.  **Clona el repositorio interno:**

    ```bash
    git clone <URL_DEL_REPOSITORIO_INTERNO>
    cd starpdf
    ```

2.  **Crea y activa un entorno virtual:**

    ```bash
    # Crea el entorno
    python -m venv venv

    # Actívalo (Windows)
    .\venv\Scripts\Activate.ps1

    # Actívalo (macOS/Linux)
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecuta la aplicación:**
    ```bash
    python -m src.main
    ```

## ⚙️ Configuración

La aplicación utiliza dos archivos `config.yaml` para una gestión flexible:

1.  **Plantilla Base (`config.yaml`):** Ubicado en la raíz del proyecto. Contiene la configuración por defecto y sirve como plantilla.
2.  **Configuración de Usuario:** Se crea automáticamente en la carpeta `Documentos/StarPDF` del usuario. **Este es el archivo que se modifica** para que los ajustes personales se guarden permanentemente.

## 📜 Licencia y Derechos de Autor

**Copyright © 2025 STAR Software. Todos los derechos reservados.**

Este software es un producto propietario y confidencial de STAR Software. No está permitido copiar, modificar, distribuir, vender o realizar ingeniería inversa de este software sin el permiso explícito por escrito de STAR Software.

El uso de esta aplicación está sujeto a los términos y condiciones del Acuerdo de Licencia de Usuario Final (EULA) proporcionado con el software.
