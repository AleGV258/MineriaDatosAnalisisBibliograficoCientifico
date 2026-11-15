# Inicialización del proyecto — Minería de Textos

## 1. Requisitos previos

Antes de iniciar, se necesita tener instalado:

- Python 3.12 o superior
- Git (opcional)
- Visual Studio Code o algún editor de código (opcional)

## 2. Obtener el proyecto

Descargar o clonar el repositorio y abrir una terminal dentro de la carpeta principal del proyecto

## 3. Crear el entorno virtual

Ejecutar el siguiente comando:

```powershell
python -m venv .venv
```

## 4. Activar el entorno virtual

En Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

En Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

## 5. Instalar las dependencias

Con el entorno virtual activado, ejecutar:

```powershell
python -m pip install --upgrade pip
```

Posteriormente, instalar las librerías del proyecto:

```powershell
pip install -r requirements.txt
```

## 6. Ejecutar la aplicación

Desde la carpeta principal del proyecto, ejecutar:

```powershell
python main.py
```

## 7. Estructura de resultados

Los documentos procesados y resultados se almacenarán dentro de la carpeta `datos/salida`

Los documentos PDF originales deberán seleccionarse desde la interfaz de la aplicación

## 8. Consideraciones

- El entorno virtual debe estar activado antes de ejecutar el proyecto
- Las dependencias se encuentran registradas en `requirements.txt`
- No es necesario instalar las librerías individualmente
- La carpeta `.datos\entrada` no debe compartirse ni incluirse en el repositorio, ya que es información confidencial de los documentos originales

---

**Proyecto:** Minería de Textos

**Lenguaje:** Python