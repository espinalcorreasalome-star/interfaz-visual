import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
from datetime import datetime

# ── PALETA NORDSIGN - ESTÉTICA LIMPIA ───────────────────
# Colores base: #1B3A68, #3D949B, #F0AF39, #9C85AF
COLOR_PRIMARIO = "#1B3A68"       # Azul oscuro: encabezado principal
COLOR_PRIMARIO_2 = "#234A7D"     # Azul de apoyo
COLOR_SECUNDARIO = "#3D949B"     # Turquesa: acción principal
COLOR_SECUNDARIO_2 = "#58AAB0"   # Turquesa claro
COLOR_ACENTO = "#F0AF39"         # Amarillo: acción secundaria / alertas
COLOR_ACENTO_2 = "#F7C76A"       # Amarillo suave
COLOR_COMPLEMENTO = "#9C85AF"    # Morado: detalles y usuario
COLOR_COMPLEMENTO_2 = "#EDE7F3"  # Morado muy claro
COLOR_FONDO = "#F7F9FD"          # Fondo base claro
COLOR_FONDO_AZUL = "#EAF5F7"     # Mancha decorativa turquesa
COLOR_FONDO_AMARILLO = "#FFF0D2" # Mancha decorativa amarilla
COLOR_TARJETA = "#FFFFFF"        # Tarjetas y formularios
COLOR_TEXTO = "#273247"          # Texto principal
COLOR_TEXTO_SUAVE = "#667085"    # Texto secundario
COLOR_BORDE = "#E7EAF0"          # Bordes suaves

