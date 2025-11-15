from tkinter import *
from tkinter import ttk
import sqlite3 as sql
from tkinter import filedialog
from tkinter import messagebox
import os
import re

databasename = None

def createBase():
  db = filedialog.asksaveasfilename(
    initialdir="C:/",
    title="Selecciona la ruta de la base de datos",
    defaultextension=".db",
    filetypes=[("Base de datos", "*.db")]
  )
  if db:
      databasename = db
      conn = sql.connect(databasename)
      conn.close()
      tablesOfDatabase()
      frameHome.pack(side=TOP)

def openBase():
  global databasename
  db = filedialog.askopenfilename(initialdir="C:/", title="Selecciona la ruta de la base de datos", filetypes=[("Base de datos", (".db", ".sql", "*.sqlite"))])
  try:
    if db is None:
      pass
    else:
      databasename = db
      tablesOfDatabase()
      frameHome.pack(side=TOP)
  except Exception as e:
    cmdText.delete(0.0, END)
    cmdText.insert(0.0, f'Ocurrio un error. \nError: {str(e)}.')

def closeBase():
  global databasename
  try:
    db = None
    databasename = db
    reload()
    app.update()
  except Exception as e:
    cmdText.delete(0.0, END)
    cmdText.insert(0.0, f'Ocurrio un error. \nError: {str(e)}.')

def fExecuteSql():
  try:
    frameHome.pack_forget()
    frameExecute.pack()
    frameCreateTable.pack_forget()
    frameTableSelect.pack_forget()
    frame_tabla.pack_forget()
    frameTablaVista.pack_forget()
  except Exception as e:
    cmdText.delete(0.0, END)
    cmdText.insert(0.0, f'Ocurrio un error. \nError: {str(e)}.')

def executeSql():
    global databasename
    query = entrySql.get("1.0", END).strip()
    if databasename is None:
        cmdText.delete(0.0, END)
        cmdText.insert(0.0, 'ERROR: No hay una base de datos abierta.')
        return

    try:
        conn = sql.connect(databasename)
        cursor = conn.cursor()
        cursor.execute(query)

        for widget in frame_tabla.winfo_children():
            widget.destroy()

        if query.strip().lower().startswith("select"):
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()

            # Asegurarse de que frame_tabla esté visible
            frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

            tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", style="Treeview")
            tabla.pack(fill="both", expand=True)

            # Scrollbars
            scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
            scroll_y.pack(side="right", fill="y")
            scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tabla.xview)
            scroll_x.pack(side="bottom", fill="x")
            tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

            for col in columnas:
                tabla.heading(col, text=col)
                tabla.column(col, width=100, anchor="center")

            for fila in filas:
                tabla.insert("", "end", values=fila)
            cmdText.delete(0.0, END)
            cmdText.insert(0.0, f'{len(filas)} filas y {len(columnas)} columnas ejecutadas sin errores. \n{entrySql.get(0.0, END)}.')
        elif query.strip().lower().startswith("delete from"):
            if "where" in query.strip().lower():
              conn.commit()
              cmdText.delete(0.0, END)
              cmdText.insert(0.0, f'La consulta fue ejecutada exitosamente. \n{entrySql.get(0.0, END)}')
            else:
              okcancel = messagebox.askokcancel("SQL", "Estas ejecutando una consulta que borrara todos los datos de la tabla. \n¿Estás seguro de que quieres continuar?")
              if okcancel:
                  conn.commit()
                  cursor = conn.cursor()
                  cursor.execute(query)
                  cmdText.delete(0.0, END)
                  cmdText.insert(0.0, f'La consulta fue ejecutada exitosamente. \n{entrySql.get(0.0, END)}.')
              else:
                  cmdText.delete(0.0, END)
        else:
            conn.commit()
            cmdText.delete(0.0, END)
            cmdText.insert(0.0, f'La consulta fue ejecutada exitosamente. \n{entrySql.get(0.0, END)}')

        conn.close()
    except Exception as e:
        cmdText.delete(0.0, END)
        cmdText.insert(0.0, f'Ocurrio un error. \nError: {str(e)}.')

def fHome():
  try:
    frameHome.pack(side=TOP)
    frameExecute.pack_forget()
    frameTableSelect.pack_forget()
    frame_tabla.pack_forget()
    frameTablaVista.pack_forget()
    frameCreateTable.pack_forget()
  except Exception as e:
    cmdText.delete(0.0, END)
    cmdText.insert(0.0, f'Ocurrio un error. \nError: {str(e)}.')

