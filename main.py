import requests
import os
import zipfile
import json
import shutil
import tempfile
import tkinter as tk
from tkinter import messagebox

# URL del archivo JSON de la versión en GitHub
GITHUB_JSON_URL = "https://raw.githubusercontent.com/usuario/repositorio/main/version.json"

# Rutas locales
CARPETA_INSTALACION = "juegos"
RUTA_VERSION_LOCAL = os.path.join(CARPETA_INSTALACION, "version.json")

# Comprobación de versión
def obtener_version_remota():
    response = requests.get(GITHUB_JSON_URL)
    if response.status_code == 200:
        version_info = response.json()
        return version_info
    else:
        print("Error al obtener la versión remota.")
        return None

def obtener_version_local():
    if os.path.exists(RUTA_VERSION_LOCAL):
        with open(RUTA_VERSION_LOCAL, "r") as file:
            return json.load(file).get("version")
    return None

def guardar_version_local(version_info):
    os.makedirs(CARPETA_INSTALACION, exist_ok=True)
    with open(RUTA_VERSION_LOCAL, "w") as file:
        json.dump({"version": version_info["version"], "juegos": version_info["juegos"]}, file)

# Función para descargar los juegos
def descargar_juegos(juegos_info):
    for juego_info in juegos_info:
        juego = juego_info["nombre"]
        url = juego_info["url"]
        print(f"Descargando {juego} desde Gamejolt...")
        response = requests.get(url)
        if response.status_code == 200:
            archivo_temp = tempfile.NamedTemporaryFile(delete=False)
            with open(archivo_temp.name, "wb") as f:
                f.write(response.content)
            print(f"Juego {juego} descargado.")
            descomprimir_juego(archivo_temp.name, juego)
            os.remove(archivo_temp.name)  # Eliminar archivo temporal después de la descompresión
        else:
            print(f"Error al descargar {juego}.")

# Función para descomprimir el archivo de juego
def descomprimir_juego(archivo_zip, juego):
    temp_dir = tempfile.mkdtemp()  # Crear carpeta temporal
    try:
        with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        print(f"{juego} descomprimido en {temp_dir}")
        instalar_juego(temp_dir, juego)
    except zipfile.BadZipFile:
        print(f"Error al descomprimir el archivo {juego}. No es un archivo ZIP válido.")
    except Exception as e:
        print(f"Error al descomprimir {juego}: {e}")

# Función para mover el juego descomprimido a la carpeta de instalación
def instalar_juego(temp_dir, juego):
    juego_carpeta = os.path.join(CARPETA_INSTALACION, juego)
    if not os.path.exists(juego_carpeta):
        os.makedirs(juego_carpeta)

    for item in os.listdir(temp_dir):
        src_path = os.path.join(temp_dir, item)
        dst_path = os.path.join(juego_carpeta, item)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

# Función para comprobar si hay una actualización
def comprobar_actualizacion():
    version_local = obtener_version_local()
    version_info_remota = obtener_version_remota()
    
    if version_info_remota and version_info_remota["version"] != version_local:
        respuesta = messagebox.askyesno("Actualización disponible", f"Una nueva versión (v{version_info_remota['version']}) está disponible. ¿Quieres actualizar ahora?")
        if respuesta:
            descargar_juegos(version_info_remota["juegos"])
            guardar_version_local(version_info_remota)
            messagebox.showinfo("Actualización completada", "La actualización se ha completado.")
        else:
            print("El usuario decidió no actualizar.")
    else:
        print("No hay actualizaciones disponibles.")

# Función para cargar los juegos desde el JSON
def cargar_aplicaciones():
    juegos = []
    for juego in os.listdir(CARPETA_INSTALACION):
        juego_path = os.path.join(CARPETA_INSTALACION, juego, "app.json")  # Se asume que cada juego tiene su archivo app.json
        if os.path.exists(juego_path):
            with open(juego_path, "r") as f:
                datos = json.load(f)
                juegos.append(datos)
    return juegos

# Función para abrir un juego
def abrir_juego(ruta_relativa):
    ruta_completa = os.path.join(os.getcwd(), ruta_relativa)
    os.startfile(ruta_completa)

# Crear ventana de interfaz gráfica
def crear_ventana(juegos):
    ventana = tk.Tk()
    ventana.title("Lanzador de Juegos")
    ventana.geometry("300x300")

    for juego in juegos:
        nombre = juego["nombre"]
        ruta_relativa = juego["ruta"]
        boton = tk.Button(ventana, text=nombre, command=lambda ruta=ruta_relativa: abrir_juego(ruta))
        boton.pack(pady=10)

    ventana.mainloop()

# Iniciar el proceso
if __name__ == "__main__":
    comprobar_actualizacion()
    juegos = cargar_aplicaciones()
    crear_ventana(juegos)