# Colores semánticos para mantener uniformidad después del login
COLOR_BOTON_PRINCIPAL = COLOR_SECUNDARIO      # Guardar, configurar, iniciar, acciones normales
COLOR_BOTON_SECUNDARIO = COLOR_COMPLEMENTO    # Cancelar, volver, salir
COLOR_BOTON_ALERTA = COLOR_ACENTO             # Estados en espera / detener
COLOR_CARD_SUAVE = "#FAFBFF"                 # Interior de tarjetas
COLOR_PANEL = "#FFFFFF"
COLOR_LINEA_SUAVE = "#E9D7EF"
COLOR_PESTANA_ACTIVA = "#B753B6"
COLOR_PESTANA_INACTIVA = COLOR_COMPLEMENTO
COLOR_SOMBRA = "#D9DDE8"

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NordSign - Sistema de Autenticación")
        self.root.geometry("450x650")
        self.root.resizable(True, True)
        self.root.configure(bg=COLOR_FONDO)
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.db_name = "usuarios.db"
        self.current_user = None
        self.init_database()

        # Si el administrador apagó la interfaz desde la base de datos,
        # se cierran sesiones y se bloquea login/registro.
        if not self.interfaz_esta_habilitada():
            self.clear_session()
            self.create_disabled_interface()
            return

        # ── CAMBIO 1: Verificar sesión guardada al iniciar ──────────────────
        saved_session = self.load_session()
        if saved_session:
            self.current_user = saved_session
            self.root.geometry("800x600")
            self.root.attributes("-fullscreen", True)
            self.create_dashboard_layout()
        else:
            self.create_main_interface()

    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                password_plain TEXT DEFAULT '',
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Agrega la columna password_plain si la base de datos ya existía
        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN password_plain TEXT DEFAULT ''")
            conn.commit()
        except sqlite3.OperationalError:
            pass

        # ── CAMBIO 2: Tabla para sesión persistente ─────────────────────────
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sesion_activa (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                email TEXT NOT NULL
            )
        ''')

        # Tabla compartida con la interfaz de base de datos.
        # interfaz_habilitada = 1 permite usar la interfaz visual.
        # interfaz_habilitada = 0 bloquea inicio de sesión y registro.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion_sistema (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                interfaz_habilitada INTEGER NOT NULL DEFAULT 1,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            INSERT OR IGNORE INTO configuracion_sistema
            (id, interfaz_habilitada, fecha_actualizacion)
            VALUES (1, 1, CURRENT_TIMESTAMP)
        ''')

        conn.commit()
        conn.close()
        print(f"Base de datos '{self.db_name}' inicializada correctamente")

    # ── CAMBIO 3: Métodos para guardar/cargar/borrar sesión ─────────────────
    def save_session(self, email):
        if not self.interfaz_esta_habilitada():
            self.clear_session()
            return
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO sesion_activa (id, email) VALUES (1, ?)", (email,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error al guardar sesión: {e}")

    def load_session(self):
        if not self.interfaz_esta_habilitada():
            self.clear_session()
            return None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM sesion_activa WHERE id = 1")
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            print(f"Error al cargar sesión: {e}")
            return None

    def clear_session(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sesion_activa WHERE id = 1")
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error al borrar sesión: {e}")

    def interfaz_esta_habilitada(self):
        """Lee el estado de encendido/apagado guardado por la interfaz de base de datos."""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracion_sistema (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    interfaz_habilitada INTEGER NOT NULL DEFAULT 1,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                INSERT OR IGNORE INTO configuracion_sistema
                (id, interfaz_habilitada, fecha_actualizacion)
                VALUES (1, 1, CURRENT_TIMESTAMP)
            ''')
            cursor.execute("SELECT interfaz_habilitada FROM configuracion_sistema WHERE id = 1")
            row = cursor.fetchone()
            conn.commit()
            conn.close()
            return bool(row[0]) if row else True
        except Exception as e:
            print(f"Error al verificar estado de interfaz: {e}")
            return True

    def bloquear_si_interfaz_apagada(self):
        """Devuelve True si debe bloquear la acción actual."""
        if self.interfaz_esta_habilitada():
            return False
        self.clear_session()
        self.current_user = None
        messagebox.showwarning(
            "Interfaz deshabilitada",
            "NordSign se encuentra temporalmente deshabilitado por el administrador."
        )
        self.create_disabled_interface()
        return True

    def create_disabled_interface(self):
        """Pantalla que se muestra cuando la interfaz fue apagada desde la base de datos."""
        self.clear_root()
        canvas = self.draw_auth_background("Sistema deshabilitado")
        card = self.create_auth_card(canvas)

        tk.Label(
            card,
            text="🔒",
            font=("Arial", 44),
            bg=COLOR_COMPLEMENTO_2,
            fg=COLOR_COMPLEMENTO,
            width=3
        ).pack(pady=(0, 14))

        tk.Label(
            card,
            text="NordSign está apagado",
            font=("Arial", 22, "bold"),
            bg=COLOR_TARJETA,
            fg=COLOR_PRIMARIO
        ).pack(pady=(0, 8))

        tk.Label(
            card,
            text="El administrador deshabilitó temporalmente el acceso.\nNo se puede iniciar sesión ni registrar usuarios hasta que se encienda nuevamente.",
            font=("Arial", 12),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO_SUAVE,
            justify="center"
        ).pack(pady=(0, 24))

        def verificar_estado():
            if self.interfaz_esta_habilitada():
                messagebox.showinfo("Sistema habilitado", "La interfaz fue habilitada nuevamente.")
                self.create_main_interface()
            else:
                messagebox.showwarning("Sigue deshabilitado", "La interfaz aún está apagada por el administrador.")

        self.create_styled_button(
            card,
            "🔄 Verificar estado",
            COLOR_SECUNDARIO,
            verificar_estado
        ).pack(fill="x", pady=(0, 10))

        tk.Button(
            card,
            text="Cerrar ventana",
            font=("Arial", 11, "bold"),
            bg=COLOR_TARJETA,
            fg=COLOR_COMPLEMENTO,
            activebackground=COLOR_COMPLEMENTO_2,
            relief="flat",
            cursor="hand2",
            command=self.root.destroy
        ).pack(fill="x")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, email, password):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            hashed_password = self.hash_password(password)
            cursor.execute("INSERT INTO usuarios (email, password, password_plain) VALUES (?, ?, ?)", (email, hashed_password, password))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error al registrar usuario: {e}")
            return False

    def verify_user(self, email, password):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            hashed_password = self.hash_password(password)
            cursor.execute("SELECT * FROM usuarios WHERE email = ? AND password = ?", (email, hashed_password))
            user = cursor.fetchone()
            conn.close()
            return user is not None
        except Exception as e:
            print(f"Error al verificar usuario: {e}")
            return False

    def email_exists(self, email):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
            user = cursor.fetchone()
            conn.close()
            return user is not None
        except Exception as e:
            print(f"Error al verificar email: {e}")
            return False

    def get_user_count(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error al contar usuarios: {e}")
            return 0

    # ── ESTÉTICA GENERAL ─────────────────────────────────────────────────────
    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg=COLOR_FONDO)

    def create_styled_button(self, parent, text, bg, command, width=None):
        """Botón plano con apariencia moderna."""
        btn = tk.Button(
            parent,
            text=text,
            font=("Arial", 14, "bold"),
            bg=bg,
            fg="white",
            activebackground=bg,
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            height=2,
            command=command
        )
        if width:
            btn.config(width=width)
        return btn

    def draw_auth_background(self, title):
        """Fondo visual tipo landing: encabezado azul, manchas suaves y puntos decorativos.
        IMPORTANTE: solo borra elementos decorativos, NO borra los botones ni las tarjetas.
        """
        canvas = tk.Canvas(self.root, bg=COLOR_FONDO, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        def redraw(event=None):
            canvas.delete("decor")
            w = max(canvas.winfo_width(), 1)
            h = max(canvas.winfo_height(), 1)

            # Fondo principal
            canvas.create_rectangle(0, 0, w, h, fill=COLOR_FONDO, outline="", tags="decor")

            # Encabezado superior
            header_h = int(h * 0.22)
            canvas.create_rectangle(0, 0, w, header_h, fill=COLOR_PRIMARIO, outline="", tags="decor")
            canvas.create_oval(w - 180, -120, w + 220, header_h + 120, fill=COLOR_PRIMARIO_2, outline="", tags="decor")

            # Logo simple circular
            canvas.create_oval(70, 55, 135, 120, fill="white", outline="", tags="decor")
            canvas.create_polygon(86, 104, 103, 78, 114, 98, 121, 86, 135, 104, fill=COLOR_PRIMARIO, outline="", tags="decor")
            canvas.create_line(160, 55, 160, 120, fill="white", width=2, tags="decor")
            canvas.create_text(190, 88, text=title, anchor="w", fill="white", font=("Arial", 30, "bold"), tags="decor")

            # Puntos decorativos
            for i in range(5):
                for j in range(3):
                    x = w - 300 + i * 22
                    y = 65 + j * 25
                    canvas.create_oval(x, y, x + 5, y + 5, fill="#8DB0D5", outline="", tags="decor")

            # Manchas suaves del fondo
            canvas.create_oval(-150, int(h * 0.62), 260, h + 230, fill=COLOR_FONDO_AZUL, outline="", tags="decor")
            canvas.create_oval(w - 170, int(h * 0.15), w + 280, int(h * 0.58), fill=COLOR_COMPLEMENTO_2, outline="", tags="decor")
            canvas.create_oval(w - 260, h - 120, w + 230, h + 250, fill=COLOR_FONDO_AMARILLO, outline="", tags="decor")

            # Mantener el fondo detrás de tarjetas, formularios y botones
            canvas.tag_lower("decor")

        canvas.bind("<Configure>", redraw)
        canvas.after(50, redraw)
        return canvas

    def create_auth_card(self, canvas, mode="main"):
        card = tk.Frame(canvas, bg=COLOR_TARJETA, highlightbackground=COLOR_BORDE, highlightthickness=1)
        card.configure(padx=44, pady=34)
        canvas.create_window(0, 0, window=card, anchor="center", tags="auth_card")

        def position_card(event=None):
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            canvas.coords("auth_card", w // 2, int(h * 0.56))
            canvas.itemconfig("auth_card", width=min(560, max(w - 50, 320)))

        canvas.bind("<Configure>", position_card, add="+")
        position_card()
        return card

    def create_main_interface(self):
        if not self.interfaz_esta_habilitada():
            self.clear_session()
            self.create_disabled_interface()
            return
        self.clear_root()
        canvas = self.draw_auth_background("Bienvenido")
        card = self.create_auth_card(canvas)

        tk.Label(card, text="👤", font=("Arial", 42), bg=COLOR_COMPLEMENTO_2, fg=COLOR_COMPLEMENTO, width=3).pack(pady=(0, 14))
        tk.Label(card, text="Sistema de Autenticación", font=("Arial", 20, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(pady=(0, 8))
        tk.Label(
            card,
            text="Gestiona tu cuenta de forma segura\ny accede a todas las funcionalidades.",
            font=("Arial", 12),
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO_SUAVE,
            justify="center"
        ).pack(pady=(0, 26))

        self.create_styled_button(card, "👤   Iniciar Sesión", COLOR_SECUNDARIO, self.show_login_form).pack(fill="x", pady=(0, 12), ipadx=10)
        self.create_styled_button(card, "👥   Registrarse", COLOR_ACENTO, self.show_register_form).pack(fill="x", pady=(0, 4), ipadx=10)

        user_count = self.get_user_count()
        badge = tk.Frame(canvas, bg=COLOR_COMPLEMENTO_2, padx=22, pady=10)
        tk.Label(badge, text=f"👥  Usuarios registrados: {user_count}", font=("Arial", 12, "bold"), bg=COLOR_COMPLEMENTO_2, fg=COLOR_COMPLEMENTO).pack()
        canvas.create_window(0, 0, window=badge, anchor="center", tags="user_badge")

        def position_badge(event=None):
            canvas.coords("user_badge", canvas.winfo_width() // 2, int(canvas.winfo_height() * 0.90))
        canvas.bind("<Configure>", position_badge, add="+")
        position_badge()

    def show_login_form(self):
        if self.bloquear_si_interfaz_apagada():
            return
        self.clear_root()
        canvas = self.draw_auth_background("Iniciar Sesión")
        card = self.create_auth_card(canvas)

        tk.Label(card, text="🔐", font=("Arial", 40), bg=COLOR_COMPLEMENTO_2, fg=COLOR_COMPLEMENTO, width=3).pack(pady=(0, 12))
        tk.Label(card, text="Acceso a NordSign", font=("Arial", 20, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(pady=(0, 18))

        tk.Label(card, text="Correo Electrónico", font=("Arial", 11, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(anchor="w", pady=(0, 5))
        self.login_email_entry = tk.Entry(card, font=("Arial", 13), relief="solid", borderwidth=1, highlightthickness=1, highlightbackground=COLOR_BORDE)
        self.login_email_entry.pack(fill="x", ipady=9, pady=(0, 16))

        tk.Label(card, text="Contraseña", font=("Arial", 11, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(anchor="w", pady=(0, 5))
        self.login_password_entry = tk.Entry(card, font=("Arial", 13), show="*", relief="solid", borderwidth=1, highlightthickness=1, highlightbackground=COLOR_BORDE)
        self.login_password_entry.pack(fill="x", ipady=9, pady=(0, 24))

        self.create_styled_button(card, "Entrar", COLOR_SECUNDARIO, self.login).pack(fill="x", pady=(0, 10))
        tk.Button(card, text="← Volver", font=("Arial", 11, "bold"), bg=COLOR_TARJETA, fg=COLOR_COMPLEMENTO, activebackground=COLOR_COMPLEMENTO_2, relief="flat", cursor="hand2", command=self.create_main_interface).pack(fill="x")
        self.login_password_entry.bind('<Return>', lambda e: self.login())

    # ── FORMULARIO DE REGISTRO CORREGIDO ─────────────────────────────────────
    def show_register_form(self):
        if self.bloquear_si_interfaz_apagada():
            return
        self.clear_root()
        canvas = self.draw_auth_background("Crear Cuenta")
        card = self.create_auth_card(canvas)

        tk.Label(card, text="👥", font=("Arial", 40), bg=COLOR_COMPLEMENTO_2, fg=COLOR_COMPLEMENTO, width=3).pack(pady=(0, 12))
        tk.Label(card, text="Registro de Usuario", font=("Arial", 20, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(pady=(0, 18))

        tk.Label(card, text="Correo Electrónico", font=("Arial", 11, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(anchor="w", pady=(0, 5))
        self.register_email_entry = tk.Entry(card, font=("Arial", 13), relief="solid", borderwidth=1, highlightthickness=1, highlightbackground=COLOR_BORDE)
        self.register_email_entry.pack(fill="x", ipady=9, pady=(0, 13))

        tk.Label(card, text="Contraseña", font=("Arial", 11, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(anchor="w", pady=(0, 5))
        self.register_password_entry = tk.Entry(card, font=("Arial", 13), show="●", relief="solid", borderwidth=1, highlightthickness=1, highlightbackground=COLOR_BORDE)
        self.register_password_entry.pack(fill="x", ipady=9, pady=(0, 13))

        tk.Label(card, text="Confirmar Contraseña", font=("Arial", 11, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(anchor="w", pady=(0, 5))
        self.register_confirm_entry = tk.Entry(card, font=("Arial", 13), show="●", relief="solid", borderwidth=1, highlightthickness=1, highlightbackground=COLOR_BORDE)
        self.register_confirm_entry.pack(fill="x", ipady=9, pady=(0, 22))

        self.create_styled_button(card, "✓ Confirmar Registro", COLOR_ACENTO, self.register).pack(fill="x", pady=(0, 10))
        tk.Button(card, text="← Volver", font=("Arial", 11, "bold"), bg=COLOR_TARJETA, fg=COLOR_COMPLEMENTO, activebackground=COLOR_COMPLEMENTO_2, relief="flat", cursor="hand2", command=self.create_main_interface).pack(fill="x")
        self.register_confirm_entry.bind('<Return>', lambda e: self.register())

    def login(self):
        if self.bloquear_si_interfaz_apagada():
            return
        email = self.login_email_entry.get().strip()
        password = self.login_password_entry.get()
        if not email or not password:
            messagebox.showerror("Error", "Por favor completa todos los campos")
            return
        if not self.email_exists(email):
            messagebox.showerror("Error", "Este correo no está registrado")
            return
        if self.verify_user(email, password):
            self.current_user = email
            self.save_session(email)  # ── CAMBIO 4: Guardar sesión al iniciar
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")

    def register(self):
        if self.bloquear_si_interfaz_apagada():
            return
        email = self.register_email_entry.get().strip()
        password = self.register_password_entry.get()
        confirm_password = self.register_confirm_entry.get()
        if not email or not password or not confirm_password:
            messagebox.showerror("❌ Error", "Por favor completa todos los campos")
            return
        if "@" not in email or "." not in email:
            messagebox.showerror("❌ Error", "Por favor ingresa un correo electrónico válido")
            return
        if len(password) < 6:
            messagebox.showerror("❌ Error", "La contraseña debe tener al menos 6 caracteres")
            return
        if password != confirm_password:
            messagebox.showerror("❌ Error", "Las contraseñas no coinciden")
            return
        if self.email_exists(email):
            messagebox.showerror("❌ Error", "Este correo electrónico ya está registrado")
            return
        if self.register_user(email, password):
            messagebox.showinfo("✅ ¡Éxito!", f"¡Cuenta creada exitosamente!\n\nEmail: {email}\n\n¡Ya puedes iniciar sesión!")
            self.create_main_interface()
        else:
            messagebox.showerror("❌ Error", "No se pudo crear la cuenta. Intenta de nuevo.")

    def create_dashboard_layout(self):
        """Dashboard con estética tipo panel: encabezado, contenido en tarjetas y pestañas inferiores."""
        if self.bloquear_si_interfaz_apagada():
            return
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg=COLOR_FONDO)

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
            text=f"👤 {self.current_user}",
            font=("Arial", 11, "bold"),
            bg=COLOR_PRIMARIO,
            fg="white"
        ).pack(side="right", padx=25)

        shell = tk.Frame(self.root, bg=COLOR_FONDO)
        shell.pack(fill="both", expand=True, padx=26, pady=(22, 16))

        self.content_frame = tk.Frame(shell, bg=COLOR_FONDO)
        self.content_frame.pack(fill="both", expand=True)

        nav_bar = tk.Frame(self.root, bg=COLOR_PESTANA_ACTIVA, height=66)
        nav_bar.pack(side="bottom", fill="x", padx=70, pady=(0, 18))
        nav_bar.pack_propagate(False)

        menu_buttons = [
            ("🏠 Inicio", self.show_dashboard_content),
            ("🎓 Clase", self.show_classroom),
            ("⚙️ Ajustes", self.show_settings),
            ("🔔 Notificaciones", self.show_notifications),
            ("🚪 Salir", self.logout),
        ]

        for text, command in menu_buttons:
            tk.Button(
                nav_bar,
                text=text,
                font=("Arial", 12, "bold"),
                bg=COLOR_PESTANA_ACTIVA,
                fg="white",
                activebackground=COLOR_COMPLEMENTO,
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                command=command
            ).pack(side="left", expand=True, fill="both")

        self.show_dashboard_content()

    def show_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("800x600")
        self.root.attributes("-fullscreen", True)
        self.create_dashboard_layout()

    def _create_card(self, parent, bg=COLOR_CARD_SUAVE, border=COLOR_LINEA_SUAVE, padx=0, pady=0):
        card = tk.Frame(parent, bg=bg, highlightbackground=border, highlightthickness=1)
        if padx or pady:
            card.configure(padx=padx, pady=pady)
        return card

    def _nav_button(self, parent, text, command, active=False):
        bg = COLOR_COMPLEMENTO_2 if active else COLOR_PANEL
        fg = COLOR_PRIMARIO if active else COLOR_TEXTO_SUAVE
        return tk.Button(
            parent,
            text=text,
            font=("Arial", 11, "bold"),
            bg=bg,
            fg=fg,
            activebackground=COLOR_COMPLEMENTO_2,
            activeforeground=COLOR_PRIMARIO,
            relief="flat",
            bd=0,
            cursor="hand2",
            anchor="w",
            padx=18,
            command=command
        )

    def _action_button(self, parent, text, command, tipo="principal", width=16):
        colores = {
            "principal": (COLOR_BOTON_PRINCIPAL, COLOR_SECUNDARIO_2),
            "secundario": (COLOR_COMPLEMENTO, COLOR_COMPLEMENTO_2),
            "alerta": (COLOR_ACENTO, COLOR_ACENTO_2),
            "salir": ("#D94D5C", "#C43D4C"),
        }
        bg, active = colores.get(tipo, colores["principal"])
        fg = COLOR_PRIMARIO if tipo == "alerta" else "white"
        return tk.Button(
            parent,
            text=text,
            font=("Arial", 11, "bold"),
            bg=bg,
            fg=fg,
            activebackground=active,
            activeforeground=fg,
            relief="flat",
            bd=0,
            cursor="hand2",
            width=width,
            command=command
        )

    def show_dashboard_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Panel principal con estética educativa, limpia e infantil
        main_panel = tk.Frame(
            self.content_frame,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1
        )
        main_panel.pack(fill="both", expand=True, padx=10, pady=5)

        # Barra superior
        top_row = tk.Frame(main_panel, bg=COLOR_PANEL)
        top_row.pack(fill="x", padx=28, pady=(22, 12))

        search_box = tk.Frame(top_row, bg=COLOR_CARD_SUAVE, highlightbackground=COLOR_LINEA_SUAVE, highlightthickness=1)
        search_box.pack(side="left", fill="x", expand=True, ipady=6)
        tk.Label(search_box, text="Buscar letra, clase o actividad...", font=("Arial", 11), bg=COLOR_CARD_SUAVE, fg=COLOR_TEXTO_SUAVE).pack(side="left", padx=18)
        tk.Label(search_box, text="🔍", font=("Arial", 16), bg=COLOR_CARD_SUAVE, fg=COLOR_COMPLEMENTO).pack(side="right", padx=14)

        user_box = tk.Frame(top_row, bg=COLOR_PANEL)
        user_box.pack(side="right", padx=(22, 0))
        tk.Label(user_box, text="👤", font=("Arial", 20), bg=COLOR_PANEL, fg=COLOR_PRIMARIO).pack(side="left")
        tk.Label(user_box, text="Hola, usuario", font=("Arial", 11, "bold"), bg=COLOR_PANEL, fg=COLOR_PRIMARIO).pack(side="left", padx=(6, 16))
        tk.Button(user_box, text="🔔", font=("Arial", 16), bg=COLOR_PANEL, fg=COLOR_COMPLEMENTO, relief="flat", bd=0, cursor="hand2", command=self.show_notifications).pack(side="left", padx=4)
        tk.Button(user_box, text="⚙️", font=("Arial", 16), bg=COLOR_PANEL, fg=COLOR_COMPLEMENTO, relief="flat", bd=0, cursor="hand2", command=self.show_settings).pack(side="left", padx=4)

        body = tk.Frame(main_panel, bg=COLOR_PANEL)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        body.grid_columnconfigure(0, weight=1, uniform="cols")
        body.grid_columnconfigure(1, weight=1, uniform="cols")
        body.grid_rowconfigure(2, weight=1)

        # Bienvenida: enfocada en NordSign y LSC
        welcome = tk.Frame(body, bg=COLOR_PRIMARIO, highlightbackground=COLOR_BORDE, highlightthickness=1)
        welcome.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))
        tk.Label(welcome, text="Bienvenido de vuelta,", font=("Arial", 15, "bold"), bg=COLOR_PRIMARIO, fg="white").pack(anchor="w", padx=22, pady=(20, 0))
        tk.Label(welcome, text="NordSign 👋", font=("Arial", 24, "bold"), bg=COLOR_PRIMARIO, fg="white").pack(anchor="w", padx=22, pady=(2, 4))
        tk.Label(welcome, text="Practica letras en LSC con apoyo visual y cámara en tiempo real.", font=("Arial", 11), bg=COLOR_PRIMARIO, fg="#EAF5F7", wraplength=420, justify="left").pack(anchor="w", padx=22, pady=(0, 18))

        # Progreso del estudiante/prototipo
        progress_panel = self._create_card(body, bg=COLOR_CARD_SUAVE)
        progress_panel.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=(0, 12))
        tk.Label(progress_panel, text="Progreso de práctica", font=("Arial", 17, "bold"), bg=COLOR_CARD_SUAVE, fg=COLOR_PRIMARIO).pack(anchor="w", padx=22, pady=(18, 10))

        progress_items = tk.Frame(progress_panel, bg=COLOR_CARD_SUAVE)
        progress_items.pack(fill="x", padx=18, pady=(0, 15))
        datos_progreso = [
            ("🔤", "Letras", "9", COLOR_SECUNDARIO),
            ("✅", "Aciertos", "0", COLOR_SECUNDARIO),
            ("⏱️", "Práctica", "0 min", COLOR_COMPLEMENTO),
        ]
        for i, (icon, title, value, color) in enumerate(datos_progreso):
            mini = tk.Frame(progress_items, bg=COLOR_PANEL, highlightbackground=COLOR_LINEA_SUAVE, highlightthickness=1)
            mini.grid(row=0, column=i, padx=6, sticky="nsew")
            tk.Label(mini, text=icon, font=("Arial", 20), bg=COLOR_PANEL, fg=color).pack(pady=(10, 0))
            tk.Label(mini, text=value, font=("Arial", 18, "bold"), bg=COLOR_PANEL, fg=color).pack()
            tk.Label(mini, text=title, font=("Arial", 9, "bold"), bg=COLOR_PANEL, fg=COLOR_TEXTO_SUAVE).pack(pady=(0, 10))
            progress_items.grid_columnconfigure(i, weight=1)

        # Acciones principales uniformes
        actions = self._create_card(body, bg=COLOR_PANEL)
        actions.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        tk.Label(actions, text="Acciones rápidas", font=("Arial", 17, "bold"), bg=COLOR_PANEL, fg=COLOR_PRIMARIO).pack(anchor="w", padx=20, pady=(16, 8))
        actions_grid = tk.Frame(actions, bg=COLOR_PANEL)
        actions_grid.pack(fill="x", padx=16, pady=(0, 16))
        quick_actions = [
            ("🎓", "Clase virtual", "Practicar con cámara", self.show_classroom, COLOR_SECUNDARIO),
            ("🔤", "Letras LSC", "A, E, I, O, U, L, S, C, B", self.show_classroom, COLOR_COMPLEMENTO),
            ("📈", "Progreso", "Ver avances de práctica", lambda: messagebox.showinfo("Progreso", "Sección de progreso en preparación"), COLOR_ACENTO),
            ("⚙️", "Ajustes", "Configurar cuenta", self.show_settings, COLOR_COMPLEMENTO),
        ]
        for i, (icon, title, desc, cmd, color) in enumerate(quick_actions):
            card = tk.Frame(actions_grid, bg=COLOR_CARD_SUAVE, highlightbackground=COLOR_LINEA_SUAVE, highlightthickness=1)
            card.grid(row=0, column=i, padx=7, sticky="nsew")
            tk.Label(card, text=icon, font=("Arial", 27), bg=COLOR_CARD_SUAVE, fg=color).pack(pady=(14, 3))
            tk.Label(card, text=title, font=("Arial", 11, "bold"), bg=COLOR_CARD_SUAVE, fg=COLOR_PRIMARIO).pack()
            tk.Label(card, text=desc, font=("Arial", 9), bg=COLOR_CARD_SUAVE, fg=COLOR_TEXTO_SUAVE, wraplength=140).pack(pady=(2, 10))
            self._action_button(card, "Abrir", cmd, "principal", width=10).pack(pady=(0, 14), ipady=4)
            actions_grid.grid_columnconfigure(i, weight=1)

        # Se eliminó el panel inferior de “Estado del sistema” para dejar el inicio más limpio.
    # ── Ajustes ──────────────────────────────────────────────────────────────

    def show_settings(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        panel = tk.Frame(self.content_frame, bg=COLOR_PANEL, highlightbackground=COLOR_COMPLEMENTO, highlightthickness=3)
        panel.pack(fill="both", expand=True, padx=10, pady=5)
        tk.Label(panel, text="⚙️ Configuración", font=("Arial", 24, "bold"), bg=COLOR_PANEL, fg=COLOR_PRIMARIO).pack(anchor="w", padx=26, pady=(24, 6))
        tk.Label(panel, text="Organiza tu cuenta y preferencias del sistema", font=("Arial", 11), bg=COLOR_PANEL, fg=COLOR_TEXTO_SUAVE).pack(anchor="w", padx=28, pady=(0, 18))

        settings_frame = tk.Frame(panel, bg=COLOR_PANEL)
        settings_frame.pack(fill="both", expand=True, padx=24, pady=10)
        settings_options = [
            ("👤", "Editar Perfil", self.show_edit_profile),
            ("🔒", "Cambiar Contraseña", self.show_change_password),
            ("🔔", "Notificaciones", self.show_notification_settings),
            ("🎨", "Tema de la Aplicación", self.show_theme_settings),
            ("🌐", "Idioma", self.show_language_settings),
            ("🔐", "Privacidad y Seguridad", self.show_privacy_settings),
        ]
        for i, (icon, text, cmd) in enumerate(settings_options):
            card = tk.Frame(settings_frame, bg=COLOR_CARD_SUAVE, highlightbackground=COLOR_LINEA_SUAVE, highlightthickness=1)
            card.grid(row=i//3, column=i%3, sticky="nsew", padx=10, pady=10)
            tk.Label(card, text=icon, font=("Arial", 26), bg=COLOR_CARD_SUAVE, fg=COLOR_COMPLEMENTO).pack(pady=(18, 5))
            tk.Label(card, text=text, font=("Arial", 12, "bold"), bg=COLOR_CARD_SUAVE, fg=COLOR_PRIMARIO).pack(pady=(0, 12))
            tk.Button(card, text="Configurar →", font=("Arial", 10, "bold"), bg=COLOR_BOTON_PRINCIPAL, fg="white", activebackground=COLOR_SECUNDARIO_2, relief="flat", cursor="hand2", command=cmd).pack(pady=(0, 18), ipadx=10, ipady=5)
        for c in range(3):
            settings_frame.grid_columnconfigure(c, weight=1)

    def show_edit_profile(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        tk.Label(self.content_frame, text="👤 Editar Perfil", font=("Arial", 24, "bold"), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=20)
        form_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        form_frame.pack(fill="both", expand=True, padx=50, pady=20)
        tk.Label(form_frame, text="Correo Electrónico:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20, pady=(20, 5))
        tk.Label(form_frame, text=self.current_user, font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO_SUAVE, relief="solid", borderwidth=1, padx=10, pady=8, anchor="w").pack(fill="x", padx=20, pady=(0, 20))
        tk.Label(form_frame, text="Nombre Completo:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20, pady=(0, 5))
        self.profile_name_entry = tk.Entry(form_frame, font=("Arial", 12), relief="solid", borderwidth=1)
        self.profile_name_entry.pack(fill="x", padx=20, ipady=8, pady=(0, 20))
        tk.Label(form_frame, text="Teléfono:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20, pady=(0, 5))
        self.profile_phone_entry = tk.Entry(form_frame, font=("Arial", 12), relief="solid", borderwidth=1)
        self.profile_phone_entry.pack(fill="x", padx=20, ipady=8, pady=(0, 30))
        buttons_frame = tk.Frame(form_frame, bg="white")
        buttons_frame.pack(fill="x", padx=20, pady=20)
        tk.Button(buttons_frame, text="💾 Guardar Cambios", font=("Arial", 12, "bold"), bg=COLOR_BOTON_PRINCIPAL, fg="white", cursor="hand2", command=self.save_profile).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=("Arial", 12), bg=COLOR_BOTON_SECUNDARIO, fg="white", cursor="hand2", command=self.show_settings).pack(side="left", padx=5)

    def save_profile(self):
        name = self.profile_name_entry.get().strip()
        phone = self.profile_phone_entry.get().strip()
        if not name and not phone:
            messagebox.showwarning("Aviso", "No has realizado ningún cambio")
            return
        messagebox.showinfo("✅ Éxito", f"Perfil actualizado correctamente\n\nNombre: {name}\nTeléfono: {phone}")
        self.show_settings()

    def show_change_password(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        tk.Label(self.content_frame, text="🔒 Cambiar Contraseña", font=("Arial", 24, "bold"), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=20)
        form_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        form_frame.pack(fill="both", expand=True, padx=50, pady=20)
        tk.Label(form_frame, text="Contraseña Actual:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20, pady=(20, 5))
        self.current_password_entry = tk.Entry(form_frame, font=("Arial", 12), show="*", relief="solid", borderwidth=1)
        self.current_password_entry.pack(fill="x", padx=20, ipady=8, pady=(0, 20))
        tk.Label(form_frame, text="Nueva Contraseña:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20, pady=(0, 5))
        self.new_password_entry = tk.Entry(form_frame, font=("Arial", 12), show="*", relief="solid", borderwidth=1)
        self.new_password_entry.pack(fill="x", padx=20, ipady=8, pady=(0, 20))
        tk.Label(form_frame, text="Confirmar Nueva Contraseña:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=20, pady=(0, 5))
        self.confirm_new_password_entry = tk.Entry(form_frame, font=("Arial", 12), show="*", relief="solid", borderwidth=1)
        self.confirm_new_password_entry.pack(fill="x", padx=20, ipady=8, pady=(0, 30))
        buttons_frame = tk.Frame(form_frame, bg="white")
        buttons_frame.pack(fill="x", padx=20, pady=20)
        tk.Button(buttons_frame, text="🔒 Cambiar Contraseña", font=("Arial", 12, "bold"), bg=COLOR_BOTON_PRINCIPAL, fg="white", cursor="hand2", command=self.change_password).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=("Arial", 12), bg=COLOR_BOTON_SECUNDARIO, fg="white", cursor="hand2", command=self.show_settings).pack(side="left", padx=5)

    def change_password(self):
        current_pass = self.current_password_entry.get()
        new_pass = self.new_password_entry.get()
        confirm_pass = self.confirm_new_password_entry.get()
        if not current_pass or not new_pass or not confirm_pass:
            messagebox.showerror("Error", "Por favor completa todos los campos")
            return
        if not self.verify_user(self.current_user, current_pass):
            messagebox.showerror("Error", "La contraseña actual es incorrecta")
            return
        if len(new_pass) < 6:
            messagebox.showerror("Error", "La nueva contraseña debe tener al menos 6 caracteres")
            return
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "Las contraseñas nuevas no coinciden")
            return
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET password = ?, password_plain = ? WHERE email = ?", (self.hash_password(new_pass), new_pass, self.current_user))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "✅ Contraseña actualizada correctamente")
            self.show_settings()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar contraseña: {e}")

    def show_notification_settings(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        tk.Label(self.content_frame, text="🔔 Notificaciones", font=("Arial", 24, "bold"), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=20)
        options_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        options_frame.pack(fill="both", expand=True, padx=50, pady=20)
        tk.Label(options_frame, text="Configura qué notificaciones quieres recibir", font=("Arial", 11), bg="white", fg=COLOR_TEXTO_SUAVE).pack(pady=20)
        self.notif_email   = tk.IntVar(value=1)
        self.notif_desktop = tk.IntVar(value=1)
        self.notif_sound   = tk.IntVar(value=0)
        for text, var in [("📧 Notificaciones por Email", self.notif_email), ("💻 Notificaciones de Escritorio", self.notif_desktop), ("🔊 Sonidos de Notificación", self.notif_sound)]:
            tk.Checkbutton(options_frame, text=text, font=("Arial", 12), bg="white", variable=var, cursor="hand2").pack(anchor="w", padx=40, pady=10)
        buttons_frame = tk.Frame(options_frame, bg="white")
        buttons_frame.pack(pady=30)
        tk.Button(buttons_frame, text="💾 Guardar", font=("Arial", 12, "bold"), bg=COLOR_BOTON_PRINCIPAL, fg="white", cursor="hand2", width=15, command=self.save_notification_settings).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=("Arial", 12), bg=COLOR_BOTON_SECUNDARIO, fg="white", cursor="hand2", width=15, command=self.show_settings).pack(side="left", padx=5)

    def save_notification_settings(self):
        messagebox.showinfo("✅ Éxito", "Configuración de notificaciones guardada")
        self.show_settings()

    def show_theme_settings(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        tk.Label(self.content_frame, text="🎨 Tema de la Aplicación", font=("Arial", 24, "bold"), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=20)
        options_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        options_frame.pack(fill="both", expand=True, padx=50, pady=20)
        tk.Label(options_frame, text="Selecciona el tema de la aplicación", font=("Arial", 11), bg="white", fg=COLOR_TEXTO_SUAVE).pack(pady=20)
        self.theme_var = tk.StringVar(value="claro")
        for text, value in [("☀️ Tema Claro", "claro"), ("🌙 Tema Oscuro", "oscuro"), ("🔵 Tema Azul", "azul")]:
            tk.Radiobutton(options_frame, text=text, font=("Arial", 12), bg="white", variable=self.theme_var, value=value, cursor="hand2").pack(anchor="w", padx=40, pady=10)
        tk.Label(options_frame, text="Nota: Los cambios se aplicarán en la próxima sesión", font=("Arial", 9, "italic"), bg="white", fg=COLOR_COMPLEMENTO).pack(pady=10)
        buttons_frame = tk.Frame(options_frame, bg="white")
        buttons_frame.pack(pady=30)
        tk.Button(buttons_frame, text="💾 Guardar", font=("Arial", 12, "bold"), bg=COLOR_BOTON_PRINCIPAL, fg="white", cursor="hand2", width=15, command=self.save_theme_settings).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=("Arial", 12), bg=COLOR_BOTON_SECUNDARIO, fg="white", cursor="hand2", width=15, command=self.show_settings).pack(side="left", padx=5)

    def save_theme_settings(self):
        messagebox.showinfo("✅ Éxito", f"Tema '{self.theme_var.get()}' guardado correctamente")
        self.show_settings()

    def show_language_settings(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        tk.Label(self.content_frame, text="🌐 Idioma", font=("Arial", 24, "bold"), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=20)
        options_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        options_frame.pack(fill="both", expand=True, padx=50, pady=20)
        tk.Label(options_frame, text="Selecciona el idioma de la aplicación", font=("Arial", 11), bg="white", fg=COLOR_TEXTO_SUAVE).pack(pady=20)
        self.language_var = tk.StringVar(value="es")
        for text, value in [("🇪🇸 Español", "es"), ("🇺🇸 English", "en"), ("🇫🇷 Français", "fr"), ("🇩🇪 Deutsch", "de")]:
            tk.Radiobutton(options_frame, text=text, font=("Arial", 12), bg="white", variable=self.language_var, value=value, cursor="hand2").pack(anchor="w", padx=40, pady=10)
        tk.Label(options_frame, text="Nota: Los cambios se aplicarán en la próxima sesión", font=("Arial", 9, "italic"), bg="white", fg=COLOR_COMPLEMENTO).pack(pady=10)
        buttons_frame = tk.Frame(options_frame, bg="white")
        buttons_frame.pack(pady=30)
        tk.Button(buttons_frame, text="💾 Guardar", font=("Arial", 12, "bold"), bg=COLOR_BOTON_PRINCIPAL, fg="white", cursor="hand2", width=15, command=self.save_language_settings).pack(side="left", padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=("Arial", 12), bg=COLOR_BOTON_SECUNDARIO, fg="white", cursor="hand2", width=15, command=self.show_settings).pack(side="left", padx=5)

    def save_language_settings(self):
        nombres = {'es': 'Español', 'en': 'English', 'fr': 'Français', 'de': 'Deutsch'}
        messagebox.showinfo("✅ Éxito", f"Idioma '{nombres[self.language_var.get()]}' guardado correctamente")
        self.show_settings()

    def show_privacy_settings(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        tk.Label(self.content_frame, text="🔐 Privacidad y Seguridad", font=("Arial", 24, "bold"), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=20)
        options_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        options_frame.pack(fill="both", expand=True, padx=50, pady=20)
        tk.Label(options_frame, text="Gestiona tu privacidad y seguridad", font=("Arial", 11), bg="white", fg=COLOR_TEXTO_SUAVE).pack(pady=20)
        for text, command, color in [
            ("🗑️ Eliminar Cuenta", self.delete_account_confirmation, COLOR_BOTON_SECUNDARIO),
            ("📥 Descargar mis Datos", self.download_user_data, COLOR_BOTON_PRINCIPAL),
            ("🔒 Ver Actividad Reciente", self.show_recent_activity, COLOR_BOTON_PRINCIPAL),
            ("🚪 Cerrar Sesión en Todos los Dispositivos", self.logout_all_devices, COLOR_BOTON_ALERTA),
        ]:
            option_frame = tk.Frame(options_frame, bg="white")
            option_frame.pack(fill="x", padx=20, pady=10)
            tk.Button(option_frame, text=text, font=("Arial", 11), bg=color, fg="white", cursor="hand2", width=40, command=command).pack(pady=5)
        tk.Button(options_frame, text="← Volver", font=("Arial", 11), bg=COLOR_BOTON_SECUNDARIO, fg="white", cursor="hand2", width=20, command=self.show_settings).pack(pady=20)

    def delete_account_confirmation(self):
        if messagebox.askyesno("⚠️ Eliminar Cuenta", "¿Estás seguro de que deseas eliminar tu cuenta?\n\nEsta acción NO se puede deshacer.\nTodos tus datos serán eliminados permanentemente."):
            messagebox.showinfo("Cuenta Eliminada", "Tu cuenta ha sido eliminada")
            self.create_main_interface()

    def download_user_data(self):
        messagebox.showinfo("Descargar Datos", "Se enviará un archivo con todos tus datos\na tu correo electrónico")

    def show_recent_activity(self):
        messagebox.showinfo("Actividad Reciente", "Últimos accesos:\n\n• Hoy, 10:30 AM - Windows PC\n• Ayer, 3:45 PM - Android\n• 2 días atrás, 8:20 AM - Windows PC")

    def logout_all_devices(self):
        if messagebox.askyesno("Cerrar Todas las Sesiones", "¿Deseas cerrar sesión en todos los dispositivos?\n\nTendrás que iniciar sesión nuevamente."):
            messagebox.showinfo("Éxito", "✅ Sesiones cerradas en todos los dispositivos")
            self.logout()

    # ── Notificaciones ────────────────────────────────────────────────────────

    def show_notifications(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        panel = tk.Frame(self.content_frame, bg=COLOR_PANEL, highlightbackground=COLOR_COMPLEMENTO, highlightthickness=3)
        panel.pack(fill="both", expand=True, padx=10, pady=5)
        tk.Label(panel, text="🔔 Notificaciones", font=("Arial", 24, "bold"), bg=COLOR_PANEL, fg=COLOR_PRIMARIO).pack(anchor="w", padx=26, pady=(24, 12))

        notif_frame = tk.Frame(panel, bg=COLOR_PANEL)
        notif_frame.pack(fill="both", expand=True, padx=24, pady=10)
        notifications = [
            ("📧", "Nuevo mensaje recibido", "Revisa las actualizaciones de tu cuenta."),
            ("✅", "Tarea completada por equipo", "Una actividad del proyecto fue marcada como terminada."),
            ("⏰", "Fecha límite próxima", "Recuerda revisar las entregas pendientes."),
        ]
        for icon, title, desc in notifications:
            card = tk.Frame(notif_frame, bg=COLOR_CARD_SUAVE, highlightbackground=COLOR_LINEA_SUAVE, highlightthickness=1)
            card.pack(fill="x", pady=8, ipady=8)
            tk.Label(card, text=icon, font=("Arial", 24), bg=COLOR_CARD_SUAVE, fg=COLOR_COMPLEMENTO).pack(side="left", padx=18)
            text_box = tk.Frame(card, bg=COLOR_CARD_SUAVE)
            text_box.pack(side="left", fill="x", expand=True)
            tk.Label(text_box, text=title, font=("Arial", 12, "bold"), bg=COLOR_CARD_SUAVE, fg=COLOR_PRIMARIO).pack(anchor="w")
            tk.Label(text_box, text=desc, font=("Arial", 10), bg=COLOR_CARD_SUAVE, fg=COLOR_TEXTO_SUAVE).pack(anchor="w")

    # ── Clase Virtual con model_NS.pkl ────────────────────────────────────────

    def show_classroom(self):
        self.root.attributes("-fullscreen", True)
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.camera_active = False
        self.cap = None
        self.selected_letter = tk.StringVar(value="A")
        self.detected_letter = ""
        self.practice_hits = 0
        self.practice_attempts = 0
        self.last_correct_state = False

        main_class_frame = tk.Frame(
            self.content_frame,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1
        )
        main_class_frame.pack(fill="both", expand=True, padx=8, pady=3)

        # Encabezado de clase
        header = tk.Frame(main_class_frame, bg=COLOR_PRIMARIO, height=58)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🎓 Clase Virtual LSC", font=("Arial", 20, "bold"), bg=COLOR_PRIMARIO, fg="white").pack(side="left", padx=24)
        tk.Label(header, text="Practica, observa y repite la seña", font=("Arial", 11), bg=COLOR_PRIMARIO, fg="#EAF5F7").pack(side="left", padx=6)

        body = tk.Frame(main_class_frame, bg=COLOR_PANEL)
        body.pack(fill="both", expand=True, padx=18, pady=8)
        # Ajuste solicitado: se mantiene el apoyo visual y se permite
        # que la cámara use más espacio hacia la izquierda y hacia abajo
        body.grid_columnconfigure(0, weight=0, minsize=450)
        body.grid_columnconfigure(1, weight=1, minsize=760)
        body.grid_rowconfigure(0, weight=1)

        # Lado izquierdo: letra + apoyo visual + progreso
        left_frame = tk.Frame(body, bg=COLOR_CARD_SUAVE, width=450, highlightbackground=COLOR_LINEA_SUAVE, highlightthickness=1)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left_frame.grid_propagate(False)

        tk.Label(left_frame, text="Letra de práctica", font=("Arial", 15, "bold"), bg=COLOR_CARD_SUAVE, fg=COLOR_PRIMARIO).pack(pady=(10, 4))

        letras = ["A", "E", "I", "O", "U", "L", "S", "C", "B"]
        menu_letras = tk.OptionMenu(left_frame, self.selected_letter, *letras, command=self.select_letter)
        menu_letras.config(font=("Arial", 12, "bold"), bg=COLOR_SECUNDARIO, fg="white", activebackground=COLOR_SECUNDARIO_2, activeforeground="white", width=12, relief="flat", cursor="hand2")
        menu_letras.pack(pady=(0, 8), ipady=3)

        self.selected_letter_label = tk.Label(
            left_frame,
            text=self.selected_letter.get(),
            font=("Arial", 68, "bold"),
            bg=COLOR_PANEL,
            fg=COLOR_PRIMARIO,
            width=5,
            highlightbackground=COLOR_COMPLEMENTO_2,
            highlightthickness=2
        )
        self.selected_letter_label.pack(pady=(0, 8))

        self.visual_support_frame = tk.Frame(left_frame, bg=COLOR_PANEL, highlightbackground=COLOR_LINEA_SUAVE, highlightthickness=1)
        self.visual_support_frame.pack(padx=20, pady=(0, 8), fill="both", expand=True)

        self.visual_support_label = tk.Label(
            self.visual_support_frame,
            text="Aquí se mostrará\nel apoyo visual",
            font=("Arial", 11, "bold"),
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SUAVE,
            justify="center"
        )
        self.visual_support_label.pack(expand=True)

        progress_box = tk.Frame(left_frame, bg=COLOR_COMPLEMENTO_2, highlightbackground=COLOR_LINEA_SUAVE, highlightthickness=1)
        progress_box.pack(fill="x", padx=20, pady=(0, 10), ipady=6)
        self.class_progress_label = tk.Label(progress_box, text="Aciertos: 0  |  Intentos: 0", font=("Arial", 11, "bold"), bg=COLOR_COMPLEMENTO_2, fg=COLOR_COMPLEMENTO)
        self.class_progress_label.pack()

        self.update_visual_support("A")

        # Lado derecho: feedback + cámara
        right_frame = tk.Frame(body, bg=COLOR_PANEL)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=0)
        right_frame.grid_rowconfigure(1, weight=0)
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.feedback_label = tk.Label(
            right_frame,
            text="Haz la seña de la letra A",
            font=("Arial", 14, "bold"),
            bg=COLOR_ACENTO,
            fg=COLOR_PRIMARIO,
            height=1
        )
        self.feedback_label.grid(row=0, column=0, sticky="ew", pady=(0, 4), ipady=7)

        buttons_frame = tk.Frame(right_frame, bg=COLOR_PANEL)
        buttons_frame.grid(row=1, column=0, pady=(0, 6))

        self.start_class_btn = self._action_button(buttons_frame, "🎥 INICIAR CLASE", self.toggle_camera, "principal", width=18)
        self.start_class_btn.grid(row=0, column=0, padx=7, ipady=5)
        self._action_button(buttons_frame, "🚪 SALIR", self.exit_classroom, "salir", width=18).grid(row=0, column=1, padx=7, ipady=5)

        # Cámara expandida proporcionalmente hasta aproximarse a las líneas rojas
        # Mantiene una forma equilibrada, pero ocupa más del espacio disponible
        self.camera_frame = tk.Frame(right_frame, bg=COLOR_PRIMARIO, width=880, height=610, highlightbackground=COLOR_SECUNDARIO, highlightthickness=4)
        self.camera_frame.grid(row=2, column=0, sticky="n", pady=(0, 0))
        self.camera_frame.grid_propagate(False)
        self.camera_frame.pack_propagate(False)
        self.camera_label = tk.Label(
            self.camera_frame,
            bg="#0B1320",
            text="Presiona 'INICIAR CLASE' para encender la cámara",
            fg="white",
            font=("Arial", 14, "bold")
        )
        self.camera_label.pack(expand=True, fill="both")

    def select_letter(self, value):
        self.selected_letter.set(value)
        self.selected_letter_label.config(text=value)
        self.feedback_label.config(text=f"Haz la seña de la letra {value}", bg=COLOR_ACENTO, fg=COLOR_PRIMARIO)
        self.last_correct_state = False
        self.update_visual_support(value)

    def update_visual_support(self, letter):
        """Muestra la imagen de apoyo visual según la letra seleccionada.
        Solo debes guardar las imágenes en la carpeta 'imagenes' con el nombre correcto.
        """
        from PIL import Image, ImageTk
        import os

        # Obtener la carpeta donde está este archivo .py
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Carpeta donde deben guardarse las imágenes
        carpeta_imagenes = os.path.join(base_dir, "imagenes")

        # Nombre esperado para cada imagen
        image_paths = {
            "A": os.path.join(carpeta_imagenes, "apoyo_A.jpg"),
            "E": os.path.join(carpeta_imagenes, "apoyo_E.jpg"),
            "I": os.path.join(carpeta_imagenes, "apoyo_I.jpg"),
            "O": os.path.join(carpeta_imagenes, "apoyo_O.jpg"),
            "U": os.path.join(carpeta_imagenes, "apoyo_U.jpg"),
            "L": os.path.join(carpeta_imagenes, "apoyo_L.jpg"),
            "S": os.path.join(carpeta_imagenes, "apoyo_S.jpg"),
            "C": os.path.join(carpeta_imagenes, "apoyo_C.jpg"),
            "B": os.path.join(carpeta_imagenes, "apoyo_B.jpg"),
        }

        ruta = image_paths.get(letter)

        print("RUTA BUSCADA:", ruta)

        if ruta and os.path.exists(ruta):
            try:
                img = Image.open(ruta)

                # Imagen de apoyo un poco más grande, sin exagerar el tamaño
                img.thumbnail((350, 390), Image.LANCZOS)

                photo = ImageTk.PhotoImage(img)

                self.visual_support_label.config(
                    image=photo,
                    text=""
                )

                # Mantener referencia para que Tkinter no borre la imagen
                self.visual_support_label.image = photo

            except Exception as e:
                print("ERROR:", e)

                self.visual_support_label.config(
                    image="",
                    text=f"Error cargando imagen:\n{e}"
                )

                self.visual_support_label.image = None

        else:
            self.visual_support_label.config(
                image="",
                text=f"No encontrada:\n{ruta}"
            )

            self.visual_support_label.image = None

    def toggle_camera(self):
        if not self.camera_active:
            self.start_camera()
        else:
            self.stop_camera()

    def start_camera(self):
        """Iniciar la cámara con reconocimiento LSC usando model_NS.pkl."""
        try:
            import cv2
            from PIL import Image, ImageTk
            import mediapipe as mp
            import joblib
            import numpy as np

            # ── Cargar model_NS.pkl ──────────────────────────────────────────
            try:
                import os

                # Busca el modelo en la misma carpeta donde está este archivo .py
                base_dir = os.path.dirname(os.path.abspath(__file__))
                ruta_modelo = os.path.join(base_dir, "model_NS.pkl")

                bundle = joblib.load(ruta_modelo)

                if isinstance(bundle, dict):
                    self.modelo_lsc = bundle["modelo"]
                    self.label_enc  = bundle["encoder"]
                    self.features_modelo = bundle.get("features", None)
                    self.clases_modelo = bundle.get("clases", None)
                else:
                    self.modelo_lsc = bundle
                    self.label_enc  = None
                    self.features_modelo = None
                    self.clases_modelo = None

                self.lsc_enabled = True
                print("✅ model_NS.pkl cargado correctamente")

            except FileNotFoundError:
                self.modelo_lsc = None
                self.label_enc  = None
                self.features_modelo = None
                self.clases_modelo = None
                self.lsc_enabled = False
                print("⚠️ model_NS.pkl no encontrado. Colócalo en la misma carpeta que este archivo.")

            except Exception as e:
                self.modelo_lsc = None
                self.label_enc  = None
                self.features_modelo = None
                self.clases_modelo = None
                self.lsc_enabled = False
                print(f"⚠️ Error al cargar model_NS.pkl: {e}")

            # ── Inicializar MediaPipe ────────────────────────────────────────
            if self.lsc_enabled:
                self.mp_hands   = mp.solutions.hands
                self.hands      = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
                self.mp_drawing = mp.solutions.drawing_utils

            # ── Abrir cámara ─────────────────────────────────────────────────
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "No se pudo acceder a la cámara")
                return

            self.camera_active = True
            self.start_class_btn.config(text="⏸️ DETENER CLASE", bg=COLOR_ACENTO, fg=COLOR_PRIMARIO)
            self.update_camera()

        except ImportError as e:
            missing_lib = str(e).split("'")[1] if "'" in str(e) else "desconocida"
            messagebox.showerror("Error - Librería faltante", f"Falta instalar: {missing_lib}\n\npip install opencv-python pillow mediapipe joblib numpy scikit-learn")
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar la cámara:\n{str(e)}")

    def update_camera(self):
        """Actualizar frame con reconocimiento LSC usando model_NS.pkl."""
        if not self.camera_active or self.cap is None:
            return
        try:
            import cv2
            from PIL import Image, ImageTk
            import numpy as np

            ret, frame = self.cap.read()
            if not ret:
                self.camera_label.after(10, self.update_camera)
                return

            # ── Reconocimiento de señas ───────────────
            if self.lsc_enabled and self.modelo_lsc is not None:
                rgb       = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                resultado = self.hands.process(rgb)

                if resultado.multi_hand_landmarks:
                    hand = resultado.multi_hand_landmarks[0]
                    self.mp_drawing.draw_landmarks(frame, hand, self.mp_hands.HAND_CONNECTIONS)

                    datos = []
                    for lm in hand.landmark:
                        datos.extend([lm.x, lm.y, lm.z])
                    datos = np.array(datos, dtype=np.float32).reshape(1, -1)

                    try:
                        pred_id = self.modelo_lsc.predict(datos)[0]
                        letra   = self.label_enc.inverse_transform([pred_id])[0] if self.label_enc else str(pred_id)
                        letra   = str(letra).upper()

                        cv2.putText(frame, f"Detectado: {letra}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                        letra_objetivo = self.selected_letter.get().upper()
                        if letra == letra_objetivo:
                            self.feedback_label.config(text="✅ ¡BIEN HECHO!", bg=COLOR_SECUNDARIO, fg="white")
                            if not getattr(self, "last_correct_state", False):
                                self.practice_hits = getattr(self, "practice_hits", 0) + 1
                                self.practice_attempts = getattr(self, "practice_attempts", 0) + 1
                                self.last_correct_state = True
                                if hasattr(self, "class_progress_label"):
                                    self.class_progress_label.config(text=f"Aciertos: {self.practice_hits}  |  Intentos: {self.practice_attempts}")
                        else:
                            self.feedback_label.config(text=f"Haz la seña de la letra {letra_objetivo}", bg=COLOR_ACENTO, fg=COLOR_PRIMARIO)
                            if getattr(self, "last_correct_state", False):
                                self.last_correct_state = False

                    except Exception as e:
                        print(f"Error en predicción: {e}")

            # ── Indicador de estado ──────────────────────────────────────────
            if self.lsc_enabled:
                cv2.putText(frame, "LSC: ACTIVO", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 200, 0), 2)
            else:
                cv2.putText(frame, "LSC: sin model_NS.pkl", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 100, 255), 2)

            # ── Mostrar en Tkinter ───────────────────────────────────────────
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ancho_camara = max(self.camera_frame.winfo_width(), 1)
            alto_camara = max(self.camera_frame.winfo_height(), 1)
            frame = cv2.resize(frame, (ancho_camara, alto_camara))
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)

        except Exception as e:
            print(f"Error en update_camera: {e}")
            self.stop_camera()
            return

        self.camera_label.after(10, self.update_camera)

    def stop_camera(self):
        self.camera_active = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if hasattr(self, 'hands') and self.hands is not None:
            self.hands.close()
        self.camera_label.configure(image='')
        self.camera_label.imgtk = None
        self.start_class_btn.config(text="🎥 INICIAR CLASE", bg=COLOR_BOTON_PRINCIPAL, fg="white")

    def exit_classroom(self):
        if self.camera_active:
            self.stop_camera()
        self.show_dashboard_content()

    def logout(self):
        if hasattr(self, 'camera_active') and self.camera_active:
            self.stop_camera()
        if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que deseas cerrar sesión?"):
            self.clear_session()  # ── CAMBIO 5: Borrar sesión guardada al cerrar manualmente
            self.current_user = None
            self.root.geometry("400x500")
            self.root.attributes("-fullscreen", True)
            self.create_main_interface()


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()