def showTable(t):
    frame_tabla.pack_forget()
    frameCreateTable.pack_forget()
    frameExecute.pack_forget()
    frameTableSelect.pack_forget()
    frameHome.pack_forget()
    global databasename
    if databasename is None:
        cmdText.delete(0.0, END)
        cmdText.insert(0.0, f'ERROR: No hay una base de datos abierta.')
        return

    for widget in frameTablaVista.winfo_children():
        widget.destroy()

    frameTablaVista.pack(fill="both", expand=True)

    Button(
        frameTablaVista, text="⬅ Volver",
        bg="#002341", fg="white", font=("Arial", 10, "bold"),
        relief="raised", bd=3,
        command=fHome,
        activebackground="#002341", activeforeground="#ffffff"
    ).pack(pady=10)

    try:
        conn = sql.connect(databasename)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {t}")
        columnas = [desc[0] for desc in cursor.description]
        filas = cursor.fetchall()
        conn.close()

        contenedor_tabla = Frame(frameTablaVista)
        contenedor_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        scroll_y = ttk.Scrollbar(contenedor_tabla, orient="vertical")
        scroll_y.pack(side="right", fill="y")
        scroll_x = ttk.Scrollbar(contenedor_tabla, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")

        tabla = ttk.Treeview(contenedor_tabla, columns=columnas, show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set, style="Treeview")
        tabla.pack(fill="both", expand=True)
        scroll_y.config(command=tabla.yview)
        scroll_x.config(command=tabla.xview)

        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, anchor="center", width=120)

        for fila in filas:
            tabla.insert("", "end", values=fila)

    except Exception as e:
        cmdText.delete(0.0, END)
        cmdText.insert(0.0, f'Error al mostrar la tabla. \nERROR: {str(e)}.')


def tablesOfDatabase():
    global databasename

    for widget in frameHome.winfo_children():
        widget.destroy()

    if databasename is None:
        cmdText.delete(0.0, END)
        cmdText.insert(0.0, f'ERROR: No hay una base de datos abierta.')
        return []

    try:
        conn = sql.connect(databasename)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        conn.close()
        Label(frameHome, text="Tablas \n", fg="#ffffff", font=('sans-serif', 16), bg="#011627").pack(pady=5)
        for tabla in tablas:
          Button(frameHome, text=tabla[0], command=lambda tabla=tabla[0]: showTable(tabla), bg="#011627", fg="white", font=("Arial", 10, "bold"), relief="raised", bd=0, activebackground="#011627", activeforeground="#ffffff").pack(pady=5)
    except Exception as e:
        cmdText.delete(0.0, END)
        cmdText.insert(0.0, f'Ocurrio un error. \nERROR: {str(e)}.')

def fCreateTable():
  try:
    frameCreateTable.pack()
    frameExecute.pack_forget()
    frameTableSelect.pack_forget()
    frame_tabla.pack_forget()
    frameTablaVista.pack_forget()
    frameHome.pack_forget()
  except Exception as e:
    cmdText.delete(0.0, END)
    cmdText.insert(0.0, f'Ocurrio un error. \nError: {str(e)}.')


def appAddCol():
    top = Toplevel(app)
    top.configure(bg="#011627")
    top.title("Agregar Columna")
    top.geometry("500x200")

    Label(top, text="Nombre de la columna", bg="#011627", fg="#ffffff").grid(row=0, column=0)
    entryNameCol = Entry(top, width=20, bg="#011A2E", fg="#ffffff", insertbackground="#ffffff")
    entryNameCol.grid(row=1, column=0)

    Label(top, text="Tipo de Dato", bg="#011627", fg="#ffffff").grid(row=2, column=0)
    entryTypeCol = Entry(top, width=20, bg="#011A2E", fg="#ffffff", insertbackground="#ffffff")
    entryTypeCol.grid(row=3, column=0)

    autoIncrement = BooleanVar()
    Label(top, text="AI", bg="#011627", fg="#ffffff").grid(row=4, column=0)
    checkAutoIncrement = Checkbutton(top, variable=autoIncrement, onvalue=True, offvalue=False, bg="#011A2E", fg="#ffffff", selectcolor="#011A2E")
    checkAutoIncrement.grid(row=5, column=0)

    Button(top, text="Agregar", command=lambda: addCol(entryNameCol.get(), entryTypeCol.get(), autoIncrement.get()), bg="#011A2E", fg="#ffffff", activebackground="#002341").grid(row=6, column=0)
    try:
      pass
    except Exception as e:
      cmdText.delete(0.0, END)
      cmdText.insert(0.0, f'Ocurrio un error. \nError: {str(e)}.')

