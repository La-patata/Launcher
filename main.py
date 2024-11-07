import requests
import os
import zipfile
import json
import tkinter as tk
from tkinter import messagebox

# URL de GitHub para el JSON de versión y juegos
URL_VERSION_JSON = "https://raw.githubusercontent.com/La-patata/Launcher/refs/heads/main/version.json"

# Rutas de instalación
CARPETA_INSTALACION = "juegos"
RUTA_VERSION_LOCAL = os.path.join(CARPETA_INSTALACION, "version.json")

# Asegurarse de que la carpeta de instalación exista
os.makedirs(CARPETA_INSTALACION, exist_ok=True)

# Función para descargar y descomprimir juegos
def descargar_y_descomprimir_juegos(url):
    # Ruta del archivo comprimido en la carpeta de instalación
    archivo_comprimido = os.path.join(CARPETA_INSTALACION, "contenido_comprimido")

    # Descargar el archivo comprimido (puede ser ZIP, RAR o 7z)
    if descargar_archivo(url, archivo_comprimido):
        # Descomprimir el archivo
        if descomprimir_archivo(archivo_comprimido, CARPETA_INSTALACION):
            # Eliminar el archivo comprimido después de descomprimir
            os.remove(archivo_comprimido)
            print(f"Juegos instalados en: {CARPETA_INSTALACION}")
        else:
            print("Error al descomprimir el archivo.")
    else:
        print("Error al descargar el archivo comprimido.")

# Función para descargar el archivo desde una URL dada
def descargar_archivo(url, ruta_destino):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(ruta_destino, "wb") as file:
            for chunk in response.iter_content(1024):
                if chunk:
                    file.write(chunk)
        print(f"Descarga completa: {ruta_destino}")
        return True
    else:
        print(f"Error al descargar el archivo: {response.status_code}")
        return False

# Función para descomprimir archivos ZIP, RAR o 7z
def descomprimir_archivo(archivo_comprimido, carpeta_destino):
    try:
        if archivo_comprimido.endswith('.zip'):
            with zipfile.ZipFile(archivo_comprimido, 'r') as zip_ref:
                zip_ref.extractall(carpeta_destino)
            print(f"Descompresión completada en: {carpeta_destino}")
            return True

        else:
            print("Tipo de archivo no soportado.")
            return False

    except Exception as e:
        print(f"Error al descomprimir el archivo: {e}")
        return False

# Función para comprobar actualizaciones
def comprobar_actualizacion():
    version_local = obtener_version_local()
    version_remota, juegos = obtener_version_remota()

    if version_remota and version_remota != version_local:
        respuesta = messagebox.askyesno("Actualización Disponible",
                                        f"Hay una nueva versión disponible (v{version_remota}). ¿Quieres actualizar ahora?")
        if respuesta:
            for juego in juegos:
                url_juego = juego["url"]
                descargar_y_descomprimir_juegos(url_juego)
            guardar_version_local(version_remota)
            messagebox.showinfo("Actualización Completa", "La actualización se ha completado.")
    else:
        print("No hay actualizaciones disponibles o la versión está actualizada.")

# Función para obtener la versión remota y URLs de juegos
def obtener_version_remota():
    response = requests.get(URL_VERSION_JSON)
    if response.status_code == 200:
        data = response.json()
        return data.get("version"), data.get("juegos", [])
    return None, []

# Función para obtener la versión local desde JSON
def obtener_version_local():
    if os.path.exists(RUTA_VERSION_LOCAL):
        with open(RUTA_VERSION_LOCAL, "r") as file:
            return json.load(file).get("version")
    return None

# Función para guardar la versión local después de una actualización
def guardar_version_local(version):
    os.makedirs(CARPETA_INSTALACION, exist_ok=True)
    with open(RUTA_VERSION_LOCAL, "w") as file:
        json.dump({"version": version}, file)

# Interfaz de usuario
ventana = tk.Tk()
ventana.title("Lanzador de Juegos")
ventana.geometry("300x300")

# Comprobar actualizaciones al iniciar
comprobar_actualizacion()

# Ejecutar la aplicación de interfaz gráfica
ventana.mainloop()

