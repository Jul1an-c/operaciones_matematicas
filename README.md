# Aplicación de Operaciones Matemáticas por Voz con Vosk y Flet

## Descripción

Esta aplicación permite realizar operaciones matemáticas utilizando un modelo de reconocimiento de voz local Vosk. 
El usuario puede seleccionar las tablas de multiplicar que desea practicar y la aplicación generará preguntas aleatorias basadas en esas tablas. 
Las preguntas se presentan mediante audio (pyttsx3) y el usuario puede responder tanto por voz (Vosk) como por texto. 
La aplicación verifica las respuestas y proporciona un resultado final. La interfaz gráfica se construye con Flet.

## Características Principales

* **Reconocimiento de Voz Local:** Utiliza el modelo Vosk para un reconocimiento de voz preciso y sin conexión a internet.
* **Síntesis de Voz:** Utiliza pyttsx3 para generar preguntas y retroalimentación por audio.
* **Interfaz Gráfica con Flet:** Interfaz de usuario interactiva y multiplataforma.
* **Selección de Tablas:** Permite al usuario elegir las tablas de multiplicar que desea practicar.
* **Generación Aleatoria de Preguntas:** Genera preguntas aleatorias basadas en las tablas seleccionadas (con `question_generator.py`).
* **Preguntas por Audio:** Presenta las preguntas mediante voz para una experiencia interactiva.
* **Respuesta por Voz o Texto:** Permite al usuario responder tanto por voz como por texto.
* **Verificación de Respuestas:** Comprueba las respuestas del usuario y proporciona retroalimentación.
* **Resultado Final:** Muestra el resultado final de la sesión de práctica.
* **Utilidades de voz:** (voice_utils.py) para abstracción de funciones de audio.
* **Hilos:** Se utiliza threading para mejorar la respuesta y no bloquear la interfaz grafica.

## Instalación

1.  **Requisitos:**
    * Python 3.x
    * Vosk API
    * Modelo de lenguaje Vosk (descargar desde [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models))
Spanish-vosk-model-small-es-0.42
    * Bibliotecas Python: `re`, `pyttsx3`, `threading`, `queue`, `pyaudio`, `json`, `time`, `vosk`, `flet`.
2.  **Instalación de Dependencias:**
    ```bash
    pip install vosk flet pyttsx3 pyaudio
    ```
3.  **Descarga del Modelo Vosk:**
    * Descarga el modelo de lenguaje Vosk deseado y descomprímirlo en la carpeta principal.
4.  **Configuración:**
    * Asegúrate de que el modelo Vosk esté en la ubicación correcta y configura la ruta en el código.

## Uso

1.  **Ejecución:**
    ```bash
    python interface.py
    ```
2.  **Selección de Tablas:**
    * Utiliza la interfaz de Flet para seleccionar las tablas de multiplicar que deseas practicar.
3.  **Práctica:**
    * Escucha las preguntas por audio (pyttsx3) y responde por voz (Vosk) o texto.
    * La aplicación verificará tus respuestas y te dará retroalimentación.
4.  **Resultado Final:**
    * Al finalizar la sesión, la aplicación mostrará tu resultado en la interfaz de Flet.

## Estructura del Proyecto

* `interface.py`: Script principal que ejecuta la aplicación con Flet.
* `question_generator.py`: Genera preguntas matemáticas aleatorias.
* `voice_utils.py`: Funciones de utilidad para el manejo de voz (Vosk y pyttsx3).
* `modelo_vosk/`: Carpeta que contiene el modelo de lenguaje Vosk.
