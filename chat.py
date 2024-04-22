import os
import re
import requests
import sqlite3
import unicodedata
import customtkinter as ctk  # Importar CustomTkinter
from tkinter import (
     Toplevel, PhotoImage, Label, Button, scrolledtext, messagebox,
    simpledialog,  LEFT, RIGHT, TOP, X, BOTH, END, 
)
import os

# Inicialización de variables globales
login_window = None
welcome_window = None
chat_window = None

API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.getenv('MY_API_KEY')


conn = sqlite3.connect('usuarios.db')
conn.row_factory = sqlite3.Row # Esto permite acceder a las columnas por nombre
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS usuarios
             (ID INTEGER PRIMARY KEY AUTOINCREMENT,
              Nombre TEXT NOT NULL,
              Apellido TEXT NOT NULL)''')
conn.commit()


def create_database():
    if os.path.exists('usuarios.db'):
        messagebox.showinfo("Crear Base de Datos", "La base de datos ya está creada.")
    else:
        conn = sqlite3.connect('usuarios.db')  # Abre la conexión a la base de datos
        c = conn.cursor()  # Crea un cursor
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                      Nombre TEXT NOT NULL,
                      Apellido TEXT NOT NULL)''')
        conn.commit()
        messagebox.showinfo("Crear Base de Datos", "Base de datos creada exitosamente.")
    
    conn.close()  # Cierra la conexión después de usarla



# --- INTERACCIÓN CON CHATGPT ---

manual_text = """
### Manual de Usuario para Interactuar con NickyGPT y la Base de Datos

#### Comandos Básicos:
- **Añadir Usuarios**: "quiero añadir un usuario llamado [Nombre] y que tenga el apellido [Apellido]"
- **Eliminar Usuarios**: "elimina a [ID]" o "elimina al usuario [Nombre] [Apellido]"
- **Modificar Información de Usuarios**: "cambia el nombre de [nombre_actual] a [nuevo_nombre]"
- **Consultar Información de Usuarios**: "cuál es el nombre del usuario con apellido [Apellido]"

#### Gestión de Columnas:
- **Añadir Columnas**: "añade la columna [nombre_columna]"
- **Eliminar Columnas**: "elimina la columna [nombre_columna]"

#### Consultas Específicas:
- **Datos de Columnas Específicas**: "cuál es la [columna] del usuario con ID [ID]" o "dame todas las [columna_plural]"

### Cómo Usar el Sistema:
1. **Iniciar la Aplicación**: Abre la aplicación donde está integrado NickyGPT.
2. **Escribir Comando**: En el espacio provisto, escribe el comando según las instrucciones dadas arriba.
3. **Enviar Comando**: Envía el comando y espera la respuesta de NickyGPT.
4. **Ver Resultados**: Los resultados de la acción solicitada serán mostrados en la interfaz de la aplicación.
"""

def get_chatgpt_response(user_input):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Aquí proporcionas ejemplos de cómo diferentes comandos pueden ser formulados y cómo deberían ser interpretados
    context_with_accents = """Ejemplos:
    Usuario: cual es la direccion de sofia
    Sistema: la dirección del usuario con nombre Sofia es Av Madrid
    Usuario: quiero añadir un usuario llamado Alex y que tenga el apellido Garcia
    Sistema: añade un nuevo usuario con el nombre Alex y apellido Garcia
    Usuario: elimina a la id 123
    Sistema: elimina el usuario con ID 123
    Usuario: quiero cambiar el nombre de pedro a manolo
    Sistema: cambia el nombre del usuario pedro a manolo
    Usuario: necesito cambiar el apellido de la id 456 a Martínez
    Sistema: cambia el apellido del usuario con ID 456 a Martínez
    Usuario: borrar al usuario John Smith por favor
    Sistema: elimina el usuario con nombre John y apellido Smith
    Usuario: cambia nombre de usuario de 789 a Jane
    Sistema: cambia el nombre del usuario con ID 789 a Jane
    Usuario: cambia apellido de 423 a Manolo
    Sistema: cambia el apellido del usuario con ID 423 a Manolo
    Usuario: cambia el apellido de María a Rodríguez
    Sistema: cambia el apellido del usuario con nombre María a Rodríguez
    Usuario: cambia el nombre de Ernesto a Pau
    Sistema: cambia el nombre del usuario Ernesto a Pau
    Usuario: dame todos los nombres de los usuarios
    Sistema: los nombres de todos los usuarios son: Alex, John, Jane, Pedro, Sofia
    Usuario: dame todos los apellidos de los usuarios
    Sistema: los apellidos de todos los usuarios son: Garcia, Martínez, Doe, Smith, Montero
    Usuario: cuál es el nombre del usuario con apellido Garcia
    Sistema: el nombre del usuario con apellido Garcia es Marco
    Usuario: cual es el apellido de Manolo
    Sistema: el apellido del usuario con nombre Manolo es Fernandez
    Usuario: cual es el apellido del usuario con nombre Jane
    Sistema: el apellido del usuario con nombre Jane es Doe
    Usuario: cual es la ID de Ramon
    Sistema: la ID del usuario con nombre Ramon es 435
    Usuario: cual es la ID del usaurio con nombre Alex
    Sistema: la ID del usuario con nombre Alex es 102
    Usuario: cual es la ID del apellido alfonso
    Sistema: la ID del usuario con apellido Alfonso es 654
    Usuario: cual es la ID del usuario con apellido garcia
    Sistema: la ID del usuario con apellido García es 205
    Usuario: cual es la ID del usuario con nombre marcos
    Sistema: la ID del usuario con nombre Marcos es 315
    Usuario: cual es la ID del usuario con apellido martinez
    Sistema: la ID del usuario con apellido Martínez es 409
    Usuario: cual es el nombre de 456
    Sistema: el nombre del usuario con ID 456 es Pedro
    Usuario: cual es el apellido de 23
    Sistema: el apellido del usuario con ID 23 es Garcia
    Usuario: cual es el apellido de la ID 789
    Sistema: el apellido del usuario con ID 789 es Martínez
    Usuario: añade la columna direccion
    Sistema: añade la columna direccion
    Usuario: cambia la direccion de marta a av albaida
    Sistema: añade la direccion Av Albaida al usuario con nombre Marta
    Usuario: cambia la direccion de 65 a gran via
    Sistema: cambia la direccion del usuario con ID 65 a Gran Via
    Usuario: elimina la columna direccion
    Sistema: elimina la columna direccion
    Usuario: cual es la dirección de 264
    Sistema: la dirección del usuario con ID 264 es Gran Via 23
    Usuario: dame todas las direcciones
    Sistema: las dirección de todos los usuarios son: Gran Via 23, Paseo de la Reforma 123, Calle Falsa 456
    Usuario: cual es el teléfono de 232
    Sistema: el teléfono del usuario con ID 232 es 424853135
    Usuario: dame todos los telefonos
    Sistema: los teléfono de todos los usuarios son: 123654345, 231657987, 12365123
    Usuario: ayuda
    Sistema: Aqui tienes el manual de ayuda:
    Usuario: elimina la dirección del usuario con ID 123
    Sistema: elimina la dirección del usuario con ID 123
    Usuario: elimina la dirección del usuario llamado Carlos
    Sistema: elimina la dirección del usuario con nombre Carlos
    Usuario: crea a Marta Jiménez con la dirección Av Albaida
    Sistema: añade un nuevo usuario con el nombre Marta, apellido Jiménez y dirección Av Albaida
    Usuario: registra el correo juan@example.com para Juan
    Sistema: añade el correo juan@example.com al usuario con nombre Juan
    Usuario: el teléfono de Maria es 5551234324
    Sistema: añade el teléfono 5551234324 al usuario con nombre María
    Usuario: cual es la fecha de nacimiento de Jorge
    Sistema: la fecha de nacimiento del usuario con nombre Jorge es 1984-03-12
    Usuario: cual es el telfono de Beatriz
    Sistema: el teléfono del usuario con nombre Beatriz es 654734247
    Usuario: elimina la base de datos
    Sistema: elimina la base de datos
    Usuario: crea la base de datos
    Sistema: crea la base de datos
    """
    context = remove_accents(context_with_accents)

 

    prompt = f"{context}Usuario: {user_input}\nSistema:"

    data = {
        "model": "gpt-4-turbo",
        "messages": [{"role": "system", "content": context}, {"role": "user", "content": user_input}]
    }

    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        # Interpretar la respuesta para extraer la acción del sistema
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        return "Error en la respuesta de la API."

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])   