def addCol(nameCol, typeCol, autoIncrement):
  try:
    global databasename
    tableName = entryNameTable.get()
    if nameCol and typeCol:
        conn = sql.connect(databasename)
        cursor = conn.cursor()

        if autoIncrement:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {tableName} (ID INTEGER PRIMARY KEY AUTOINCREMENT, {nameCol} {typeCol})")
        else:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {tableName} ({nameCol} {typeCol})")

        conn.commit()
        conn.close()
        cmdText.delete(0.0, END)
        cmdText.insert(0.0, f'Columna agregada correctamente.')
    else:
        cmdText.delete(0.0, END)
        cmdText.insert(0.0, f'Porfavor complete todos los campos.')
        fHome()
  except Exception as e:
    cmdText.delete(0.0, END)
    cmdText.insert(0.0, f'Ocurrio un error. \nError: {str(e)}.')

def reload():
    try:
        result = tablesOfDatabase()
        cmdText.delete(0.0, END)
        cmdText.insert(0.0, result)
    except Exception as e:
        cmdText.delete(0.0, END)
        cmdText.insert(0.0, f'Ha ocurrido un error.\nError: {str(e)}.')

def closeApp():
  respuesta = messagebox.askyesno("Salir", "¿Estás seguro que deseas salir?")
  if respuesta:
    app.destroy()

def infoDatabase():
  conn = sql.connect(databasename)
  cursor = conn.cursor()
  if databasename is None:
    cmdText.delete(0.0, END)
    cmdText.insert(0.0, f'ERROR: No hay una base de datos abierta.')
    return
  else:
    try:
      cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
      tablas = cursor.fetchall()
      nametabla = ""
      for tabla in tablas:
        cursor.execute(f"PRAGMA table_info({tabla[0]})")
        columnas = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
        cantidad = cursor.fetchone()[0]
        nametabla += f'(Tabla "{tabla[0]}" → Columnas: {len(columnas)}, Filas: {cantidad}), '
      cmdText.insert(0.0, f'''Datos de la Base de Datos
------------------------------
Cantidad de Tablas: {len(tablas)}
Info de las Tablas: {nametabla}''')
    except Exception as e:
      cmdText.delete(0.0, END)
      cmdText.insert(0.0, f'Ocurrio un error. \nERROR: {str(e)}.')

