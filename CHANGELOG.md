# Historial de Cambios de StarPDF

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto se adhiere al [Versionado Semántico](https://semver.org/spec/v2.0.0.html).

---

## [3.0.1] - [Fecha: 23/10/2025]

### 🐛 Corregido (Fixed)

- Corregido un problema de compatibilidad con la biblioteca FPDF que causaba errores en la generación de PDFs
- Mejorado el manejo de rutas de archivos para asegurar la compatibilidad con la aplicación empaquetada
- Actualizada la sintaxis de las llamadas a métodos de FPDF para mantener compatibilidad con versiones anteriores

## [3.0.0] - [Fecha: 22/10/2025]

Esta es una **actualización mayor** que transforma a StarPDF de un generador de un solo documento a una plataforma de documentación modular completa. La arquitectura ha sido reescrita desde cero para ser escalable, y la interfaz de usuario ha sido rediseñada para una experiencia profesional y moderna.

### ✨ Añadido (Added)

- **Arquitectura Multi-Módulo (Hub and Spoke):** La aplicación ahora funciona como un lanzador (`Hub`) capaz de gestionar múltiples generadores de documentos (`Spokes`).
- **Dashboard de Bienvenida:** Una nueva pantalla de inicio elegante que muestra los módulos disponibles como tarjetas interactivas con iconos, descripciones y efectos `hover`.
- **Navegación Global con Sidebar:** Se implementó una barra lateral persistente que permite al usuario navegar fluidamente entre el "Inicio" (Dashboard), cada módulo de documento y los "Ajustes".
- **Funcionalidad de Drag & Drop Avanzada:** Los items en las listas (Normas, Orden del Día, etc.) ahora se pueden reordenar arrastrando y soltando, con una animación de desplazamiento en tiempo real y movimiento confinado verticalmente.
- **Pestaña de Ajustes Global:** Se añadió una nueva sección de "Ajustes" para que el usuario pueda personalizar listas predefinidas de Proyectos, Lugares y Personas.
- **Persistencia de Ajustes:** Los cambios realizados en la pestaña "Ajustes" se guardan de forma permanente en el `config.yaml` del usuario.
- **Módulos Deshabilitados:** La interfaz ahora detecta qué módulos no están implementados y los muestra visualmente como "deshabilitados" (en gris, no clickables) tanto en el Dashboard como en el Sidebar.

### 🎨 Cambiado (Changed)

- **Refactorización Completa a Ventana Única:** Se eliminó el concepto de ventanas separadas. Ahora toda la aplicación opera dentro de una única ventana principal, intercambiando vistas de contenido.
- **Controlador y Vista Genéricos:** El `Controlador` y la `AppPrincipal` (la nueva `Vista`) son ahora completamente agnósticos al tipo de documento, operando sobre una interfaz `DocumentoBase`.
- **Campos de Texto a ComboBox:** Los campos de Proyecto, Lugar, Moderador y Responsable de Acta ahora son menús desplegables (`ComboBox`) que se pueblan desde los Ajustes.
- **Botón de Tema Mejorado:** Se reemplazó el texto del botón de cambio de tema por un icono sin fondo, mejorando la estética de la interfaz.
- **Mejora del Flujo de Inicialización:** El orden de carga de la configuración, módulos y componentes de la UI fue completamente reestructurado para ser más robusto y evitar errores de `AttributeError`.

### 🐞 Corregido (Fixed)

- Se solucionó un error visual donde el texto de los botones del sidebar no era visible en el tema claro.
- Se corrigieron múltiples errores de `AttributeError` y `ValueError` relacionados con el orden de creación de widgets y la carga de módulos.

---

## [2.5.0] - [Fecha: 12/10/2025]

Versión inicial estable con la interfaz de usuario moderna basada en CustomTkinter y una arquitectura MVC profesional.

### ✨ Añadido (Added)

- **Interfaz Gráfica Profesional:** Se migró de Tkinter estándar a **CustomTkinter**, introduciendo un diseño moderno.
- **Selector de Tema Animado:** Se añadió un selector de tema (Claro/Oscuro) con una suave animación de fundido.
- **Gestión de Configuración Profesional:**
  - Se implementó un `config.yaml` para centralizar la configuración.
  - La configuración del usuario ahora se guarda de forma segura en `Documentos/StarPDF`, separada de la instalación.
- **Widgets Avanzados:** Se introdujeron selectores de fecha con calendario (`tkcalendar`) y selectores de hora.
- **Icono de Aplicación:** La aplicación ahora tiene su propio icono personalizado en la ventana y la barra de tareas.
- **Diseño de PDF Mejorado:** Se añadió un encabezado con logo, un pie de página con el nombre de la empresa y numeración de páginas al PDF generado.
- **Logging Profesional:** Se reemplazaron los `print()` por un sistema de logging que escribe en un archivo `app.log`.
- **Gestión de Errores Robusta:** Se implementó una lógica para manejar errores de permisos y de archivos no encontrados de forma elegante.

### 🎨 Cambiado (Changed)

- **Arquitectura MVC Robusta:** Se consolidó la separación entre Modelo, Vista y Controlador.
- **Control de Versiones:** El proyecto fue inicializado con Git y un archivo `.gitignore`.

### 🐞 Corregido (Fixed)

- Se solucionaron múltiples errores de `TypeError` y `TclError` en la lógica de generación de PDF y en la funcionalidad de Drag & Drop inicial.