def handle_database_command(command):
    chat_response1 = get_chatgpt_response(command)
    chat_response = remove_accents(chat_response1)
    print("Respuesta del Chat:", chat_response)  # Para depuración
    if command.lower() == "Aqui tienes el manual de ayuda:":
        return manual_text
    # Añadir y eliminar
    add_match = re.search(r'(?:anade|añade) un nuevo usuario con el nombre (\w+) y apellido (\w+)', chat_response, re.IGNORECASE)
    if add_match:
        name, surname = add_match.groups()
        return add_user(name, surname)
    delete_match = re.search(r"elimina el usuario con nombre (\w+)", chat_response, re.IGNORECASE)
    if delete_match:
        name = delete_match.group(1)
        return delete_user_by_name(name)
    delete_match = re.search(r"elimina el usuario con ID (\d+)", chat_response, re.IGNORECASE)
    if delete_match:
        user_id = int(delete_match.group(1))
        return delete_user_by_id(user_id)
    # Eliminar información de una columna específica por ID o nombre
    remove_info_match = re.search(r'elimina la (\w+) del usuario (con ID (\d+)|con nombre (\w+))', chat_response, re.IGNORECASE)
    if remove_info_match:
        column_name, _, user_id, name = remove_info_match.groups()
        if user_id:
            return remove_user_info_by_id(user_id, column_name)
        elif name:
            return remove_user_info_by_name(name, column_name)
           # Añadir usuario con información adicional
    add_with_info_match = re.search(r'(?:anade|añade) un nuevo usuario con el nombre (\w+), apellido (\w+) y (\w+) (.+)', chat_response, re.IGNORECASE)
    if add_with_info_match:
        name, surname, column, info = add_with_info_match.groups()
        return add_user_with_info(name, surname, column, info)

    # Cambiar informacion
    update_match = re.search(r"cambia el nombre del usuario (\w+) a (\w+)", chat_response, re.IGNORECASE)
    if update_match:
        old_name, new_name = update_match.groups()
        return update_user_name_by_name(old_name, new_name)
    update_match = re.search(r"cambia el apellido del usuario con nombre (\w+) a (\w+)", chat_response, re.IGNORECASE)
    if update_match:
        old_name, new_surname = update_match.groups()
        return update_user_surname_by_name(old_name, new_surname)
    update_match = re.search(r"cambia el nombre del usuario con ID (\d+) a (\w+)", chat_response, re.IGNORECASE)
    if update_match:
        user_id, new_name = update_match.groups()
        return update_user_field(user_id, "Nombre", new_name)
    update_surname_match = re.search(r"cambia el apellido del usuario con ID (\d+) a (\w+)", chat_response, re.IGNORECASE)
    if update_surname_match:
        user_id, new_surname = update_surname_match.groups()
        return update_user_field(user_id, "Apellido", new_surname)

    #Consultar infromacion 
    id_by_name_match = re.search(r"la ID del usuario con nombre (\w+) es (\d+)", chat_response, re.IGNORECASE)
    if id_by_name_match:
        name = id_by_name_match.group(1)
        return fetch_user_id_by_name(name)
    id_by_surname_match = re.search(r"la ID del usuario con apellido (\w+) es (\d+)", chat_response, re.IGNORECASE)
    if id_by_surname_match:
        surname = id_by_surname_match.group(1)
        return fetch_user_id_by_surname(surname)
    name_by_id_match = re.search(r"el nombre del usuario con ID (\d+) es (\w+)", chat_response, re.IGNORECASE)
    if name_by_id_match:
        user_id = int(name_by_id_match.group(1))
        return fetch_user_name_by_id(user_id)
    surname_by_id_match = re.search(r"el apellido del usuario con ID (\d+) es (\w+)", chat_response, re.IGNORECASE)
    if surname_by_id_match:
        user_id = int(surname_by_id_match.group(1))
        return fetch_user_surname_by_id(user_id)
    name_by_surname_match = re.search(r"el nombre del usuario con apellido (\w+) es (\w+)", chat_response, re.IGNORECASE)
    if name_by_surname_match:
        surname = name_by_surname_match.group(1)
        return fetch_user_name_by_surname(surname)
    surname_by_name_match = re.search(r"el apellido del usuario con nombre (\w+) es (\w+)", chat_response, re.IGNORECASE)
    if surname_by_name_match:
        name = surname_by_name_match.group(1)
        return fetch_user_surname_by_name(name)

    # Consultar informacion a gran escala
    all_names_match = re.search(r"los nombres de todos los usuarios son", chat_response, re.IGNORECASE)
    print(chat_response)
    print(all_names_match)
    if all_names_match:
        return fetch_all_user_names()
    all_surnames_match = re.search(r"los apellidos de todos los usuarios son", chat_response, re.IGNORECASE)
    if all_surnames_match:
        return fetch_all_user_surnames()
    

        #  columnas
    add_column_match = re.search(r'(?:anade|añade) la columna (\w+)', chat_response, re.IGNORECASE)
    if add_column_match:
        column_name = add_column_match.group(1)
        return add_column_to_users(column_name)
    
        # Actualización de información basada en el nombre
    update_info_name_match = re.search(r"cambia (?:el|la) (\w+) del usuario con nombre (\w+) a (.+)$", chat_response, re.IGNORECASE)
    if update_info_name_match:
        column, info, name = update_info_name_match.groups()
        return update_user_info_by_name()
    
    update_info_name_match1 = re.search(r"(?:cambia|actualiza|anade|añade) (?:el|la) (\w+) (.+) al usuario con nombre (\w+)", chat_response, re.IGNORECASE)
    if update_info_name_match1:
        column, info, name = update_info_name_match1.groups()
        return update_user_info_by_name(name, column, info)
    
    update_info_match = re.search(r"cambia (?:el|la) (\w+) del usuario con ID (\d+) a (.+)$", chat_response, re.IGNORECASE)
    if update_info_match:
        column_name, user_id, new_info = update_info_match.groups()
        return update_user_info_in_column(user_id, column_name, new_info)
    delete_column_match = re.search(r"elimina la columna (\w+)", chat_response, re.IGNORECASE)
    if delete_column_match:
        column_name = delete_column_match.group(1)
        return delete_column(tabla='usuarios', columna=column_name)  
    # Extraer el valor de una columna específica por ID
    column_value_match = re.search(r"(?:el|la) (\w+) del usuario con ID (\d+) es (.+)", chat_response, re.IGNORECASE)
    if column_value_match:
        column_name, user_id, value = column_value_match.groups()
        return fetch_column_value_by_id(column_name, int(user_id))  # No incluyas `value` aquí

    # Extraer todos los valores de una columna
    all_column_values_match = re.search(r"(?:los|las) (\w+) de todos (?:los|las) usuarios son", chat_response, re.IGNORECASE)
    if all_column_values_match:
        column_name = all_column_values_match.group(1)
        return fetch_all_column_values(column_name)
    
    column_value_by_name_match = re.search(r"(?:el|la) (\w+) del usuario con nombre (\w+) es (.+)", chat_response, re.IGNORECASE)
    if column_value_by_name_match:
        column_name, user_name, _ = column_value_by_name_match.groups()
        return fetch_column_value_by_name(column_name, user_name)
    
    # Base de datos
    delete_data = re.search(r"elimina la base de datos", chat_response, re.IGNORECASE)
    if delete_data:
        return delete_database()
    create_data = re.search(r"crea la base de datos", chat_response, re.IGNORECASE)
    if create_data:
        return create_database()
    return "Lo siento, podrias especificar un poco mas"





