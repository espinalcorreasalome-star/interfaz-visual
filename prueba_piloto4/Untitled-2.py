
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from datetime import datetime


DB_NAME = "usuarios.db"

# ── PALETA NORDSIGN - MISMA ESTÉTICA DE LA INTERFAZ VISUAL ──
COLOR_PRIMARIO = "#1B3A68"
COLOR_PRIMARIO_2 = "#234A7D"
COLOR_SECUNDARIO = "#3D949B"
COLOR_SECUNDARIO_2 = "#58AAB0"
COLOR_ACENTO = "#F0AF39"
COLOR_ACENTO_2 = "#F7C76A"
COLOR_COMPLEMENTO = "#9C85AF"
COLOR_COMPLEMENTO_2 = "#EDE7F3"
COLOR_FONDO = "#F7F9FD"
COLOR_PANEL = "#FFFFFF"
COLOR_CARD_SUAVE = "#FAFBFF"
COLOR_TEXTO = "#273247"
COLOR_TEXTO_SUAVE = "#667085"
COLOR_BORDE = "#E7EAF0"
COLOR_LINEA_SUAVE = "#E9D7EF"
COLOR_PESTANA_ACTIVA = "#B753B6"
COLOR_ERROR = "#D94D5C"
COLOR_EXITO = "#2EAD68"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class InterfazBaseDatos:
    def __init__(self, root):
        self.root = root
        self.root.title("NordSign - Base de Datos")
        self.root.geometry("1100x680")
        self.root.minsize(980, 620)
        self.root.configure(bg=COLOR_FONDO)
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.init_database()
        self.configurar_estilos()
        self.crear_interfaz()
        self.cargar_usuarios()
        self.cargar_sesion()
        self.cargar_estado_sistema()

    # ── BASE DE DATOS ─────────────────────────────────────
    def conectar(self):
        return sqlite3.connect(DB_NAME)

    def init_database(self):
        conn = self.conectar()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                password_plain TEXT DEFAULT '',
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN password_plain TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sesion_activa (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                email TEXT NOT NULL
            )
        """)

        # Tabla de control general del sistema.
        # interfaz_habilitada = 1 permite login/registro.
        # interfaz_habilitada = 0 bloquea login/registro y cierra sesiones.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion_sistema (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                interfaz_habilitada INTEGER NOT NULL DEFAULT 1,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            INSERT OR IGNORE INTO configuracion_sistema
            (id, interfaz_habilitada, fecha_actualizacion)
            VALUES (1, 1, CURRENT_TIMESTAMP)
        """)

        conn.commit()
        conn.close()

    # ── ESTILO TREEVIEW ───────────────────────────────────
    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=COLOR_PANEL,
            foreground=COLOR_TEXTO,
            rowheight=36,
            fieldbackground=COLOR_PANEL,
            bordercolor=COLOR_BORDE,
            borderwidth=0,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=COLOR_PRIMARIO,
            foreground="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padding=9
        )

        style.map(
            "Treeview",
            background=[("selected", COLOR_SECUNDARIO)],
            foreground=[("selected", "white")]
        )

        style.configure(
            "Vertical.TScrollbar",
            background=COLOR_COMPLEMENTO_2,
            troughcolor=COLOR_CARD_SUAVE,
            bordercolor=COLOR_BORDE,
            arrowcolor=COLOR_PRIMARIO
        )

    # ── COMPONENTES VISUALES ──────────────────────────────
    def crear_boton(self, parent, texto, color, comando, fg="white", ancho=16):
        return tk.Button(
            parent,
            text=texto,
            bg=color,
            fg=fg,
            activebackground=color,
            activeforeground=fg,
            font=("Arial", 10, "bold"),
            relief="flat",
            bd=0,
            width=ancho,
            height=2,
            cursor="hand2",
            command=comando
        )

    def crear_tarjeta(self, parent, bg=COLOR_PANEL, padx=18, pady=16):
        return tk.Frame(
            parent,
            bg=bg,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1,
            padx=padx,
            pady=pady
        )

    def crear_interfaz(self):
        # ── Header igual al dashboard visual ─────────────────
        header_frame = tk.Frame(self.root, bg=COLOR_PRIMARIO, height=78)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="●  NordSign",
            font=("Arial", 18, "bold"),
            bg=COLOR_PRIMARIO,
            fg="white"
        ).pack(side="left", padx=25)

        tk.Label(
            header_frame,
            text="Administrador de Base de Datos",
            font=("Arial", 11, "bold"),
            bg=COLOR_PRIMARIO,
            fg="#EAF5F7"
        ).pack(side="left", padx=5)

        tk.Label(
            header_frame,
            text="usuarios.db",
            font=("Arial", 11, "bold"),
            bg=COLOR_PRIMARIO,
            fg="white"
        ).pack(side="right", padx=25)

        shell = tk.Frame(self.root, bg=COLOR_FONDO)
        shell.pack(fill="both", expand=True, padx=26, pady=(22, 16))

        main_panel = tk.Frame(
            shell,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1
        )
        main_panel.pack(fill="both", expand=True)

        # ── Barra superior interna ──────────────────────────
        top_row = tk.Frame(main_panel, bg=COLOR_PANEL)
        top_row.pack(fill="x", padx=28, pady=(22, 12))

        search_box = tk.Frame(
            top_row,
            bg=COLOR_CARD_SUAVE,
            highlightbackground=COLOR_LINEA_SUAVE,
            highlightthickness=1
        )
        search_box.pack(side="left", fill="x", expand=True, ipady=6)
        self.search_var = tk.StringVar()

        self.search_entry = tk.Entry(
            search_box,
            textvariable=self.search_var,
            font=("Arial", 11),
            bg=COLOR_CARD_SUAVE,
            fg=COLOR_TEXTO,
            relief="flat",
            bd=0,
            insertbackground=COLOR_PRIMARIO
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(18, 8), ipady=4)
        self.search_entry.insert(0, "Buscar usuario por nombre o correo...")

        def limpiar_placeholder(event=None):
            if self.search_entry.get() == "Buscar usuario por nombre o correo...":
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(fg=COLOR_TEXTO)

        def poner_placeholder(event=None):
            if not self.search_entry.get().strip():
                self.search_entry.insert(0, "Buscar usuario por nombre o correo...")
                self.search_entry.config(fg=COLOR_TEXTO_SUAVE)

        self.search_entry.config(fg=COLOR_TEXTO_SUAVE)
        self.search_entry.bind("<FocusIn>", limpiar_placeholder)
        self.search_entry.bind("<FocusOut>", poner_placeholder)
        self.search_entry.bind("<KeyRelease>", lambda e: self.buscar_usuarios())

        tk.Button(
            search_box,
            text="🔍",
            font=("Arial", 14, "bold"),
            bg=COLOR_CARD_SUAVE,
            fg=COLOR_COMPLEMENTO,
            activebackground=COLOR_COMPLEMENTO_2,
            activeforeground=COLOR_PRIMARIO,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.buscar_usuarios
        ).pack(side="right", padx=(4, 8))

        tk.Button(
            search_box,
            text="Limpiar",
            font=("Arial", 9, "bold"),
            bg=COLOR_COMPLEMENTO_2,
            fg=COLOR_COMPLEMENTO,
            activebackground=COLOR_LINEA_SUAVE,
            activeforeground=COLOR_PRIMARIO,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.limpiar_busqueda
        ).pack(side="right", padx=(0, 10), ipadx=8, ipady=3)

        self.total_label = tk.Label(
            top_row,
            text="Usuarios: 0",
            font=("Arial", 11, "bold"),
            bg=COLOR_COMPLEMENTO_2,
            fg=COLOR_COMPLEMENTO,
            padx=18,
            pady=8
        )
        self.total_label.pack(side="right", padx=(22, 0))

        tk.Label(
            main_panel,
            text="Gestión de usuarios",
            font=("Arial", 24, "bold"),
            bg=COLOR_PANEL,
            fg=COLOR_PRIMARIO
        ).pack(anchor="w", padx=28, pady=(0, 4))

        tk.Label(
            main_panel,
            text="Agrega, actualiza, elimina usuarios y controla la sesión activa del sistema.",
            font=("Arial", 11),
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SUAVE
        ).pack(anchor="w", padx=30, pady=(0, 14))

        # ── Formulario ─────────────────────────────────────
        form_card = self.crear_tarjeta(main_panel, bg=COLOR_CARD_SUAVE, padx=20, pady=16)
        form_card.pack(fill="x", padx=28, pady=(0, 14))

        tk.Label(
            form_card,
            text="Datos del usuario",
            font=("Arial", 16, "bold"),
            bg=COLOR_CARD_SUAVE,
            fg=COLOR_PRIMARIO
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        tk.Label(form_card, text="Correo electrónico", bg=COLOR_CARD_SUAVE, fg=COLOR_TEXTO, font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.email_entry = tk.Entry(form_card, width=38, font=("Arial", 11), relief="solid", bd=1, highlightthickness=1, highlightbackground=COLOR_BORDE)
        self.email_entry.grid(row=2, column=0, sticky="ew", padx=(0, 16), ipady=8)

        tk.Label(form_card, text="Contraseña visible", bg=COLOR_CARD_SUAVE, fg=COLOR_TEXTO, font=("Arial", 10, "bold")).grid(row=1, column=1, sticky="w", pady=(0, 5))
        self.password_entry = tk.Entry(form_card, width=30, font=("Arial", 11), relief="solid", bd=1, highlightthickness=1, highlightbackground=COLOR_BORDE)
        self.password_entry.grid(row=2, column=1, sticky="ew", padx=(0, 16), ipady=8)

        botones = tk.Frame(form_card, bg=COLOR_CARD_SUAVE)
        botones.grid(row=2, column=2, sticky="e")

        self.crear_boton(botones, "➕ Agregar", COLOR_SECUNDARIO, self.agregar_usuario, ancho=13).grid(row=0, column=0, padx=5)
        self.crear_boton(botones, "🔒 Cambiar", COLOR_ACENTO, self.cambiar_password, fg=COLOR_PRIMARIO, ancho=13).grid(row=0, column=1, padx=5)
        self.crear_boton(botones, "🗑 Eliminar", COLOR_ERROR, self.eliminar_usuario, ancho=13).grid(row=0, column=2, padx=5)
        self.crear_boton(botones, "🔄 Actualizar", COLOR_COMPLEMENTO, self.actualizar_todo, ancho=13).grid(row=0, column=3, padx=5)

        form_card.grid_columnconfigure(0, weight=2)
        form_card.grid_columnconfigure(1, weight=1)
        form_card.grid_columnconfigure(2, weight=0)

        # ── Cuerpo central: tabla + panel lateral ───────────
        center = tk.Frame(main_panel, bg=COLOR_PANEL)
        center.pack(fill="both", expand=True, padx=28, pady=(0, 18))

        table_card = self.crear_tarjeta(center, bg=COLOR_PANEL, padx=0, pady=0)
        table_card.pack(side="left", fill="both", expand=True, padx=(0, 16))

        table_header = tk.Frame(table_card, bg=COLOR_PANEL)
        table_header.pack(fill="x", padx=18, pady=(16, 8))

        tk.Label(table_header, text="Usuarios registrados", font=("Arial", 16, "bold"), bg=COLOR_PANEL, fg=COLOR_PRIMARIO).pack(side="left")
        tk.Label(table_header, text="Selecciona una fila para editarla", font=("Arial", 10), bg=COLOR_PANEL, fg=COLOR_TEXTO_SUAVE).pack(side="right")

        frame_tabla = tk.Frame(table_card, bg=COLOR_PANEL)
        frame_tabla.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        columnas = ("id", "email", "password_plain", "fecha_registro")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        self.tabla.heading("id", text="ID")
        self.tabla.heading("email", text="Correo")
        self.tabla.heading("password_plain", text="Contraseña visible")
        self.tabla.heading("fecha_registro", text="Fecha registro")

        self.tabla.column("id", width=55, anchor="center")
        self.tabla.column("email", width=320)
        self.tabla.column("password_plain", width=190)
        self.tabla.column("fecha_registro", width=215, anchor="center")

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_usuario)

        side_panel = self.crear_tarjeta(center, bg=COLOR_PANEL, padx=20, pady=18)
        side_panel.configure(width=310)
        side_panel.pack(side="right", fill="y")
        side_panel.pack_propagate(False)

        tk.Label(side_panel, text="Estado de sesión", font=("Arial", 17, "bold"), bg=COLOR_PANEL, fg=COLOR_PRIMARIO).pack(anchor="w", pady=(0, 10))

        session_box = tk.Frame(side_panel, bg=COLOR_COMPLEMENTO_2, highlightbackground=COLOR_LINEA_SUAVE, highlightthickness=1, padx=14, pady=14)
        session_box.pack(fill="x", pady=(0, 16))

        tk.Label(session_box, text="👤", font=("Arial", 24), bg=COLOR_COMPLEMENTO_2, fg=COLOR_COMPLEMENTO).pack(anchor="w")
        self.sesion_label = tk.Label(session_box, text="Sesión activa:\nninguna", bg=COLOR_COMPLEMENTO_2, fg=COLOR_COMPLEMENTO, font=("Arial", 11, "bold"), justify="left", wraplength=240)
        self.sesion_label.pack(anchor="w", pady=(4, 0))

        self.crear_boton(side_panel, "🚪 Borrar sesión activa", COLOR_PRIMARIO, self.borrar_sesion, ancho=26).pack(fill="x", pady=(0, 16))

        # ── Control de acceso de la interfaz visual ─────────
        control_box = tk.Frame(
            side_panel,
            bg=COLOR_CARD_SUAVE,
            highlightbackground=COLOR_LINEA_SUAVE,
            highlightthickness=1,
            padx=14,
            pady=14
        )
        control_box.pack(fill="x", pady=(0, 16))

        tk.Label(
            control_box,
            text="Control de acceso",
            font=("Arial", 13, "bold"),
            bg=COLOR_CARD_SUAVE,
            fg=COLOR_PRIMARIO
        ).pack(anchor="w", pady=(0, 6))

        self.estado_interfaz_label = tk.Label(
            control_box,
            text="Interfaz: habilitada",
            font=("Arial", 11, "bold"),
            bg=COLOR_CARD_SUAVE,
            fg=COLOR_EXITO,
            justify="left"
        )
        self.estado_interfaz_label.pack(anchor="w", pady=(0, 10))

        self.toggle_interfaz_btn = self.crear_boton(
            control_box,
            "🔴 Apagar interfaz",
            COLOR_ERROR,
            self.toggle_interfaz,
            ancho=24
        )
        self.toggle_interfaz_btn.pack(fill="x")

        tk.Label(
            control_box,
            text="Al apagarla se cierran las sesiones y luego nadie podrá iniciar sesión ni registrarse.",
            font=("Arial", 9),
            bg=COLOR_CARD_SUAVE,
            fg=COLOR_TEXTO_SUAVE,
            wraplength=245,
            justify="left"
        ).pack(anchor="w", pady=(10, 0))

        info = tk.Frame(side_panel, bg=COLOR_CARD_SUAVE, highlightbackground=COLOR_LINEA_SUAVE, highlightthickness=1, padx=14, pady=14)
        info.pack(fill="x", pady=(0, 16))
        tk.Label(info, text="Información", font=("Arial", 13, "bold"), bg=COLOR_CARD_SUAVE, fg=COLOR_PRIMARIO).pack(anchor="w", pady=(0, 8))
        tk.Label(info, text="Esta ventana usa la misma base usuarios.db de la interfaz visual de NordSign.", font=("Arial", 10), bg=COLOR_CARD_SUAVE, fg=COLOR_TEXTO_SUAVE, wraplength=245, justify="left").pack(anchor="w")

        mini_cards = tk.Frame(side_panel, bg=COLOR_PANEL)
        mini_cards.pack(fill="x", pady=(0, 12))
        self.card_usuarios = self.crear_mini_estado(mini_cards, "👥", "Usuarios", "0", COLOR_SECUNDARIO)
        self.card_usuarios.pack(fill="x", pady=(0, 8))
        self.card_db = self.crear_mini_estado(mini_cards, "🗄️", "Base", "Activa", COLOR_ACENTO)
        self.card_db.pack(fill="x")

        tk.Label(side_panel, text="Presiona Esc para salir de pantalla completa.", font=("Arial", 9, "italic"), bg=COLOR_PANEL, fg=COLOR_TEXTO_SUAVE, wraplength=240, justify="left").pack(side="bottom", anchor="w")

    def crear_mini_estado(self, parent, icono, titulo, valor, color):
        card = tk.Frame(parent, bg=COLOR_CARD_SUAVE, highlightbackground=COLOR_LINEA_SUAVE, highlightthickness=1, padx=12, pady=10)
        tk.Label(card, text=icono, font=("Arial", 20), bg=COLOR_CARD_SUAVE, fg=color).pack(side="left", padx=(0, 10))
        textos = tk.Frame(card, bg=COLOR_CARD_SUAVE)
        textos.pack(side="left", fill="x", expand=True)
        tk.Label(textos, text=titulo, font=("Arial", 9, "bold"), bg=COLOR_CARD_SUAVE, fg=COLOR_TEXTO_SUAVE).pack(anchor="w")
        tk.Label(textos, text=valor, font=("Arial", 13, "bold"), bg=COLOR_CARD_SUAVE, fg=color).pack(anchor="w")
        return card

    # ── FUNCIONES ─────────────────────────────────────────
    def actualizar_todo(self):
        self.cargar_usuarios()
        self.cargar_sesion()
        self.cargar_estado_sistema()

    def obtener_texto_busqueda(self):
        if not hasattr(self, "search_entry"):
            return ""

        texto = self.search_entry.get().strip()

        if texto == "Buscar usuario por nombre o correo...":
            return ""

        return texto

    def buscar_usuarios(self):
        texto = self.obtener_texto_busqueda()

        if not texto:
            self.cargar_usuarios()
            return

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            conn = self.conectar()
            cursor = conn.cursor()

            patron = f"%{texto}%"

            cursor.execute("""
                SELECT id, email, password_plain, fecha_registro
                FROM usuarios
                WHERE email LIKE ?
                ORDER BY id DESC
            """, (patron,))

            usuarios = cursor.fetchall()
            conn.close()

            for i, usuario in enumerate(usuarios):
                tag = "par" if i % 2 == 0 else "impar"
                self.tabla.insert("", "end", values=usuario, tags=(tag,))

            self.tabla.tag_configure("par", background="#FFFFFF")
            self.tabla.tag_configure("impar", background="#FAFBFF")
            self.total_label.config(text=f"Resultados: {len(usuarios)}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar el usuario:\n{e}")

    def limpiar_busqueda(self):
        if hasattr(self, "search_entry"):
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, "Buscar usuario por nombre o correo...")
            self.search_entry.config(fg=COLOR_TEXTO_SUAVE)

        self.cargar_usuarios()

    def obtener_estado_sistema(self):
        """Devuelve True si la interfaz visual está habilitada."""
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT interfaz_habilitada
                FROM configuracion_sistema
                WHERE id = 1
            """)
            row = cursor.fetchone()
            conn.close()
            return bool(row[0]) if row else True
        except Exception as e:
            print(f"Error al leer estado del sistema: {e}")
            return True

    def cargar_estado_sistema(self):
        """Actualiza el botón de encendido/apagado en pantalla."""
        if not hasattr(self, "estado_interfaz_label"):
            return

        habilitada = self.obtener_estado_sistema()

        if habilitada:
            self.estado_interfaz_label.config(
                text="🟢 Interfaz: habilitada",
                fg=COLOR_EXITO
            )
            self.toggle_interfaz_btn.config(
                text="🔴 Apagar interfaz",
                bg=COLOR_ERROR,
                activebackground=COLOR_ERROR,
                fg="white",
                activeforeground="white"
            )
        else:
            self.estado_interfaz_label.config(
                text="🔴 Interfaz: apagada",
                fg=COLOR_ERROR
            )
            self.toggle_interfaz_btn.config(
                text="🟢 Encender interfaz",
                bg=COLOR_EXITO,
                activebackground=COLOR_EXITO,
                fg="white",
                activeforeground="white"
            )

    def toggle_interfaz(self):
        """Activa o desactiva el acceso a la interfaz visual."""
        habilitada = self.obtener_estado_sistema()

        if habilitada:
            confirmar = messagebox.askyesno(
                "Apagar interfaz",
                "¿Seguro que deseas apagar la interfaz visual?\\n\\n"
                "Esto cerrará todas las sesiones activas y bloqueará el inicio de sesión y el registro."
            )
            if not confirmar:
                return
            nuevo_estado = 0
        else:
            confirmar = messagebox.askyesno(
                "Encender interfaz",
                "¿Deseas volver a habilitar la interfaz visual?\\n\\n"
                "Los usuarios podrán iniciar sesión y registrarse nuevamente."
            )
            if not confirmar:
                return
            nuevo_estado = 1

        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE configuracion_sistema
                SET interfaz_habilitada = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = 1
            """, (nuevo_estado,))

            if nuevo_estado == 0:
                cursor.execute("DELETE FROM sesion_activa")

            conn.commit()
            conn.close()

            if nuevo_estado == 0:
                messagebox.showinfo(
                    "Interfaz apagada",
                    "La interfaz fue apagada correctamente.\\nTodas las sesiones activas fueron cerradas."
                )
            else:
                messagebox.showinfo(
                    "Interfaz encendida",
                    "La interfaz fue habilitada nuevamente."
                )

            self.cargar_sesion()
            self.cargar_estado_sistema()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar el estado de la interfaz:\\n{e}")


    def cargar_usuarios(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, email, password_plain, fecha_registro
            FROM usuarios
            ORDER BY id DESC
        """)
        usuarios = cursor.fetchall()
        conn.close()

        for i, usuario in enumerate(usuarios):
            tag = "par" if i % 2 == 0 else "impar"
            self.tabla.insert("", "end", values=usuario, tags=(tag,))

        self.tabla.tag_configure("par", background="#FFFFFF")
        self.tabla.tag_configure("impar", background="#FAFBFF")
        self.total_label.config(text=f"Usuarios: {len(usuarios)}")

        try:
            for widget in self.card_usuarios.winfo_children():
                pass
            # actualizar mini card recreando texto simple por seguridad
            self.card_usuarios.destroy()
            parent = self.card_db.master
            self.card_usuarios = self.crear_mini_estado(parent, "👥", "Usuarios", str(len(usuarios)), COLOR_SECUNDARIO)
            self.card_usuarios.pack(fill="x", pady=(0, 8), before=self.card_db)
        except Exception:
            pass

    def cargar_sesion(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM sesion_activa WHERE id = 1")
        sesion = cursor.fetchone()
        conn.close()

        if sesion:
            self.sesion_label.config(text=f"Sesión activa:\n{sesion[0]}")
        else:
            self.sesion_label.config(text="Sesión activa:\nninguna")

    def seleccionar_usuario(self, event):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            return

        valores = self.tabla.item(seleccionado[0], "values")
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, valores[1])
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, valores[2])

    def agregar_usuario(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "Completa correo y contraseña.")
            return
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Ingresa un correo válido.")
            return
        if len(password) < 6:
            messagebox.showerror("Error", "La contraseña debe tener mínimo 6 caracteres.")
            return

        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (email, password, password_plain, fecha_registro)
                VALUES (?, ?, ?, ?)
            """, (email, hash_password(password), password, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Usuario agregado correctamente.")
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.cargar_usuarios()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ese correo ya existe.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar:\n{e}")

    def cambiar_password(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "Selecciona un usuario y escribe la nueva contraseña.")
            return
        if len(password) < 6:
            messagebox.showerror("Error", "La contraseña debe tener mínimo 6 caracteres.")
            return

        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET password = ?, password_plain = ?
                WHERE email = ?
            """, (hash_password(password), password, email))
            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showerror("Error", "No se encontró ese usuario.")
            else:
                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.")

            conn.close()
            self.cargar_usuarios()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar la contraseña:\n{e}")

    def eliminar_usuario(self):
        email = self.email_entry.get().strip()

        if not email:
            messagebox.showerror("Error", "Selecciona o escribe el correo del usuario.")
            return

        confirmar = messagebox.askyesno("Confirmar eliminación", f"¿Seguro que deseas eliminar este usuario?\n\n{email}")
        if not confirmar:
            return

        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE email = ?", (email,))
            cursor.execute("DELETE FROM sesion_activa WHERE email = ?", (email,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.cargar_usuarios()
            self.cargar_sesion()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def borrar_sesion(self):
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sesion_activa WHERE id = 1")
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Sesión activa eliminada.")
            self.cargar_sesion()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo borrar la sesión:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazBaseDatos(root)
    root.mainloop()