def cmdCommand(event=None):
    if event.keysym != "Return":
        return

    global databasename

    cmd = cmdText.get("1.0", "end").strip()
    cmdText.delete("1.0", "end")
    cmd_lower = cmd.lower()

    if not cmd:
        return

    if cmd_lower in ("help", "?"):
        help_text = """\
📘 Comandos disponibles:

  help                     → Muestra esta ayuda
  clear                    → Limpia la consola
  info                     → Información de la base actual
  show tables              → Lista todas las tablas
  viewtable(nombre)        → Muestra una tabla específica
  delete database          → Borra la base de datos abierta
  reload                   → Recarga la interfaz
  sql [consulta]           → Ejecuta SQL directamente
  search [dato]            → Busca datos en la base
  exit                     → Cierra la aplicación
"""
        cmdText.insert("1.0", help_text)
        return

    elif cmd_lower == "clear":
        cmdText.delete("1.0", "end")
        return

    elif cmd_lower == "exit":
        closeApp()
        return

    elif cmd_lower == "info":
        if databasename is None:
            cmdText.insert("1.0", "❌ No hay una base de datos abierta.")
            return
        try:
            conn = sql.connect(databasename)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = cursor.fetchall()

            info_text = f"📂 Base de datos: {os.path.basename(databasename)}\n"
            info_text += f"🗃 Tablas encontradas: {len(tablas)}\n"

            for t in tablas:
                cursor.execute(f"PRAGMA table_info({t[0]})")
                columnas = cursor.fetchall()
                cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
                filas = cursor.fetchone()[0]
                info_text += f"   - {t[0]} → {len(columnas)} columnas, {filas} filas\n"

            conn.close()
            cmdText.insert("1.0", info_text)
        except Exception as e:
            cmdText.insert("1.0", f"⚠ Error obteniendo info: {e}")
        return

    elif cmd_lower == "show tables":
        if databasename is None:
            cmdText.insert("1.0", "❌ No hay una base de datos abierta.")
            return
        try:
            conn = sql.connect(databasename)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = [t[0] for t in cursor.fetchall()]
            conn.close()
            if tablas:
                cmdText.insert("1.0", "📋 Tablas disponibles:\n- " + "\n- ".join(tablas))
            else:
                cmdText.insert("1.0", "📂 No hay tablas creadas aún.")
        except Exception as e:
            cmdText.insert("1.0", f"⚠ Error mostrando tablas: {e}")
        return

    elif cmd_lower.startswith("viewtable("):
        match = re.search(r"viewtable\((\w+)\)", cmd_lower)
        if not match:
            cmdText.insert("1.0", "⚠ Uso correcto: viewtable(nombre_tabla)")
            return
        tabla = match.group(1)
        showTable(tabla)
        cmdText.insert("1.0", f"👁 Mostrando tabla: {tabla}")
        return

    elif cmd_lower == "delete database":
        if databasename is None:
            cmdText.insert("1.0", "❌ No hay base de datos para eliminar.")
            return
        confirm = messagebox.askokcancel("Eliminar Base", f"¿Borrar '{databasename}' permanentemente?")
        if confirm:
            try:
                os.remove(databasename)
                databasename = None
                cmdText.insert("1.0", "✅ Base de datos eliminada exitosamente.")
            except Exception as e:
                cmdText.insert("1.0", f"⚠ Error al eliminar: {e}")
        else:
            cmdText.insert("1.0", "❎ Cancelado.")
        return

    elif cmd_lower == "reload":
        reload()
        cmdText.insert("1.0", "🔄 Base de datos recargada correctamente.")
        return

    elif cmd_lower.startswith("sql "):
        query = cmd[4:].strip()
        if not query:
            cmdText.insert("1.0", "⚠ Debes escribir una consulta SQL. Ejemplo:\nsql SELECT * FROM usuarios;")
            return
        entrySql.delete("1.0", "end")
        entrySql.insert("1.0", query)
        executeSql()
        return

    elif cmd_lower.startswith("search "):
        query = cmd[7:].strip()
        if not query:
            cmdText.insert("1.0", "⚠ Debes escribir un dato para poder busacarlo.")
            return
        else:
            searchDate(query)
        return

    else:
        if databasename is None:
            cmdText.insert("1.0", "❌ No hay base de datos abierta.")
            return
        try:
            entrySql.delete("1.0", "end")
            entrySql.insert("1.0", cmd)
            executeSql()
            cmdText.insert("1.0", f"✅ Comando SQL ejecutado correctamente:\n{cmd}")
        except Exception as e:
            cmdText.insert("1.0", f"⚠ Error al ejecutar SQL: {e}")

def searchDate(d):
    conn = sql.connect(databasename)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
    tablas = cursor.fetchall()

    search_result = ""

    for tabla in tablas:
        tabla_nombre = tabla[0]
        cursor.execute(f"PRAGMA table_info({tabla_nombre})")
        columnas_info = cursor.fetchall()
        columnas = [col[1] for col in columnas_info]

        for col in columnas:
            try:
                cursor.execute(f"SELECT rowid, * FROM {tabla_nombre} WHERE {col} = ?", (d,))
                datos = cursor.fetchall()
                for dato in datos:
                    fila = dato[0]  # rowid está en la primera posición
                    search_result += f"Se ha encontrado el dato {d} en la tabla '{tabla_nombre}', columna '{col}', fila {fila}.\n"
            except Exception as e:
                print(f"Error al consultar columna {col} en tabla {tabla_nombre}: {e}")
    if search_result:
        cmdText.delete(0.0, END)
        cmdText.insert(0.0, search_result)
    else:
      cmdText.delete(0.0, END)
      cmdText.insert(0.0, f"No se ha encontrado el dato {d} en ninguna tabla.")