# Asegúrate de que la función add_user, delete_user_by_id, delete_user_by_name, etc., están correctamente definidas.
    





import sqlite3
from tkinter import messagebox
    #--- Actualizar infromacion ---#

def update_user_name_by_surname(surname, new_name):
    try:
        c.execute("UPDATE usuarios SET Nombre = ? WHERE Apellido = ?", (new_name, surname))
        conn.commit()
        return f"Nombre actualizado a {new_name} para usuarios con apellido {surname}."
    except sqlite3.Error as e:
        return f"Error al actualizar el nombre: {e}"

def update_user_surname_by_name(name, new_surname):
    try:
        c.execute("UPDATE usuarios SET Apellido = ? WHERE Nombre = ?", (new_surname, name))
        conn.commit()
        return f"Apellido actualizado a {new_surname} para usuarios con nombre {name}."
    except sqlite3.Error as e:
        return f"Error al actualizar el apellido: {e}"
def update_user_name_by_name(old_name, new_name):
    """
    Actualiza el nombre de un usuario en la base de datos.
    :param old_name: Nombre actual del usuario.
    :param new_name: Nuevo nombre para el usuario.
    """
    try:
        c.execute("UPDATE usuarios SET Nombre = ? WHERE Nombre = ?", (new_name, old_name))
        conn.commit()
        return f"Nombre actualizado de {old_name} a {new_name}."
    except sqlite3.Error as e:
        return f"Error al actualizar el nombre del usuario: {e}"
    #--- Fin actualziar informacion ---#

    #--- Añadir y eliminar ---#


def add_column_to_users(column_name):
    """
    Adds a new TEXT column to the 'usuarios' table.
    :param column_name: Name of the new column to add.
    """
    try:
        c.execute(f"ALTER TABLE usuarios ADD COLUMN {column_name} TEXT")
        conn.commit()
        return f"Columna '{column_name}' añadida correctamente."
    except sqlite3.OperationalError as e:
        return "Error al añadir la columna: " + str(e)
    
def delete_user_by_name(name):
    try:
        c.execute("DELETE FROM usuarios WHERE Nombre = ?", (name,))
        conn.commit()
        return "Usuario eliminado correctamente."
    except sqlite3.Error as e:
        return "Error al eliminar el usuario: " + str(e)

def delete_user_by_id(user_id):
    try:
        c.execute("DELETE FROM usuarios WHERE ID = ?", (user_id,))
        conn.commit()
        return "Usuario eliminado correctamente."
    except sqlite3.Error as e:
        return "Error al eliminar el usuario: " + str(e)

def update_user_info_in_column(user_id, column_name, new_info):
    """
    Updates the information in a specific column for a given user ID in the 'usuarios' table.
    :param user_id: ID of the user.
    :param column_name: Name of the column to be updated.
    :param new_info: New information to be updated in the column.
    """
    try:
        c.execute(f"UPDATE usuarios SET {column_name} = ? WHERE ID = ?", (new_info, user_id))
        conn.commit()
        return f"Información actualizada en columna '{column_name}'."
    except sqlite3.Error as e:
        return "Error al actualizar la información en la columna: " + str(e)
def remove_user_info_by_id(user_id, column):
    try:
        c.execute(f"UPDATE usuarios SET {column} = NULL WHERE ID = ?", (user_id,))
        conn.commit()
        return f"Información '{column}' eliminada correctamente para el usuario con ID {user_id}."
    except sqlite3.Error as e:
        return f"Error al eliminar la información: {e}"
def add_user_with_info(name, surname, column, info):
    if es_columna_valida(column):
        try:
            # Usar una inserción segura sin usar parámetros para el nombre de la columna
            c.execute(f"INSERT INTO usuarios (Nombre, Apellido, {column}) VALUES (?, ?, ?)", (name, surname, info))
            conn.commit()
            return "Usuario añadido correctamente con información adicional."
        except sqlite3.IntegrityError as e:
            return f"Error al añadir el usuario: {e}"
        except sqlite3.Error as e:
            return f"Error de base de datos: {e}"
    else:
        return "La columna especificada no es válida o no existe."

def remove_user_info_by_name(name, column):
    try:
        c.execute(f"UPDATE usuarios SET {column} = NULL WHERE Nombre = ?", (name,))
        conn.commit()
        return f"Información '{column}' eliminada correctamente para el usuario con nombre {name}."
    except sqlite3.Error as e:
        return f"Error al eliminar la información: {e}"

#Consultar infromacion
def fetch_user_id_by_name(name):
    try:
        c.execute("SELECT ID FROM usuarios WHERE Nombre = ?", (name,))
        results = c.fetchall()
        if results:
            ids = [str(result[0]) for result in results]
            return f"Los IDs del usuario con nombre {name} son: {', '.join(ids)}"
        else:
            return f"No se encontró un usuario con el nombre {name}."
    except sqlite3.Error as e:
        return f"Error en la consulta: {e}"

def fetch_user_id_by_surname(surname):
    try:
        c.execute("SELECT ID FROM usuarios WHERE Apellido = ?", (surname,))
        result = c.fetchone()
        if result:
            return f"El ID del usuario con apellido {surname} es {result[0]}"
        else:
            return f"No se encontró un usuario con el apellido {surname}."
    except sqlite3.Error as e:
        return f"Error en la consulta: {e}"

def fetch_user_name_by_id(user_id):
    try:
        c.execute("SELECT Nombre FROM usuarios WHERE ID = ?", (user_id,))
        result = c.fetchone()
        if result:
            return f"El nombre del usuario con ID {user_id} es {result[0]}"
        else:
            return f"No se encontró un usuario con el ID {user_id}."
    except sqlite3.Error as e:
        return f"Error en la consulta: {e}"

def fetch_user_surname_by_id(user_id):
    try:
        c.execute("SELECT Apellido FROM usuarios WHERE ID = ?", (user_id,))
        result = c.fetchone()
        if result:
            return f"El apellido del usuario con ID {user_id} es {result[0]}"
        else:
            return f"No se encontró un usuario con el ID {user_id}."
    except sqlite3.Error as e:
        return f"Error en la consulta: {e}"
def fetch_user_name_by_surname(surname):
    try:
        c.execute("SELECT ID, Nombre FROM usuarios WHERE Apellido = ?", (surname,))
        results = c.fetchall()
        if results:
            names = [f"ID {result[0]}: {result[1]}" for result in results]
            return f"Los nombres de los usuarios con apellido {surname} son: {', '.join(names)}"
        else:
            return f"No se encontró un usuario con el apellido {surname}."
    except sqlite3.Error as e:
        return f"Error en la consulta: {e}"


