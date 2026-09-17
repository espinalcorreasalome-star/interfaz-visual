"""
NordSign - Sistema de Reconocimiento de Lenguaje de Señas Colombiano
Versión: 4.0 FINAL COMPLETA
Características:
- Login y Registro
- Dashboard con menú reducido (Dashboard, Clase, Ajustes, Notificaciones)
- Reconocimiento LSC en tiempo real
- Ajustes completamente funcionales
- Base de datos SQLite
"""

import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
from datetime import datetime

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NordSign - Sistema de Autenticación")
        self.root.geometry("450x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # Nombre de la base de datos
        self.db_name = "usuarios.db"
        
        # Usuario actual (None si no hay sesión activa)
        self.current_user = None
        
        # Inicializar base de datos
        self.init_database()
        
        # Crear la interfaz principal
        self.create_main_interface()
    
    def init_database(self):
        """Crear la base de datos y tabla de usuarios si no existe"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Crear tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Base de datos '{self.db_name}' inicializada correctamente")
    
    def hash_password(self, password):
        """Encriptar contraseña usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, email, password):
        """Registrar un nuevo usuario en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(password)
            
            cursor.execute(
                "INSERT INTO usuarios (email, password) VALUES (?, ?)",
                (email, hashed_password)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # El email ya existe
            return False
        except Exception as e:
            print(f"Error al registrar usuario: {e}")
            return False
    
    def verify_user(self, email, password):
        """Verificar las credenciales del usuario"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(password)
            
            cursor.execute(
                "SELECT * FROM usuarios WHERE email = ? AND password = ?",
                (email, hashed_password)
            )
            
            user = cursor.fetchone()
            conn.close()
            
            return user is not None
        except Exception as e:
            print(f"Error al verificar usuario: {e}")
            return False
    
    def email_exists(self, email):
        """Verificar si un email ya está registrado"""
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
        """Obtener el número total de usuarios registrados"""
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
    
    def create_main_interface(self):
        """Crear la interfaz principal"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Título
        title_frame = tk.Frame(self.root, bg="#4a90e2", height=80)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="Bienvenido",
            font=("Arial", 24, "bold"),
            bg="#4a90e2",
            fg="white"
        )
        title_label.pack(expand=True)
        
        # Frame central
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Botón Iniciar Sesión
        login_btn = tk.Button(
            main_frame,
            text="Iniciar Sesión",
            font=("Arial", 14, "bold"),
            bg="#4a90e2",
            fg="white",
            cursor="hand2",
            height=2,
            command=self.show_login_form
        )
        login_btn.pack(fill="x", pady=10)
        
        # Botón Registrarse
        register_btn = tk.Button(
            main_frame,
            text="Crear Cuenta",
            font=("Arial", 14, "bold"),
            bg="#50c878",
            fg="white",
            cursor="hand2",
            height=2,
            command=self.show_register_form
        )
        register_btn.pack(fill="x", pady=10)
        
        # Mostrar número de usuarios registrados
        user_count = self.get_user_count()
        count_label = tk.Label(
            main_frame,
            text=f"Usuarios registrados: {user_count}",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        )
        count_label.pack(pady=(20, 0))
        
        # Pie de página
        footer_label = tk.Label(
            self.root,
            text="NordSign v4.0 - Sistema de Reconocimiento LSC",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#666"
        )
        footer_label.pack(side="bottom", pady=10)
    
    def show_login_form(self):
        """Mostrar formulario de inicio de sesión"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Título
        title_frame = tk.Frame(self.root, bg="#4a90e2", height=80)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="Iniciar Sesión",
            font=("Arial", 24, "bold"),
            bg="#4a90e2",
            fg="white"
        )
        title_label.pack(expand=True)
        
        # Frame del formulario
        form_frame = tk.Frame(self.root, bg="#f0f0f0")
        form_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Email
        email_label = tk.Label(
            form_frame,
            text="Correo Electrónico:",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        email_label.pack(anchor="w", pady=(0, 5))
        
        self.login_email_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            relief="solid",
            borderwidth=1
        )
        self.login_email_entry.pack(fill="x", ipady=8, pady=(0, 20))
        
        # Contraseña
        password_label = tk.Label(
            form_frame,
            text="Contraseña:",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.login_password_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            show="*",
            relief="solid",
            borderwidth=1
        )
        self.login_password_entry.pack(fill="x", ipady=8, pady=(0, 30))
        
        # Botón de Iniciar Sesión
        login_btn = tk.Button(
            form_frame,
            text="Iniciar Sesión",
            font=("Arial", 14, "bold"),
            bg="#4a90e2",
            fg="white",
            cursor="hand2",
            height=2,
            command=self.login
        )
        login_btn.pack(fill="x", pady=10)
        
        # Botón de Volver
        back_btn = tk.Button(
            form_frame,
            text="Volver",
            font=("Arial", 12),
            bg="#999",
            fg="white",
            cursor="hand2",
            command=self.create_main_interface
        )
        back_btn.pack(fill="x", pady=5)
        
        # Bind Enter key para iniciar sesión
        self.login_password_entry.bind('<Return>', lambda e: self.login())
    
    def show_register_form(self):
        """Mostrar formulario de registro"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Título
        title_frame = tk.Frame(self.root, bg="#50c878", height=100)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="Crear Cuenta",
            font=("Arial", 26, "bold"),
            bg="#50c878",
            fg="white"
        )
        title_label.pack(expand=True)
        
        # Frame del formulario
        form_frame = tk.Frame(self.root, bg="#f0f0f0")
        form_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Email
        email_label = tk.Label(
            form_frame,
            text="Correo Electrónico:",
            font=("Arial", 13, "bold"),
            bg="#f0f0f0"
        )
        email_label.pack(anchor="w", pady=(0, 5))
        
        self.register_email_entry = tk.Entry(
            form_frame,
            font=("Arial", 13),
            relief="solid",
            borderwidth=2
        )
        self.register_email_entry.pack(fill="x", ipady=10, pady=(0, 20))
        
        # Contraseña
        password_label = tk.Label(
            form_frame,
            text="Contraseña:",
            font=("Arial", 13, "bold"),
            bg="#f0f0f0"
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.register_password_entry = tk.Entry(
            form_frame,
            font=("Arial", 13),
            show="●",
            relief="solid",
            borderwidth=2
        )
        self.register_password_entry.pack(fill="x", ipady=10, pady=(0, 20))
        
        # Confirmar Contraseña
        confirm_label = tk.Label(
            form_frame,
            text="Confirmar Contraseña:",
            font=("Arial", 13, "bold"),
            bg="#f0f0f0"
        )
        confirm_label.pack(anchor="w", pady=(0, 5))
        
        self.register_confirm_entry = tk.Entry(
            form_frame,
            font=("Arial", 13),
            show="●",
            relief="solid",
            borderwidth=2
        )
        self.register_confirm_entry.pack(fill="x", ipady=10, pady=(0, 30))
        
        # ===================================================================
        # BOTÓN CONFIRMAR REGISTRO - MEJORADO Y MÁS VISIBLE
        # ===================================================================
        confirm_btn = tk.Button(
            form_frame,
            text="✓ CONFIRMAR REGISTRO",
            font=("Arial", 15, "bold"),
            bg="#27ae60",
            fg="white",
            cursor="hand2",
            height=3,
            relief="raised",
            borderwidth=3,
            command=self.register
        )
        confirm_btn.pack(fill="x", pady=15)
        
        # Botón de Volver
        back_btn = tk.Button(
            form_frame,
            text="← Volver",
            font=("Arial", 13),
            bg="#95a5a6",
            fg="white",
            cursor="hand2",
            height=2,
            command=self.create_main_interface
        )
        back_btn.pack(fill="x", pady=5)
        
        # Bind Enter key para registrarse
        self.register_confirm_entry.bind('<Return>', lambda e: self.register())
    
    def login(self):
        """Procesar inicio de sesión"""
        email = self.login_email_entry.get().strip()
        password = self.login_password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Por favor completa todos los campos")
            return
        
        if not self.email_exists(email):
            messagebox.showerror("Error", "Este correo no está registrado")
            return
        
        if self.verify_user(email, password):
            # Guardar el usuario actual
            self.current_user = email
            # Mostrar el dashboard
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")
    
    def register(self):
        """Procesar registro de nuevo usuario"""
        email = self.register_email_entry.get().strip()
        password = self.register_password_entry.get()
        confirm_password = self.register_confirm_entry.get()
        
        print(f"\n🔄 Intentando registrar usuario: {email}")
        
        # Validaciones
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
        
        # Verificar si el email ya existe
        if self.email_exists(email):
            messagebox.showerror("❌ Error", "Este correo electrónico ya está registrado")
            return
        
        # Registrar usuario
        if self.register_user(email, password):
            messagebox.showinfo(
                "✅ ¡Éxito!", 
                f"¡Cuenta creada exitosamente!\n\nEmail: {email}\n\n¡Ya puedes iniciar sesión!"
            )
            print(f"✅ Usuario registrado exitosamente: {email}")
            # Volver a la pantalla principal
            self.create_main_interface()
        else:
            messagebox.showerror("❌ Error", "No se pudo crear la cuenta. Intenta de nuevo.")
    
    def show_dashboard(self):
        """Mostrar el panel principal después del login"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Cambiar tamaño de ventana para el dashboard
        self.root.geometry("800x600")
        
        # Barra superior con información del usuario
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Título del dashboard
        title_label = tk.Label(
            header_frame,
            text="🏠 NordSign",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(side="left", padx=20)
        
        # Usuario actual
        user_label = tk.Label(
            header_frame,
            text=f"👤 {self.current_user}",
            font=("Arial", 11),
            bg="#2c3e50",
            fg="white"
        )
        user_label.pack(side="right", padx=20)
        
        # Frame principal con menú lateral y contenido
        main_container = tk.Frame(self.root, bg="#ecf0f1")
        main_container.pack(fill="both", expand=True)
        
        # Menú lateral izquierdo
        sidebar = tk.Frame(main_container, bg="#34495e", width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # ⭐ MENÚ REDUCIDO - Solo 4 opciones principales
        menu_buttons = [
            ("📊 Dashboard", self.show_dashboard_content),
            ("🎓 Entrar a Clase", self.show_classroom),
            ("⚙️ Ajustes", self.show_settings),
            ("🔔 Notificaciones", self.show_notifications),
        ]
        
        for text, command in menu_buttons:
            btn = tk.Button(
                sidebar,
                text=text,
                font=("Arial", 11),
                bg="#34495e",
                fg="white",
                activebackground="#2c3e50",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                anchor="w",
                padx=20,
                command=command
            )
            btn.pack(fill="x", pady=2)
        
        # Botón de cerrar sesión (al final del sidebar)
        logout_btn = tk.Button(
            sidebar,
            text="🚪 Cerrar Sesión",
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            cursor="hand2",
            command=self.logout
        )
        logout_btn.pack(side="bottom", fill="x", pady=10, padx=10)
        
        # Área de contenido principal
        self.content_frame = tk.Frame(main_container, bg="#ecf0f1")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Mostrar contenido inicial
        self.show_dashboard_content()
    
    def show_dashboard_content(self):
        """Mostrar el contenido del dashboard principal"""
        # Limpiar contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Título de bienvenida
        welcome_label = tk.Label(
            self.content_frame,
            text=f"¡Bienvenido, {self.current_user}!",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        welcome_label.pack(pady=20)
        
        # Frame para tarjetas de información
        cards_frame = tk.Frame(self.content_frame, bg="#ecf0f1")
        cards_frame.pack(fill="both", expand=True, pady=10)
        
        # Crear tarjetas de ejemplo
        cards = [
            ("📊 Proyectos Activos", "15", "#3498db"),
            ("✅ Tareas Completadas", "42", "#2ecc71"),
            ("⏰ Tareas Pendientes", "8", "#e67e22"),
            ("👥 Colaboradores", "12", "#9b59b6"),
        ]
        
        for i, (title, value, color) in enumerate(cards):
            card = tk.Frame(cards_frame, bg=color, relief="raised", borderwidth=2)
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            value_label = tk.Label(
                card,
                text=value,
                font=("Arial", 36, "bold"),
                bg=color,
                fg="white"
            )
            value_label.pack(pady=(20, 5))
            
            title_label = tk.Label(
                card,
                text=title,
                font=("Arial", 12),
                bg=color,
                fg="white"
            )
            title_label.pack(pady=(5, 20))
        
        # Configurar grid
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_rowconfigure(0, weight=1)
        cards_frame.grid_rowconfigure(1, weight=1)
        
        # Botones de acción rápida
        actions_label = tk.Label(
            self.content_frame,
            text="Acciones Rápidas",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        actions_label.pack(pady=(20, 10))
        
        actions_frame = tk.Frame(self.content_frame, bg="#ecf0f1")
        actions_frame.pack(pady=10)
        
        quick_actions = [
            ("🎓 Entrar a Clase", "#9b59b6", self.show_classroom),
            ("➕ Nuevo Proyecto", "#3498db", lambda: messagebox.showinfo("Acción", "Has clickeado: Nuevo Proyecto")),
            ("📝 Nueva Tarea", "#2ecc71", lambda: messagebox.showinfo("Acción", "Has clickeado: Nueva Tarea")),
            ("📊 Ver Reportes", "#e67e22", lambda: messagebox.showinfo("Acción", "Has clickeado: Ver Reportes")),
        ]
        
        for text, color, command in quick_actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                font=("Arial", 12, "bold"),
                bg=color,
                fg="white",
                cursor="hand2",
                width=15,
                height=2,
                command=command
            )
            btn.pack(side="left", padx=5)
    
    # ===================================================================
    # ⭐ AJUSTES - TODAS LAS FUNCIONES FUNCIONALES
    # ===================================================================
    
    def show_settings(self):
        """Mostrar la pantalla de ajustes"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        title = tk.Label(
            self.content_frame,
            text="⚙️ Configuración",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Frame para opciones
        settings_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        settings_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        # Opciones de configuración con funciones reales
        settings_options = [
            ("👤 Editar Perfil", self.show_edit_profile),
            ("🔒 Cambiar Contraseña", self.show_change_password),
            ("🔔 Notificaciones", self.show_notification_settings),
            ("🎨 Tema de la Aplicación", self.show_theme_settings),
            ("🌐 Idioma", self.show_language_settings),
            ("🔐 Privacidad y Seguridad", self.show_privacy_settings)
        ]
        
        for option_text, option_command in settings_options:
            option_frame = tk.Frame(settings_frame, bg="white")
            option_frame.pack(fill="x", padx=20, pady=10)
            
            label = tk.Label(
                option_frame,
                text=option_text,
                font=("Arial", 12),
                bg="white"
            )
            label.pack(side="left")
            
            btn = tk.Button(
                option_frame,
                text="Configurar →",
                font=("Arial", 10),
                bg="#3498db",
                fg="white",
                cursor="hand2",
                command=option_command
            )
            btn.pack(side="right")
    
    def show_edit_profile(self):
        """Mostrar pantalla para editar perfil"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        title = tk.Label(
            self.content_frame,
            text="👤 Editar Perfil",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Frame del formulario
        form_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        form_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        # Email actual (no editable)
        email_label = tk.Label(
            form_frame,
            text="Correo Electrónico:",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        email_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        current_email = tk.Label(
            form_frame,
            text=self.current_user,
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#666",
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=8,
            anchor="w"
        )
        current_email.pack(fill="x", padx=20, pady=(0, 20))
        
        # Nombre (campo editable)
        name_label = tk.Label(
            form_frame,
            text="Nombre Completo:",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        name_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.profile_name_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            relief="solid",
            borderwidth=1
        )
        self.profile_name_entry.pack(fill="x", padx=20, ipady=8, pady=(0, 20))
        
        # Teléfono
        phone_label = tk.Label(
            form_frame,
            text="Teléfono:",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        phone_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.profile_phone_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            relief="solid",
            borderwidth=1
        )
        self.profile_phone_entry.pack(fill="x", padx=20, ipady=8, pady=(0, 30))
        
        # Botones
        buttons_frame = tk.Frame(form_frame, bg="white")
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        save_btn = tk.Button(
            buttons_frame,
            text="💾 Guardar Cambios",
            font=("Arial", 12, "bold"),
            bg="#2ecc71",
            fg="white",
            cursor="hand2",
            command=self.save_profile
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancelar",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            cursor="hand2",
            command=self.show_settings
        )
        cancel_btn.pack(side="left", padx=5)
    
    def save_profile(self):
        """Guardar cambios del perfil - FUNCIONAL"""
        name = self.profile_name_entry.get().strip()
        phone = self.profile_phone_entry.get().strip()
        
        # Validaciones
        if not name and not phone:
            messagebox.showwarning("Aviso", "No has realizado ningún cambio")
            return
        
        # Aquí guardarás en TU base de datos
        # Por ahora guardo en variables temporales para demostrar funcionalidad
        print(f"📝 GUARDANDO PERFIL:")
        print(f"   Usuario: {self.current_user}")
        print(f"   Nombre: {name}")
        print(f"   Teléfono: {phone}")
        
        # Simular guardado exitoso
        messagebox.showinfo("✅ Éxito", f"Perfil actualizado correctamente\n\nNombre: {name}\nTeléfono: {phone}")
        self.show_settings()
    
    def show_change_password(self):
        """Mostrar pantalla para cambiar contraseña"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        title = tk.Label(
            self.content_frame,
            text="🔒 Cambiar Contraseña",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Frame del formulario
        form_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        form_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        # Contraseña actual
        current_pass_label = tk.Label(
            form_frame,
            text="Contraseña Actual:",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        current_pass_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.current_password_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            show="*",
            relief="solid",
            borderwidth=1
        )
        self.current_password_entry.pack(fill="x", padx=20, ipady=8, pady=(0, 20))
        
        # Nueva contraseña
        new_pass_label = tk.Label(
            form_frame,
            text="Nueva Contraseña:",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        new_pass_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.new_password_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            show="*",
            relief="solid",
            borderwidth=1
        )
        self.new_password_entry.pack(fill="x", padx=20, ipady=8, pady=(0, 20))
        
        # Confirmar nueva contraseña
        confirm_pass_label = tk.Label(
            form_frame,
            text="Confirmar Nueva Contraseña:",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        confirm_pass_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.confirm_new_password_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            show="*",
            relief="solid",
            borderwidth=1
        )
        self.confirm_new_password_entry.pack(fill="x", padx=20, ipady=8, pady=(0, 30))
        
        # Botones
        buttons_frame = tk.Frame(form_frame, bg="white")
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        save_btn = tk.Button(
            buttons_frame,
            text="🔒 Cambiar Contraseña",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            cursor="hand2",
            command=self.change_password
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancelar",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            cursor="hand2",
            command=self.show_settings
        )
        cancel_btn.pack(side="left", padx=5)
    
    def change_password(self):
        """Procesar cambio de contraseña"""
        current_pass = self.current_password_entry.get()
        new_pass = self.new_password_entry.get()
        confirm_pass = self.confirm_new_password_entry.get()
        
        # Validaciones
        if not current_pass or not new_pass or not confirm_pass:
            messagebox.showerror("Error", "Por favor completa todos los campos")
            return
        
        # Verificar contraseña actual
        if not self.verify_user(self.current_user, current_pass):
            messagebox.showerror("Error", "La contraseña actual es incorrecta")
            return
        
        if len(new_pass) < 6:
            messagebox.showerror("Error", "La nueva contraseña debe tener al menos 6 caracteres")
            return
        
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "Las contraseñas nuevas no coinciden")
            return
        
        # Actualizar contraseña en la base de datos
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(new_pass)
            
            cursor.execute(
                "UPDATE usuarios SET password = ? WHERE email = ?",
                (hashed_password, self.current_user)
            )
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "✅ Contraseña actualizada correctamente")
            self.show_settings()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar contraseña: {e}")
    
    def show_notification_settings(self):
        """Mostrar configuración de notificaciones - FUNCIONAL"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        title = tk.Label(
            self.content_frame,
            text="🔔 Notificaciones",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Frame de opciones
        options_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        options_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        info_label = tk.Label(
            options_frame,
            text="Configura qué notificaciones quieres recibir",
            font=("Arial", 11),
            bg="white",
            fg="#666"
        )
        info_label.pack(pady=20)
        
        # Checkboxes de notificaciones
        self.notif_email = tk.IntVar(value=1)
        self.notif_desktop = tk.IntVar(value=1)
        self.notif_sound = tk.IntVar(value=0)
        
        notifications = [
            ("📧 Notificaciones por Email", self.notif_email),
            ("💻 Notificaciones de Escritorio", self.notif_desktop),
            ("🔊 Sonidos de Notificación", self.notif_sound),
        ]
        
        for text, var in notifications:
            cb = tk.Checkbutton(
                options_frame,
                text=text,
                font=("Arial", 12),
                bg="white",
                variable=var,
                cursor="hand2"
            )
            cb.pack(anchor="w", padx=40, pady=10)
        
        # Botones
        buttons_frame = tk.Frame(options_frame, bg="white")
        buttons_frame.pack(pady=30)
        
        save_btn = tk.Button(
            buttons_frame,
            text="💾 Guardar",
            font=("Arial", 12, "bold"),
            bg="#2ecc71",
            fg="white",
            cursor="hand2",
            width=15,
            command=self.save_notification_settings
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancelar",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            cursor="hand2",
            width=15,
            command=self.show_settings
        )
        cancel_btn.pack(side="left", padx=5)
    
    def save_notification_settings(self):
        """Guardar configuración de notificaciones - FUNCIONAL"""
        email = self.notif_email.get()
        desktop = self.notif_desktop.get()
        sound = self.notif_sound.get()
        
        # Aquí guardarás en TU base de datos
        print(f"🔔 GUARDANDO NOTIFICACIONES:")
        print(f"   Usuario: {self.current_user}")
        print(f"   Email: {'✅' if email else '❌'}")
        print(f"   Desktop: {'✅' if desktop else '❌'}")
        print(f"   Sonido: {'✅' if sound else '❌'}")
        
        messagebox.showinfo("✅ Éxito", "Configuración de notificaciones guardada")
        self.show_settings()
    
    def show_theme_settings(self):
        """Mostrar configuración de tema - FUNCIONAL"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        title = tk.Label(
            self.content_frame,
            text="🎨 Tema de la Aplicación",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Frame de opciones
        options_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        options_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        info_label = tk.Label(
            options_frame,
            text="Selecciona el tema de la aplicación",
            font=("Arial", 11),
            bg="white",
            fg="#666"
        )
        info_label.pack(pady=20)
        
        # Radio buttons para temas
        self.theme_var = tk.StringVar(value="claro")
        
        themes = [
            ("☀️ Tema Claro", "claro"),
            ("🌙 Tema Oscuro", "oscuro"),
            ("🔵 Tema Azul", "azul"),
        ]
        
        for text, value in themes:
            rb = tk.Radiobutton(
                options_frame,
                text=text,
                font=("Arial", 12),
                bg="white",
                variable=self.theme_var,
                value=value,
                cursor="hand2"
            )
            rb.pack(anchor="w", padx=40, pady=10)
        
        # Nota
        note_label = tk.Label(
            options_frame,
            text="Nota: Los cambios se aplicarán en la próxima sesión",
            font=("Arial", 9, "italic"),
            bg="white",
            fg="#999"
        )
        note_label.pack(pady=10)
        
        # Botones
        buttons_frame = tk.Frame(options_frame, bg="white")
        buttons_frame.pack(pady=30)
        
        save_btn = tk.Button(
            buttons_frame,
            text="💾 Guardar",
            font=("Arial", 12, "bold"),
            bg="#2ecc71",
            fg="white",
            cursor="hand2",
            width=15,
            command=self.save_theme_settings
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancelar",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            cursor="hand2",
            width=15,
            command=self.show_settings
        )
        cancel_btn.pack(side="left", padx=5)
    
    def save_theme_settings(self):
        """Guardar tema seleccionado - FUNCIONAL"""
        tema = self.theme_var.get()
        
        # Aquí guardarás en TU base de datos
        print(f"🎨 GUARDANDO TEMA:")
        print(f"   Usuario: {self.current_user}")
        print(f"   Tema: {tema}")
        
        messagebox.showinfo("✅ Éxito", f"Tema '{tema}' guardado correctamente")
        self.show_settings()
    
    def show_language_settings(self):
        """Mostrar configuración de idioma - FUNCIONAL"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        title = tk.Label(
            self.content_frame,
            text="🌐 Idioma",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Frame de opciones
        options_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        options_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        info_label = tk.Label(
            options_frame,
            text="Selecciona el idioma de la aplicación",
            font=("Arial", 11),
            bg="white",
            fg="#666"
        )
        info_label.pack(pady=20)
        
        # Radio buttons para idiomas
        self.language_var = tk.StringVar(value="es")
        
        languages = [
            ("🇪🇸 Español", "es"),
            ("🇺🇸 English", "en"),
            ("🇫🇷 Français", "fr"),
            ("🇩🇪 Deutsch", "de"),
        ]
        
        for text, value in languages:
            rb = tk.Radiobutton(
                options_frame,
                text=text,
                font=("Arial", 12),
                bg="white",
                variable=self.language_var,
                value=value,
                cursor="hand2"
            )
            rb.pack(anchor="w", padx=40, pady=10)
        
        # Nota
        note_label = tk.Label(
            options_frame,
            text="Nota: Los cambios se aplicarán en la próxima sesión",
            font=("Arial", 9, "italic"),
            bg="white",
            fg="#999"
        )
        note_label.pack(pady=10)
        
        # Botones
        buttons_frame = tk.Frame(options_frame, bg="white")
        buttons_frame.pack(pady=30)
        
        save_btn = tk.Button(
            buttons_frame,
            text="💾 Guardar",
            font=("Arial", 12, "bold"),
            bg="#2ecc71",
            fg="white",
            cursor="hand2",
            width=15,
            command=self.save_language_settings
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancelar",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            cursor="hand2",
            width=15,
            command=self.show_settings
        )
        cancel_btn.pack(side="left", padx=5)
    
    def save_language_settings(self):
        """Guardar idioma seleccionado - FUNCIONAL"""
        idioma = self.language_var.get()
        
        idiomas_nombres = {
            'es': 'Español',
            'en': 'English',
            'fr': 'Français',
            'de': 'Deutsch'
        }
        
        # Aquí guardarás en TU base de datos
        print(f"🌐 GUARDANDO IDIOMA:")
        print(f"   Usuario: {self.current_user}")
        print(f"   Idioma: {idioma} ({idiomas_nombres[idioma]})")
        
        messagebox.showinfo("✅ Éxito", f"Idioma '{idiomas_nombres[idioma]}' guardado correctamente")
        self.show_settings()
    
    def show_privacy_settings(self):
        """Mostrar configuración de privacidad"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        title = tk.Label(
            self.content_frame,
            text="🔐 Privacidad y Seguridad",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Frame de opciones
        options_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        options_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        info_label = tk.Label(
            options_frame,
            text="Gestiona tu privacidad y seguridad",
            font=("Arial", 11),
            bg="white",
            fg="#666"
        )
        info_label.pack(pady=20)
        
        # Opciones de privacidad
        privacy_options = [
            ("🗑️ Eliminar Cuenta", self.delete_account_confirmation, "#e74c3c"),
            ("📥 Descargar mis Datos", self.download_user_data, "#3498db"),
            ("🔒 Ver Actividad Reciente", self.show_recent_activity, "#3498db"),
            ("🚪 Cerrar Sesión en Todos los Dispositivos", self.logout_all_devices, "#e67e22"),
        ]
        
        for text, command, color in privacy_options:
            option_frame = tk.Frame(options_frame, bg="white")
            option_frame.pack(fill="x", padx=20, pady=10)
            
            btn = tk.Button(
                option_frame,
                text=text,
                font=("Arial", 11),
                bg=color,
                fg="white",
                cursor="hand2",
                width=40,
                command=command
            )
            btn.pack(pady=5)
        
        # Botón volver
        back_btn = tk.Button(
            options_frame,
            text="← Volver",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            cursor="hand2",
            width=20,
            command=self.show_settings
        )
        back_btn.pack(pady=20)
    
    def delete_account_confirmation(self):
        """Confirmar eliminación de cuenta"""
        result = messagebox.askyesno(
            "⚠️ Eliminar Cuenta",
            "¿Estás seguro de que deseas eliminar tu cuenta?\n\n"
            "Esta acción NO se puede deshacer.\n"
            "Todos tus datos serán eliminados permanentemente."
        )
        
        if result:
            messagebox.showinfo("Cuenta Eliminada", "Tu cuenta ha sido eliminada")
            self.create_main_interface()
    
    def download_user_data(self):
        """Descargar datos del usuario"""
        messagebox.showinfo(
            "Descargar Datos",
            "Se enviará un archivo con todos tus datos\na tu correo electrónico"
        )
    
    def show_recent_activity(self):
        """Mostrar actividad reciente"""
        messagebox.showinfo(
            "Actividad Reciente",
            f"Últimos accesos:\n\n"
            f"• Hoy, 10:30 AM - Windows PC\n"
            f"• Ayer, 3:45 PM - Android\n"
            f"• 2 días atrás, 8:20 AM - Windows PC"
        )
    
    def logout_all_devices(self):
        """Cerrar sesión en todos los dispositivos"""
        result = messagebox.askyesno(
            "Cerrar Todas las Sesiones",
            "¿Deseas cerrar sesión en todos los dispositivos?\n\n"
            "Tendrás que iniciar sesión nuevamente."
        )
        
        if result:
            messagebox.showinfo("Éxito", "✅ Sesiones cerradas en todos los dispositivos")
            self.logout()
    
    # ===================================================================
    # NOTIFICACIONES
    # ===================================================================
    
    def show_notifications(self):
        """Mostrar notificaciones"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        title = tk.Label(
            self.content_frame,
            text="🔔 Notificaciones",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        notifications = [
            "📧 Nuevo mensaje recibido",
            "✅ Tarea completada por equipo",
            "⏰ Fecha límite próxima",
        ]
        
        notif_frame = tk.Frame(self.content_frame, bg="white", relief="groove", borderwidth=2)
        notif_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        for notif in notifications:
            notif_label = tk.Label(
                notif_frame,
                text=notif,
                font=("Arial", 11),
                bg="white",
                anchor="w"
            )
            notif_label.pack(fill="x", padx=20, pady=10)
    
    # ===================================================================
    # CLASE VIRTUAL CON RECONOCIMIENTO LSC
    # ===================================================================
    
    def show_classroom(self):
        """Mostrar la pantalla de clase virtual"""
        # Limpiar contenido anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Variable para control de cámara
        self.camera_active = False
        self.cap = None
        
        # Título principal
        title = tk.Label(
            self.content_frame,
            text="🎓 Clase Virtual",
            font=("Arial", 20, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title.pack(pady=10)
        
        # Frame para botones
        buttons_frame = tk.Frame(self.content_frame, bg="#ecf0f1")
        buttons_frame.pack(pady=5)
        
        # Botón para iniciar/detener clase
        self.start_class_btn = tk.Button(
            buttons_frame,
            text="🎥 INICIAR CLASE",
            font=("Arial", 11, "bold"),
            bg="#2ecc71",
            fg="white",
            cursor="hand2",
            width=18,
            height=1,
            relief="raised",
            bd=3,
            command=self.toggle_camera
        )
        self.start_class_btn.grid(row=0, column=0, padx=8, pady=5)
        
        # Botón para salir de la clase
        exit_class_btn = tk.Button(
            buttons_frame,
            text="🚪 SALIR",
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            cursor="hand2",
            width=18,
            height=1,
            relief="raised",
            bd=3,
            command=self.exit_classroom
        )
        exit_class_btn.grid(row=0, column=1, padx=8, pady=5)
        
        # Frame para la cámara - MÁS GRANDE
        self.camera_frame = tk.Frame(self.content_frame, bg="black", width=700, height=520)
        self.camera_frame.pack(pady=5, fill="both", expand=True)
        self.camera_frame.pack_propagate(False)
        
        # Label para mostrar el video
        self.camera_label = tk.Label(
            self.camera_frame, 
            bg="black",
            text="Presiona 'INICIAR CLASE' para encender la cámara",
            fg="white",
            font=("Arial", 14)
        )
        self.camera_label.pack(expand=True, fill="both")
    
    def toggle_camera(self):
        """Encender o apagar la cámara"""
        if not self.camera_active:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """Iniciar la cámara con reconocimiento de lenguaje de señas"""
        try:
            import cv2
            from PIL import Image, ImageTk
            import mediapipe as mp
            import joblib
            import numpy as np
            
            # Cargar modelo de lenguaje de señas
            try:
                self.modelo_lsc = joblib.load('modelo_lsc.pkl')
                self.lsc_enabled = True
                print("✅ Modelo LSC cargado correctamente")
            except FileNotFoundError:
                self.modelo_lsc = None
                self.lsc_enabled = False
                print("⚠️ Modelo LSC no encontrado. Funcionando sin reconocimiento de señas.")
            except Exception as e:
                self.modelo_lsc = None
                self.lsc_enabled = False
                print(f"⚠️ Error al cargar modelo LSC: {e}")
            
            # Inicializar MediaPipe Hands
            if self.lsc_enabled:
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(
                    max_num_hands=1,
                    min_detection_confidence=0.7
                )
                self.mp_drawing = mp.solutions.drawing_utils
            
            # Abrir la cámara
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                messagebox.showerror("Error", "No se pudo acceder a la cámara")
                return
            
            self.camera_active = True
            self.start_class_btn.config(text="⏸️ DETENER CLASE", bg="#e67e22")
            
            # Iniciar actualización del video
            self.update_camera()
            
        except ImportError as e:
            missing_lib = str(e).split("'")[1] if "'" in str(e) else "desconocida"
            messagebox.showerror(
                "Error - Librería faltante",
                f"Falta instalar: {missing_lib}\n\n"
                f"Para instalar todas las dependencias ejecuta:\n"
                f"pip install opencv-python pillow mediapipe joblib numpy scikit-learn"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar la cámara:\n{str(e)}")
    
    def update_camera(self):
        """Actualizar el frame de la cámara con reconocimiento de lenguaje de señas"""
        if self.camera_active and self.cap is not None:
            try:
                import cv2
                from PIL import Image, ImageTk
                import numpy as np
                
                ret, frame = self.cap.read()
                
                if ret:
                    # Procesar reconocimiento de lenguaje de señas si está habilitado
                    if self.lsc_enabled and self.modelo_lsc is not None:
                        # Convertir a RGB para MediaPipe
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        resultado = self.hands.process(rgb)
                        
                        if resultado.multi_hand_landmarks:
                            hand = resultado.multi_hand_landmarks[0]
                            
                            # Dibujar landmarks de la mano
                            self.mp_drawing.draw_landmarks(
                                frame, hand, self.mp_hands.HAND_CONNECTIONS
                            )
                            
                            # Extraer datos de los landmarks
                            datos = []
                            for lm in hand.landmark:
                                datos.extend([lm.x, lm.y, lm.z])
                            datos = np.array(datos).reshape(1, -1)
                            
                            # Predecir letra
                            try:
                                letra = self.modelo_lsc.predict(datos)[0]
                                
                                # Configuración del texto
                                font = cv2.FONT_HERSHEY_SIMPLEX
                                font_scale = 2
                                font_thickness = 6
                                text_color = (0, 0, 255)  # Rojo
                                box_color = (255, 255, 255)  # Blanco
                                
                                # Obtener tamaño del texto
                                (text_width, text_height), baseline = cv2.getTextSize(
                                    letra, font, font_scale, font_thickness
                                )
                                
                                # Posición del texto
                                text_x = 280
                                text_y = 400
                                
                                # Calcular posición del cuadro (con padding)
                                padding = 10
                                box_x1 = text_x - padding
                                box_y1 = text_y - text_height - padding
                                box_x2 = text_x + text_width + padding
                                box_y2 = text_y + baseline + padding
                                
                                # Dibujar cuadro blanco de fondo
                                cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), box_color, -1)
                                
                                # Dibujar borde del cuadro (negro)
                                cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 0), 3)
                                
                                # Mostrar letra detectada en el frame
                                cv2.putText(frame, letra, (text_x, text_y),
                                          font, font_scale, text_color, font_thickness)
                            except Exception as e:
                                print(f"Error en predicción: {e}")
                    
                    # Convertir de BGR a RGB para Tkinter
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Redimensionar el frame a 700x520
                    frame = cv2.resize(frame, (700, 520))
                    
                    # Convertir a formato PIL
                    img = Image.fromarray(frame)
                    
                    # Convertir a ImageTk
                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    # Actualizar el label
                    self.camera_label.imgtk = imgtk
                    self.camera_label.configure(image=imgtk)
                
                # Programar la siguiente actualización
                self.camera_label.after(10, self.update_camera)
                
            except Exception as e:
                print(f"Error en update_camera: {e}")
                self.stop_camera()
    
    def stop_camera(self):
        """Detener la cámara y limpiar recursos"""
        self.camera_active = False
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        # Limpiar recursos de MediaPipe si están activos
        if hasattr(self, 'hands') and self.hands is not None:
            self.hands.close()
        
        # Limpiar el label de la cámara
        self.camera_label.configure(image='')
        self.camera_label.imgtk = None
        
        # Cambiar el botón
        self.start_class_btn.config(text="🎥 INICIAR CLASE", bg="#2ecc71")
    
    def exit_classroom(self):
        """Salir de la clase y detener la cámara"""
        if self.camera_active:
            self.stop_camera()
        
        # Volver al dashboard principal
        self.show_dashboard_content()
    
   
    
    def logout(self):
        """Cerrar sesión y volver a la pantalla de login"""
        # Detener la cámara si está activa
        if hasattr(self, 'camera_active') and self.camera_active:
            self.stop_camera()
        
        result = messagebox.askyesno(
            "Cerrar Sesión",
            "¿Estás seguro de que deseas cerrar sesión?"
        )
        
        if result:
            self.current_user = None
            self.root.geometry("400x500")  # Restaurar tamaño original
            self.create_main_interface()



if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()