def appSearch():
  top = Toplevel(app)
  top.geometry("500x200")
  top.title("Buscar Datos")
  top.configure(bg="#011627")
  Label(top, text="Buscar Datos", bg="#011627", fg="#ffffff").grid(row=0, column=0)
  dato = Entry(top, width=20, bg="#011A2E", fg="#ffffff", insertbackground="#ffffff")
  dato.grid(row=1, column=0)
  Button(top, text="Buscar", command=lambda: searchDate(dato.get()), bg="#011A2E", fg="#ffffff", activebackground="#002341").grid(row=2, column=0)

def helpToUser():
    top = Toplevel(app)
    top.geometry("600x500")
    top.title("Ayuda")
    top.configure(bg="#011627")

    texto_ayuda = """👋 ¡Hola! Gracias por usar esta aplicación.
Esta es la versión Pre-Alfa del programa. Aunque aún está en desarrollo,
ya incluye funciones útiles para gestionar bases de datos SQLite.
Espero que lo disfrutes tanto como yo disfruté programarlo.

📘 Guía de uso:
------------------------------
🔹 Menú File:
- New Database: Crea una nueva base de datos SQLite desde cero.
- Open Database: Abre una base de datos existente (.db, .sql, .sqlite).

🔹 Menú Functions:
- Search Data: Busca un valor específico en toda la base de datos.
  Escanea todas las tablas y columnas, y muestra dónde se encuentra
  el dato (tabla, columna y fila) en la terminal.

🔹 Menú View:
- Home: Muestra todas las tablas disponibles en la base de datos.
  Puedes hacer clic en cualquiera para visualizarla.
- Create Table: Crea una nueva tabla con columnas personalizadas.
  Puedes definir el tipo de dato y activar el modo AutoIncrement.
- Execute SQL: Ejecuta cualquier consulta SQL directamente.
  Los resultados se muestran en una tabla visual con scroll.
- Info de la Base: Muestra un resumen completo de la base de datos:
  cantidad de tablas, columnas, filas y más.

🔹 Terminal:
- ¿El Programa Viene con una terminal?
  SIIIIIIII!!!!!!
- ¿Cómo Utilizo la Terminal?
  Simplemente da un click sobre ella y escribe help, te ofrecerá
  la lista de comandos completos.
  Ej: search [dato], uso: search Ronald ⇽ Esto buscará en cada rincón
  de la base de datos el dato que introdujiste, y así con muchos
  más comandos.

👨‍🎓 Información Sobre el Desarrollador:
Hola, soy Ronald, un niño de 13 años al que le apasiona la programación.
Este programa lo hice yo solo desde cero. Llevo un año completo estudiando
programación. Este no es el mejor navegador que existe para SQLite, pero
lo hice yo solo y ha sido el más grande que he hecho hasta ahora.
Planeo seguir desarrollándolo. Esto solo es una versión Pre-Alfa, ¡espero
que la disfrutes!

🎨 Interfaz:
La app tiene un diseño oscuro moderno, ideal para trabajar cómodamente.
Usa botones claros, menús intuitivos y una terminal integrada para comandos.

⚠ Esta es una versión Pre-Alfa. Algunas funciones están en desarrollo.
¡Gracias por probarla y ser parte de su evolución!
"""

    # Contenedor para texto y scroll
    frame_texto = Frame(top, bg="#011627")
    frame_texto.pack(fill="both", expand=True, padx=10, pady=10)

    scroll_y = Scrollbar(frame_texto, orient="vertical")
    scroll_y.pack(side="right", fill="y")

    scroll_x = Scrollbar(frame_texto, orient="horizontal")
    scroll_x.pack(side="bottom", fill="x")

    texto_widget = Text(frame_texto, wrap="none", bg="#011627", fg="#ffffff",
                        font=("Arial", 10), yscrollcommand=scroll_y.set,
                        xscrollcommand=scroll_x.set)
    texto_widget.insert("1.0", texto_ayuda)
    texto_widget.config(state="disabled")  # Solo lectura
    texto_widget.pack(fill="both", expand=True)

    scroll_y.config(command=texto_widget.yview)
    scroll_x.config(command=texto_widget.xview)

app = Tk()
app.title('SQLite Browser - Pre-Alfa')

style = ttk.Style(app)
style.theme_use("default")

style.configure("Treeview",
    background="#011322",
    foreground="white",
    fieldbackground="#011322",
    rowheight=25,
    font=("Arial", 10)
)

style.configure("Treeview.Heading",
    background="#000E1A",
    foreground="white",
    font=("Arial", 10, "bold")
)