def fetch_user_surname_by_name(name):
    try:
        c.execute("SELECT ID, Apellido FROM usuarios WHERE Nombre = ?", (name,))
        results = c.fetchall()
        if results:
            surnames = [f"ID {result[0]}: {result[1]}" for result in results]
            return f"Los apellidos de los usuarios con nombre {name} son: {', '.join(surnames)}"
        else:
            return f"No se encontró un usuario con el nombre {name}."
    except sqlite3.Error as e:
        return f"Error en la consulta: {e}"


    #--- Fin Consultar infromacion ---#

    #--- Columnas ---#
    
def es_columna_valida(columna):
    c.execute("PRAGMA table_info(usuarios)")
    columnas = [row[1] for row in c.fetchall()]  # Obtiene los nombres de las columnas de la tabla usuarios
    return columna in columnas

def add_column(column_name):
    # Primero verifica si la columna ya existe para evitar errores de SQL
    if es_columna_valida(column_name):
        return "La columna ya existe."

    try:
        # Añade la columna a la tabla de usuarios
        c.execute(f"ALTER TABLE usuarios ADD COLUMN {column_name} TEXT")
        conn.commit()
        return f"Columna '{column_name}' añadida correctamente."
    except sqlite3.OperationalError as e:
        return "Error al añadir la columna: " + str(e)
    except sqlite3.Error as e:
        return "Error en la base de datos: " + str(e)


def update_user_info_by_name(name, column, info):
    try:
        c.execute(f"UPDATE usuarios SET {column} = ? WHERE Nombre = ?", (info, name))
        conn.commit()
        return f"Información actualizada: {column} ahora es '{info}' para el usuario llamado {name}."
    except sqlite3.Error as e:
        return f"Error al actualizar la información del usuario: {e}"

def delete_column(tabla, columna):
    try:
        # Crear un nombre temporal para la nueva tabla
        new_table = f"{tabla}_new"
        
        # Obtener los nombres de todas las columnas menos la que se quiere eliminar
        c.execute(f"PRAGMA table_info({tabla})")
        columns = [info[1] for info in c.fetchall() if info[1] != columna]
        
        # Crear la nueva tabla sin la columna
        columns_str = ", ".join(columns)
        c.execute(f"CREATE TABLE {new_table} AS SELECT {columns_str} FROM {tabla}")
        
        # Eliminar la tabla original
        c.execute(f"DROP TABLE {tabla}")
        
        # Renombrar la nueva tabla con el nombre de la tabla original
        c.execute(f"ALTER TABLE {new_table} RENAME TO {tabla}")
        conn.commit()
        return f"Columna '{columna}' eliminada correctamente."
    except sqlite3.Error as e:
        return f"Error al eliminar la columna: {e}"

def update_column_info(user_id, column_name, new_info):
    try:
        c.execute(f"UPDATE usuarios SET {column_name} = ? WHERE ID = ?", (new_info, user_id))
        conn.commit()
        return f"Información actualizada en columna '{column_name}'."
    except sqlite3.Error as e:
        return "Error al actualizar la información en la columna: " + str(e)
def fetch_column_value_by_name(column_name, name):
    try:
        c.execute(f"SELECT {column_name} FROM usuarios WHERE Nombre = ?", (name,))
        result = c.fetchone()
        if result:
            return f"El {column_name} del usuario llamado {name} es {result[0]}"
        else:
            return f"No se encontró el {column_name} para un usuario con nombre {name}."
    except sqlite3.Error as e:
        return f"Error en la consulta: {e}"

def fetch_column_value_by_id(column_name, user_id):
    try:
        c.execute(f"SELECT {column_name} FROM usuarios WHERE ID = ?", (user_id,))
        result = c.fetchone()
        if result:
            return f"El {column_name} del usuario con ID {user_id} es {result[0]}"
        else:
            return f"No se encontró un usuario con el ID {user_id}."
    except sqlite3.Error as e:
        return f"Error en la consulta: {e}"

def fetch_all_column_values(column_name):
    try:
        c.execute(f"SELECT {column_name} FROM usuarios")
        results = c.fetchall()
        values = [result[0] for result in results if result[0] is not None]  # Asegúrate de que los valores no nulos son considerados
        if values:
            return f"Los {column_name}s de todos los usuarios son: {', '.join(map(str, values))}"
        else:
            return f"No hay valores registrados en la columna {column_name}."
    except sqlite3.Error as e:
        return f"Error al recuperar {column_name}: {e}"




#--- Fin columnas ---#

def fetch_all_user_names():
    try:
        c.execute("SELECT Nombre FROM usuarios")
        results = c.fetchall()
        names = [result[0] for result in results]
        if names:
            return f"Los nombres de todos los usuarios son: {', '.join(names)}"
        return "No hay usuarios registrados."
    except sqlite3.Error as e:
        return f"Error al recuperar los nombres de los usuarios: {e}"


def count_users():
    try:
        c.execute("SELECT COUNT(*) FROM usuarios")
        result = c.fetchone()
        if result:
            return f"Hay {result[0]} usuarios en el sistema"
        return "Error al contar los usuarios."
    except sqlite3.Error as e:
        return f"Error al contar los usuarios: {e}"

def fetch_all_user_surnames():
    try:
        c.execute("SELECT Apellido FROM usuarios")
        results = c.fetchall()
        surnames = [result[0] for result in results]
        if surnames:
            return f"Los apellidos de todos los usuarios son: {', '.join(surnames)}"
        return "No hay usuarios registrados."
    except sqlite3.Error as e:
        return f"Error al recuperar los apellidos de los usuarios: {e}"


def add_user(name, surname):
    try:
        c.execute("INSERT INTO usuarios (Nombre, Apellido) VALUES (?, ?)", (name, surname))
        conn.commit()
        return "Usuario añadido correctamente."
    except sqlite3.IntegrityError as e:
        return "Error al añadir el usuario: " + str(e)

def update_user_field(user_id, field, new_value):
    try:
        c.execute(f"UPDATE usuarios SET {field} = ? WHERE ID = ?", (new_value, user_id))
        conn.commit()
        if c.rowcount:
            return f"{field} actualizado a '{new_value}' para el usuario ID {user_id}."
        return f"No se encontró un usuario con la ID {user_id}."
    except sqlite3.Error as e:
        return f"Error al actualizar el usuario: {e}"



def delete_database():
    try:
        c.execute("DROP TABLE IF EXISTS usuarios")
        conn.commit()
        return "Base de datos eliminada correctamente."
    except sqlite3.Error as e:
        return "Error al eliminar la base de datos: " + str(e)

def fetch_user_by_id(user_id):
    c.execute("SELECT * FROM usuarios WHERE ID = ?", (user_id,))
    return c.fetchone()

def fetch_user_info(username):
    print(f"Iniciando sesión con usuario: {username}")
    url = 'https://abiding-heavy-outrigger.glitch.me/articles/'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            users = response.json()
            for user in users:
                # Comprueba si el username coincide y si el campo username existe
                if 'username' in user and user['username'] == username:
                    return user
            messagebox.showinfo("Usuario no encontrado", "El usuario solicitado no existe.")
            return None
        else:
            messagebox.showerror("Error", f"No se pudo recuperar la información. Código de estado: {response.status_code}")
            return None
    except requests.RequestException as e:
        messagebox.showerror("Error de red", str(e))
        return None




def update_user_info(username, new_password, photo_path):
    url = 'https://abiding-heavy-outrigger.glitch.me/articles/'
    data = {'password': new_password, 'photo': photo_path}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            messagebox.showinfo("Éxito", "Información actualizada correctamente.")
        else:
            messagebox.showerror("Error", f"No se pudo actualizar la información. Código de estado: {response.status_code}")
    except requests.RequestException as e:
        messagebox.showerror("Error de red", str(e))


def fetch_users_by_surname(surname):
    c.execute("SELECT * FROM usuarios WHERE Apellido = ?", (surname,))
    return c.fetchall()


def fetch_usuarios():
    """Esta función recupera todos los usuarios para verificar existencias."""
    url = 'https://abiding-heavy-outrigger.glitch.me/articles/'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except requests.RequestException:
        messagebox.showerror("Error", "Error de red, intente de nuevo más tarde.")
        return []

def check_login(username, password):
    """Verifica si el usuario existe con la contraseña correcta."""
    users = fetch_usuarios()
    for user in users:
        if 'username' in user and 'password' in user and user['username'] == username and user['password'] == password:
            return True
    return False

def register_user(username, password):
    """Registra un nuevo usuario si no existe."""
    url = 'https://abiding-heavy-outrigger.glitch.me/articles/'
    user_data = {'username': username, 'password': password}
    try:
        response = requests.post(url, json=user_data)
        if response.status_code == 201:
            return True
        else:
            return False
    except requests.RequestException:
        messagebox.showerror("Error", "Error de red, intente de nuevo más tarde.")
        return False

# Resto del código sin cambios...


from tkinter import Toplevel, Button, Label, PhotoImage, Frame
import os

from tkinter import Toplevel, Button, Label, PhotoImage, Frame
import os

def show_database_window(username):
    db_window = ctk.CTkToplevel()
    db_window.title("Administración de Base de Datos")
    db_window.geometry("720x490")
    center_window(db_window)

    # Cargar la imagen
    image = PhotoImage(file="images/robot_base.png")
    photo_label = ctk.CTkLabel(db_window, text="", image=image)
    photo_label.image = image
    photo_label.pack(pady=10)

    # Saludo y título dentro de la ventana
    greeting_label = ctk.CTkLabel(db_window, text=f"Hola, {username}, ¿cómo quieres administrar la base de datos hoy?", font=("Roboto Medium", 16))
    greeting_label.pack()

    # Crear pestañas
    tab_control = ttk.Notebook(db_window)
    tab_control.pack(fill="both", padx=10, pady=10)


    # Organizar botones en dos filas
    button_frame = ctk.CTkFrame(db_window)
    button_frame.pack(pady=10, expand=True, fill='x')

    # Definir el estilo común de los botones
    button_style = {'width': 180, 'height': 40, 'corner_radius': 10}

    # Crear botones y asignarlos a la grilla
    btn1 = ctk.CTkButton(button_frame, text="Crear Base de Datos", command=create_database, **button_style)
    btn2 = ctk.CTkButton(button_frame, text="Administrar Base de Datos", command=show_admin_window, **button_style)
    btn3 = ctk.CTkButton(button_frame, text="Administrar con NickyGPT", command=lambda: show_chat_interface(username, 1), **button_style)
    btn4 = ctk.CTkButton(button_frame, text="Eliminar Base de Datos", command=delete_database, **button_style)

    # Ubicar botones en la grilla
    btn1.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')
    btn4.grid(row=0, column=1, padx=10, pady=5, sticky='nsew')
    btn3.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
    btn2.grid(row=1, column=1, padx=10, pady=5, sticky='nsew')

    # Configurar el frame para dar el mismo espacio a las columnas
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    # Botón Volver, colocado fuera del button_frame para que se mantenga en la parte inferior
    back_button = ctk.CTkButton(db_window, text="Volver", command=db_window.destroy,
                                font=("Helvetica", 16),  # Cambia "Helvetica" por tu fuente deseada y 16 por el tamaño que quieras
                                width=200, height=50)    # Ajusta el ancho y la altura a tus necesidades
    back_button.pack(pady=10)

    db_window.mainloop()
 