style.map("Treeview", background=[("selected", "#0078D7")])

app.configure(bg="#011627")
app.geometry("1100x600+40+40")
app.protocol("WM_DELETE_WINDOW", closeApp)


menu = Menu(app, background="#01213B", foreground="#ffffff")
app.config(menu=menu)

menu_base = Menu(menu, tearoff=0, background="#01213B", foreground="#ffffff")
menu.add_cascade(label='File', menu=menu_base)
menu_base.add_command(label='New Database', command=createBase)
menu_base.add_command(label='Open Database', command=openBase)

menu_functions = Menu(menu, tearoff=0, background="#01213B", foreground="#ffffff")
menu.add_cascade(label='Functions', menu=menu_functions)
menu_functions.add_command(label='Search Data', command=appSearch)

menu_view = Menu(menu, tearoff=0, background="#01213B", foreground="#ffffff")
menu.add_cascade(label='View', menu=menu_view)
menu_view.add_command(label='Home', command=fHome)
menu_view.add_command(label='Create Table', command=fCreateTable)
menu_view.add_command(label='Execute SQL', command=fExecuteSql)
menu_view.add_command(label='Info de la Base', command=infoDatabase)

menu_help = Menu(menu, tearoff=0, background="#01213B", foreground="#ffffff")
menu.add_cascade(label='Help', menu=menu_help)
menu_help.add_command(label='Help User', command=helpToUser)

fBtn = Frame(app, bg="#01213B", width=800)
Button(fBtn, text='➕New Database', command=createBase, bd=0, bg='#01213B', font=12, pady=6, padx=80, activebackground="#01213B", fg="#0A0A0A").grid(row=0, column=0)
Button(fBtn, text='📂Open Database', command=openBase, bd=0, bg='#01213B', font=12, pady=6, padx=80, activebackground="#01213B", fg="#0A0A0A").grid(row=0, column=1)
Button(fBtn, text='✖Close Database', command=closeBase, bd=0, bg='#01213B', font=12, pady=6, padx=80, activebackground="#01213B", fg="#0A0A0A").grid(row=0, column=2)
Button(fBtn, text='↺ Reload', command=closeBase, bd=0, bg='#01213B', font=12, pady=6, padx=80, activebackground="#01213B", fg="#0A0A0A").grid(row=0, column=3)
fBtn.pack()


frameExecute = Frame(app, bg="#011322")
entrySql = Text(frameExecute, height=5, width=80, font=("Consolas", 12), bg="#011322", fg="#ffffff", insertbackground="#ffffff")
entrySql.pack(pady=5)

Button(frameExecute, text="Ejecutar", bg="#002341", fg="white", font=("Arial", 10, "bold"), relief="raised", bd=3, command=executeSql, activebackground="#001A31", activeforeground="white").pack(pady=5)

frame_tabla = Frame(frameExecute, bg="#011322")
frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)


frameHome = Frame(app, bg="#011627")

frameTableSelect = Frame(frameHome)
frameTablaVista = Frame(app, bg="#011322")


frameCreateTable = Frame(app, bg="#011627")
Label(frameCreateTable, text="Nombre de la tabla", bg="#011627", fg="#ffffff").grid(row=0, column=0)
entryNameTable = Entry(frameCreateTable, width=20, bg="#011A2E", fg="#ffffff", insertbackground="#ffffff")
entryNameTable.grid(row=1, column=0)
Button(frameCreateTable, text="Agregar Columna", command=appAddCol, bg="#002341", fg="#ffffff").grid(row=2, column=0)


cmd = Frame(app, bg="#001F38")
cmd.pack(side=BOTTOM)
Label(cmd, text='Terminal', bg='#001F38', font=('', 12)).pack()
cmdText = Text(cmd, bg="#001F38", fg="#ffffff", insertbackground="#ffffff", font=('consolas', 10, 'bold'), height=9, width=800, bd=0)
cmdText.pack(fill="both", expand=True)
cmdText.bind("<Key>", cmdCommand)
scroll_y = ttk.Scrollbar(cmd, orient="vertical")
scroll_y.pack(side="right", fill="y")
scroll_x = ttk.Scrollbar(cmd, orient="horizontal")
scroll_x.pack(side="bottom", fill="x")
scroll_y.config(command=cmdText.yview)
scroll_x.config(command=cmdText.xview)

app.mainloop()