def get_column_names(cursor, table_name="usuarios"):
    """
    Obtiene los nombres de las columnas de la tabla especificada, excluyendo el ID.
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall() if info[1].lower() != 'id']
    return columns


def fetch_users():
    c.execute("SELECT * FROM usuarios")
    return c.fetchall()

def insert_user(nombre, apellido):
    c.execute("INSERT INTO usuarios (Nombre, Apellido) VALUES (?, ?)", (nombre, apellido))
    conn.commit()


import requests


def change_password(username):
    # Solicita la contraseña actual usando un cuadro de diálogo
    current_password = simpledialog.askstring("Cambiar contraseña", "Introduce tu contraseña actual:", show='*')
    if not current_password:
        return
    
    # Buscar la información del usuario en la base de datos
    response = requests.get('https://abiding-heavy-outrigger.glitch.me/articles')
    if response.status_code == 200:
        users = response.json()
        user = next((user for user in users if user.get('username') == username), None)
        
        if user is None:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return
        
        # Verificar que la contraseña actual es correcta
        if user['password'] == current_password:
            new_password = simpledialog.askstring("Cambiar contraseña", "Introduce la nueva contraseña:", show='*')
            if not new_password:
                return
            
            # Actualizar la contraseña en la base de datos
            update_response = requests.put(
                f'https://abiding-heavy-outrigger.glitch.me/articles/{user["id"]}',
                json={"username": username, "password": new_password, "id": user["id"]}
            )
            if update_response.status_code == 200:
                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.")
            else:
                messagebox.showerror("Error", "Error al actualizar la contraseña.")
        else:
            messagebox.showerror("Error", "Contraseña incorrecta.")
    else:
        messagebox.showerror("Error", "Error al acceder a los datos del usuario.")



    
def delete_account(username):
    # Buscar la información del usuario en la base de datos
    response = requests.get('https://abiding-heavy-outrigger.glitch.me/articles')
    if response.status_code == 200:
        users = response.json()
        user = next((user for user in users if user.get('username') == username), None)
        
        if user is None:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return
        
        # Confirmar antes de eliminar la cuenta
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar tu cuenta?"):
            # Eliminar la cuenta del usuario de la base de datos
            delete_response = requests.delete(f'https://abiding-heavy-outrigger.glitch.me/articles/{user["id"]}')
            if delete_response.status_code == 200:
                messagebox.showinfo("Éxito", "Cuenta eliminada correctamente.")
                logout(username)
            else:
                messagebox.showerror("Error", "Error al eliminar la cuenta.")
    else:
        messagebox.showerror("Error", "Error al acceder a los datos del usuario.")


    # Cerrar la sesión
   


from tkinter import ttk

def show_admin_window():
    admin_window = Toplevel(welcome_window)
    admin_window.title("Administrar Base de Datos")

    # Crear el Treeview widget
    tree = ttk.Treeview(admin_window, columns=("ID", "Nombre", "Apellido"), show="headings")
    tree.pack(expand=YES, fill=BOTH)

    # Configurar las columnas y los encabezados
    tree.heading("ID", text="ID")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Apellido", text="Apellido")

    tree.column("ID", anchor="center", width=80)
    tree.column("Nombre", anchor="center", width=150)
    tree.column("Apellido", anchor="center", width=150)

    # Rellenar el Treeview con datos de la base de datos
    fill_treeview(tree)

    center_window(admin_window)
    admin_window.mainloop()

def fill_treeview(tree):
    # Limpiar el treeview
    for i in tree.get_children():
        tree.delete(i)

    # Consulta para obtener los datos
    c.execute("SELECT ID, Nombre, Apellido FROM usuarios")
    rows = c.fetchall()
    for row in rows:
        # Insertar los datos en el Treeview
        tree.insert("", "end", values=(row["ID"], row["Nombre"], row["Apellido"]))



def show_insert_window():
    global welcome_window

    # Obtener los nombres de las columnas desde la base de datos, excluyendo el ID
    column_names = get_column_names(c)

    insert_window = Toplevel(welcome_window)
    insert_window.title("Insertar Usuario")

    # Diccionario para almacenar las referencias de las entradas
    entry_fields = {}

    # Crear una entrada para cada columna en la base de datos, excepto el ID
    for index, column in enumerate(column_names):
        Label(insert_window, text=column).grid(row=index, column=0, padx=5, pady=5)
        entry = Entry(insert_window)
        entry.grid(row=index, column=1, padx=5, pady=5)
        entry_fields[column] = entry

    def save_user():
        # Crear un diccionario para los datos ingresados, excluyendo el ID
        data = {column: entry.get().strip() for column, entry in entry_fields.items()}

        if all(data.values()):  # Verificar que todos los campos estén completos
            try:
                columns = ', '.join(data.keys())
                placeholders = ', '.join('?' * len(data.values()))
                values = tuple(data.values())
                c.execute(f"INSERT INTO usuarios ({columns}) VALUES ({placeholders})", values)
                conn.commit()
                messagebox.showinfo("Éxito", "Usuario insertado correctamente.")
                insert_window.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al insertar en la base de datos: {e}")
        else:
            messagebox.showwarning("Error", "Por favor, complete todos los campos.")

    # Botón para guardar el usuario
    insert_button = Button(insert_window, text="Insertar", command=save_user)
    insert_button.grid(row=len(column_names) + 1, columnspan=2, padx=5, pady=5)
    center_window(insert_window)

def delete_database():
    confirm = messagebox.askyesno("Eliminar Base de Datos", "¿Está seguro que desea eliminar la base de datos?")
    if confirm:
        try:
            # Cerrar la conexión a la base de datos si está abierta
            if conn:
                conn.close()
            
            # Eliminar el archivo de la base de datos
            os.remove('usuarios.db')
            messagebox.showinfo("Eliminar Base de Datos", "La base de datos ha sido eliminada con éxito.")
            
            # Aquí puedes incluir cualquier otro código necesario después de eliminar la base de datos
            # Por ejemplo, cerrar la aplicación o actualizar la interfaz
            
        except OSError as e:
            messagebox.showerror("Error", f"Error al eliminar la base de datos: {e}")

    
def is_database_query(user_input):
    database_keywords = ['id', 'nombre', 'apellido', 'añade', 'elimina']
    return any(keyword in user_input.lower() for keyword in database_keywords)



def show_chat_interface(username, num):
    global chat_window
    chat_window = ctk.CTkToplevel()  # Utilizar CTkToplevel en lugar de Toplevel
    chat_window.title("Chatbot")
    chat_window.geometry("580x450")  # Dimensiones de la ventana
    center_window(chat_window)

    # Crear la imagen del bot
    bot_icon = PhotoImage(file='images/robot7.png')  # Asegúrate de tener la ruta correcta a tu imagen

    chat_history = scrolledtext.ScrolledText(chat_window, state='disabled', height=20, width=60)
    chat_history.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

    # Insertar mensaje de bienvenida
    welcome_message = {
        1: "Bienvenido al chat con NickyGPT, estoy preparado para administrar la base de datos.",
        2: "Bienvenido al chat con NickyGPT, soy tu asistente personal y estoy preparado para cualquier pregunta."
    }.get(num, "Bienvenido al chat con NickyGPT.")

    chat_history.config(state='normal')
    chat_history.image_create(END, image=bot_icon)
    chat_history.insert(END, ": " + welcome_message + "\n\n")
    chat_history.config(state='disabled')

    user_input_entry = ctk.CTkEntry(chat_window, placeholder_text="Escribe aquí...", width=400, height=50)
    user_input_entry.grid(row=1, column=0, padx=20, pady=5)

    def send_message():
        user_input = user_input_entry.get()
        if not user_input:
            messagebox.showwarning("Requerido", "Por favor, introduce algún texto para enviar.")
            return
        response = handle_database_command(user_input)

        chat_history.config(state='normal')
        chat_history.insert(END, f"{username}: {user_input}\n")
        chat_history.image_create(END, image=bot_icon)
        chat_history.insert(END, ": {}\n\n".format(response))
        chat_history.config(state='disabled')
        user_input_entry.delete(0, 'end')

    send_button = ctk.CTkButton(chat_window, text="Enviar", command=send_message, width=120, height=40, corner_radius=10)
    send_button.grid(row=1, column=1, padx=5, pady=5)

    chat_window.mainloop()



def ask_chatgpt_about_users():
    users = fetch_users()
    user_list = ', '.join([f"{user[1]} {user[2]}" for user in users])
    prompt = f"Tell me about the users: {user_list}"
    return get_chatgpt_response(prompt)

def logout(username):
    # Cierra cualquier ventana abierta relacionada con la sesión activa
    if welcome_window and welcome_window.winfo_exists():
        welcome_window.destroy()  # Cierra la ventana de bienvenida
    if welcome_window and welcome_window.winfo_exists():
        welcome_window.destroy()  # Cierra cualquier otra ventana adicional que podría estar abierta
    login_window.deiconify()  # Muestra nuevamente la ventana de inicio de sesión
"""
import openai
from tkinter import *
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Función para centrar la ventana en la pantalla
def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

# Función para mostrar la ventana de chat de imágenes
def show_image_chat(username):
    chat_window = Toplevel(welcome_window)
    chat_window.title("Chat de Imágenes - ImanolGPT")

    user_input_entry = Text(chat_window, height=3, width=50)
    user_input_entry.grid(row=1, column=0, padx=5, pady=5)

    send_button = Button(chat_window, text="Generar Imagen", command=lambda: generate_image(user_input_entry.get("1.0", END).strip()))
    send_button.grid(row=1, column=1, padx=5, pady=5)

    image_label = Label(chat_window)
    image_label.grid(row=0, column=0, columnspan=2, pady=10)

    center_window(chat_window)

# Función para generar la imagen usando DALL-E 3
def generate_image(description):
    openai.api_key = "tu_api_key_aquí"
    response = openai.Image.create(
        model="dall-e-3",
        prompt=description,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    image_path = download_image(image_url)
    display_image(image_path)

# Función para descargar y mostrar la imagen
def download_image(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image_path = "path/to/save/image.png"  # Define el path donde quieres guardar la imagen
    image.save(image_path)
    return image_path

def display_image(image_path):
    img = Image.open(image_path)
    img = img.resize((250, 250), Image.ANTIALIAS)  # Redimensionar si es necesario
    img = ImageTk.PhotoImage(img)
    image_label.config(image=img)
    image_label.image = img  # Guardar una referencia
#--- Bienvenida ---#"""

def select_button(button):
    global selected_button
    # Configuramos todos los botones a color no seleccionado
    for btn in [account_button, inicio_button, logout_button, exit_button, config_button]:
        btn.configure(fg_color='#0D6FC6')  # Color azul claro cuando no está seleccionado

    # Configuramos el botón seleccionado a un color diferente
    button.configure(fg_color='#1F507B')  # Color azul oscuro cuando está seleccionado
    selected_button = button


def welcome_screen(username):
    global account_button, inicio_button, logout_button, exit_button, config_button
    global title_label, photo_label, description_label, service_frame, welcome_window
    
    # Crear ventana principal con customtkinter
    welcome_window = ctk.CTkToplevel()
    welcome_window.title(f"Servicios - NickyGPT")
    welcome_window.geometry('790x400')

    # Menú vertical a la izquierda con mini-imágenes
    side_menu = ctk.CTkFrame(welcome_window, width=1)
    side_menu.pack(side=LEFT, fill="y")

    inicio_photo = PhotoImage(file="images/inicio.png")
    inicio_button = ctk.CTkButton(
    side_menu, 
    image=inicio_photo, 
    text="Inicio", 
    compound="top", 
    command=lambda: [show_home_screen(username), select_button(inicio_button)], 
    font=("Helvetica", 10), 
    width=70, 
    height=70, 
    fg_color='#0D6FC6')    
    inicio_button.image = inicio_photo
    inicio_button.pack(pady=5)


    config_photo = PhotoImage(file="images/ia.png")
    config_button = ctk.CTkButton(side_menu, image=config_photo, text="Servicios", compound="top", command=lambda: [show_config_screen(username), select_button(config_button)], font=("Helvetica", 10), width=70, height=70, fg_color='#0D6FC6')
    config_button.image = config_photo
    config_button.pack(pady=5)

    # Opciones del menú lateral con imágenes
    account_photo = PhotoImage(file="images/cuenta.png")
    account_button = ctk.CTkButton(side_menu, image=account_photo, text="Mi cuenta", compound="top", command=lambda: [show_account_info(username), select_button(account_button)], font=("Helvetica", 10), width=70, height=70, fg_color='#0D6FC6')
    account_button.image = account_photo
    account_button.pack(pady=(0,5))


    logout_photo = PhotoImage(file="images/cerrar.png")
    logout_button = ctk.CTkButton(side_menu, image=logout_photo, text="Cerrar sesión", compound="top", command=lambda: [logout(username), select_button(logout_button)], font=("Helvetica", 10), width=70, height=70, fg_color='#0D6FC6')
    logout_button.image = logout_photo
    logout_button.pack(pady=5)

    exit_photo = PhotoImage(file="images/salir.png")
    exit_button = ctk.CTkButton(side_menu, image=exit_photo, text="Salir", compound="top", command=lambda: [welcome_window.destroy(), select_button(exit_button)], font=("Helvetica", 10), width=70, height=70, fg_color='#0D6FC6')
    exit_button.image = exit_photo
    exit_button.pack(pady=5)

    # Área principal de la ventana
    main_area = ctk.CTkFrame(welcome_window)
    main_area.pack(side=LEFT, expand=True, fill=BOTH)

    # Título
    title_label = ctk.CTkLabel(main_area, text="Servicios", font=("Helvetica", 19, "bold"))
    title_label.pack(side=TOP, pady=(5, 0))

    # Cargar y mostrar la imagen en el área principal debajo del título
    image = PhotoImage(file="images/robot3.png")
    photo_label = ctk.CTkLabel(main_area, image=image, text="")
    photo_label.image = image  # Guarda la referencia de la imagen
    photo_label.pack(side=TOP, pady=1)  # Asegúrate de empaquetarlo en main_area

    # Descripción
    description_label = ctk.CTkLabel(main_area, text="Descubre la magia de la IA con NickyGPT a tu disposición", font=("Helvetica", 19, "bold"))
    description_label.pack(side=TOP, pady=(0, 5))  # 20 píxeles de padding en la parte inferior

    # Botones de servicio en el área principal
    service_frame = ctk.CTkFrame(main_area)
    service_frame.pack(expand=True, fill=BOTH, padx=20)

    # Botones para cada servicio
    database_button = ctk.CTkButton(service_frame, text="Base de datos", command=lambda: show_database_window(username), fg_color='#126395', font=("Helvetica", 12))
    database_button.pack(side=LEFT,  fill=BOTH, padx=10, pady=10)

    chat_button = ctk.CTkButton(service_frame, text="ImanolGPT(soon)", command=lambda: pronto(username), fg_color='#126395', font=("Helvetica", 12))
    chat_button.pack(side=LEFT,  fill=BOTH, padx=10, pady=10)

    other_service_button = ctk.CTkButton(service_frame, text="GPT4(soon)", command=lambda: pronto(username), fg_color='#126395', font=("Helvetica", 12))
    other_service_button.pack(side=LEFT, fill=BOTH, padx=10, pady=10)

    return_button = ctk.CTkButton(service_frame, text="RubGPT(soon)", command=lambda: pronto(username), fg_color='#126395', font=("Helvetica", 12))
    return_button.pack(side=LEFT, fill=BOTH, padx=10, pady=10)

    select_button(config_button)

    center_window(welcome_window)

from tkinter import *
from tkinter import filedialog

from tkinter import *

def show_config_screen(username):
    global title_label, photo_label, description_label, service_frame, selected_button

    # Actualizar título
    title_label.configure(text="Servicios")
    welcome_window.geometry('790x400')

    # Restablecer la imagen original
    home_image = PhotoImage(file="images/robot3.png")  # Asegúrate de usar la ruta correcta a tu imagen
    photo_label.configure(image=home_image)
    photo_label.image = home_image  # Mantener una referencia

    # Restablecer descripción
    description_label.configure(text="Descubre la magia de la IA con NickyGPT a tu disposición")

    # Limpiar el frame de servicios y recrear los botones de servicios
    for widget in service_frame.winfo_children():
        widget.destroy()

    # Botones para cada servicio
    database_button = ctk.CTkButton(service_frame, text="Base de datos", command=lambda: show_database_window(username), fg_color='#126395', font=("Helvetica", 12))
    database_button.pack(side=LEFT,  fill=BOTH, padx=10, pady=10)

    chat_button = ctk.CTkButton(service_frame, text="ImanolGPT(soon)",  command=lambda: pronto(username), fg_color='#126395', font=("Helvetica", 12))
    chat_button.pack(side=LEFT,  fill=BOTH, padx=10, pady=10)

    other_service_button = ctk.CTkButton(service_frame, text="GPT4(soon)",  command=lambda: pronto(username), fg_color='#126395', font=("Helvetica", 12))  # Asegúrate de definir la función `show_other_service`
    other_service_button.pack(side=LEFT,  fill=BOTH, padx=10, pady=10)

    return_button = ctk.CTkButton(service_frame, text="RubGPT(soon)", command=lambda: pronto(username), fg_color='#126395', font=("Helvetica", 12))
    return_button.pack(side=LEFT,  fill=BOTH, padx=10, pady=10)

    # Configura el botón seleccionado a "Inicio"
    select_button(config_button)
def pronto(username):
    messagebox.showwarning("ERROR")

def show_account_info(username):
    global title_label, photo_label, description_label, service_frame
    
    # Actualizar título
    welcome_window.geometry('560x450')
    title_label.configure(text="Mi cuenta")

    # Cambiar la imagen
    new_account_image = PhotoImage(file="images/robot4.png")  # Asegúrate de cambiar la ruta a la imagen que deseas mostrar
    photo_label.configure(image=new_account_image)
    photo_label.image = new_account_image  # Mantener una referencia

    # Actualizar descripción
    description_label.configure(text="Aquí puedes administrar los detalles de tu cuenta")

    # Limpiar el frame de servicios y agregar nuevos elementos
    for widget in service_frame.winfo_children():
        widget.destroy()

    # Agregar elementos de cuenta como nombre de usuario y contraseña
    username_label = ctk.CTkLabel(service_frame, text=f"Usuario: {username}", font=("Helvetica", 12))
    username_label.pack(side=TOP, fill=X, padx=10, pady=10)

    password_label = ctk.CTkLabel(service_frame, text="Contraseña: ********", font=("Helvetica", 12))
    password_label.pack(side=TOP, fill=X, padx=10, pady=10)

    # Agregar botones para cambiar contraseña y eliminar cuenta
    change_password_button = ctk.CTkButton(service_frame, command=lambda: change_password(username), text="Cambiar contraseña", fg_color='#126395', font=("Helvetica", 12))
    change_password_button.pack(side=TOP, fill=X, padx=10, pady=10)

    delete_account_button = ctk.CTkButton(service_frame, command=lambda: delete_account(username), text="Eliminar cuenta", fg_color='#126395', font=("Helvetica", 12))
    delete_account_button.pack(side=TOP, fill=X, padx=10, pady=10)

    # Configura el botón seleccionado a "Mi cuenta"
    select_button(account_button)


def show_home_screen(username):
    global title_label, photo_label, description_label, service_frame, welcome_window
    for widget in service_frame.winfo_children():
        widget.destroy()

    def update_info_text(text):
        # Primero, borramos cualquier texto existente o widgets en el frame
        for widget in info_text_frame.winfo_children():
            widget.destroy()
        # Luego, creamos una nueva etiqueta con el texto actualizado
        info_text_label = ctk.CTkLabel(info_text_frame, text=text,font=("Helvetica", 16),  wraplength=400, justify=LEFT)
        info_text_label.pack(padx=10, pady=10)

    def show_support_form():
        # Borramos cualquier contenido existente en el frame
        for widget in info_text_frame.winfo_children():
            widget.destroy()
        # Creamos el formulario de soporte
        name_label = ctk.CTkLabel(info_text_frame, text="Correo electronico:")
        name_label.pack(side=TOP,padx=120, anchor='w')
        name_entry = ctk.CTkEntry(info_text_frame)
        name_entry.pack(side=TOP, fill=X,padx=120 ,pady=(0, 10))

        comment_label = ctk.CTkLabel(info_text_frame, text="Comentario:")
        comment_label.pack(side=TOP, anchor='w',padx=120)
        comment_entry = ctk.CTkEntry(info_text_frame)
        comment_entry.pack(side=TOP, fill=X, pady=(0, 10),padx=120)

        send_button = ctk.CTkButton(info_text_frame, text="Enviar", command=lambda: send_support_form(name_entry.get(), comment_entry.get()))
        send_button.pack(pady=10)

        def send_support_form(name, comment):
            print(f"Nombre: {name}\nComentario: {comment}")
            update_info_text(f"Gracias {username} por contribuir con NickyGPT. En breve recibira su respuesta")

            # Aquí se debería incluir la lógica para manejar el envío del formulario, como enviar un email, guardar en una base de datos, etc.

    # Área principal de la ventana
    title_label.configure(text="Inicio")
    welcome_window.geometry('790x450')  # Ajustamos el tamaño de la ventana para el nuevo contenido

    # Cargar y mostrar la imagen en el área principal debajo del título
    image_path = "images/robot5.png"
    home_image = PhotoImage(file=image_path)
    photo_label.configure(image=home_image)
    photo_label.image = home_image  # Mantener una referencia

    # Restablecer descripción
    description_label.configure(text="Bienvenido a NickyGPT - Tu asistente de IA")

    # Botones para información adicional
    info_frame = ctk.CTkFrame(service_frame)
    info_frame.pack(side=LEFT, fill=BOTH, expand=True)

    info_text_frame = ctk.CTkFrame(service_frame)
    info_text_frame.pack(side=RIGHT, fill=BOTH, expand=True)

    # Botón "¿Qué es este programa?"
    program_button = ctk.CTkButton(
        info_frame, width=100,
        text="¿Qué es este programa?", 
        command=lambda: update_info_text("NickyGPT es una innovadora aplicación diseñada para optimizar la gestión de bases de datos utilizando técnicas avanzadas de inteligencia artificial. Facilita la integración, consulta y análisis de grandes volúmenes de datos."))
    program_button.pack(fill=X, padx=10, pady=10)

    # Botón "Sobre mí"
    about_button = ctk.CTkButton(
        info_frame, 
        text="Sobre mí", 
        command=lambda: update_info_text("Hola, soy Alex, un apasionado programador con experiencia en desarrollo de software y sistemas de bases de datos. Visita mi GitHub para ver mis proyectos y contribuciones: https://github.com/alexsegui10"))
    about_button.pack(fill=X, padx=10, pady=10)

    # Botón "Soporte"
    support_button = ctk.CTkButton(
        info_frame, 
        text="Soporte", 
        command=show_support_form)
    support_button.pack(fill=X, padx=10, pady=10)

    # Iniciamos la pantalla con la información de "¿Qué es este programa?"
    update_info_text("NickyGPT es una innovadora aplicación diseñada para optimizar la gestión de bases de datos utilizando técnicas avanzadas de inteligencia artificial. Facilita la integración, consulta y análisis de grandes volúmenes de datos.")

    # Configurar el botón seleccionado a "Inicio"
    select_button(inicio_button)



#--- Inicio de sesiom ---#

from tkinter import *
from tkinter import messagebox, simpledialog, PhotoImage

def initialize_login():
    global login_window
    login_window = ctk.CTk()  # Cambiamos Tk() por CTk()
    login_window.title("NickyGPT - Acceso")
    login_window.geometry('1000x660')  # Define un tamaño más grande para la ventana

    # Cargar y mostrar un logo
    logo = PhotoImage(file='images/robot.png')  # Asegúrate de usar el path correcto al archivo de logo
    logo_label = ctk.CTkLabel(login_window, image=logo, text="")
    logo_label.image = logo  # Guardar referencia
    logo_label.pack(pady=10)

    # Título del programa
    title_label = ctk.CTkLabel(login_window, text="Bienvenido a NickyGPT", font=("Helvetica", 16, "bold"),)
    title_label.pack()

    container = ctk.CTkFrame(login_window)
    container.pack(expand=True, fill="both", padx=20, pady=20)

    login_button = ctk.CTkButton(container, text="Inicio de sesión", command=login, fg_color='#00a2ed', text_color='white', font=("Helvetica", 12))
    login_button.pack(side="left", expand=True, fill="both", padx=10, pady=10)

    register_button = ctk.CTkButton(container, text="Registro", command=register, fg_color='#00a2ed', text_color='white', font=("Helvetica", 12))
    register_button.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    center_window(login_window)  # Asegúrate de definir esta función, si no lo has hecho ya

def center_window(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f'{width}x{height}+{x}+{y}')

def login():
    global username  # Declara username como global si aún no lo has hecho
    username = simpledialog.askstring("Inicio de sesión", "Ingrese su nombre de usuario", parent=login_window)
    if not username:
        messagebox.showwarning("Inicio de sesión fallido", "Debe ingresar un nombre de usuario.")
        return
    password = simpledialog.askstring("Inicio de sesión", "Ingrese su contraseña", show='*', parent=login_window)
    if not password:
        messagebox.showwarning("Inicio de sesión fallido", "Debe ingresar una contraseña.")
        return

    if check_login(username, password):
        messagebox.showinfo("Inicio de sesión exitoso", "Ha iniciado sesión correctamente.")
        login_window.withdraw()  # Oculta la ventana de inicio de sesión
        welcome_screen(username)  # Muestra la ventana de bienvenida
    else:
        messagebox.showwarning("Inicio de sesión fallido", "Usuario o contraseña incorrectos.")


def register():
    username = simpledialog.askstring("Registro", "Elija un nombre de usuario", parent=login_window)
    if username is None or username.strip() == "":
        return
    password = simpledialog.askstring("Registro", "Elija una contraseña", parent=login_window)
    if password is None or password.strip() == "":
        messagebox.showwarning("Registro fallido", "El nombre de usuario y la contraseña no pueden estar vacíos.")
        return
    if register_user(username, password):
        messagebox.showinfo("Registro exitoso", "Se ha registrado correctamente.")
    else:
        messagebox.showwarning("Registro fallido", "No se pudo completar el registro.")

# Asegúrate de tener las funciones check_login, welcome_screen y register_user correctamente implementadas.


if __name__ == "__main__":
    initialize_login()
    login_window.mainloop()
