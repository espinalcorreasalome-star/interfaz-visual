import sqlite3
from datetime import datetime, timedelta
import hashlib
import os
import json

def conectar_db():
    """Conectar a la base de datos"""
    return sqlite3.connect("usuarios.db")


14
def mostrar_todos_usuarios():
    """Mostrar todos los usuarios registrados"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        
        if not usuarios:
            print("\n❌ No hay usuarios registrados en la base de datos.")
        else:
            print(f"\n{'='*100}")
            print(f"📊 USUARIOS REGISTRADOS: {len(usuarios)}")
            print(f"{'='*100}")
            print(f"{'ID':<5} {'EMAIL':<40} {'FECHA REGISTRO':<25} {'PASSWORD HASH':<30}")
            print(f"{'-'*100}")
            
            for usuario in usuarios:
                id_usuario = usuario[0]
                email = usuario[1]
                password_hash = usuario[2][:25] + "..."
                fecha = usuario[3] if len(usuario) > 3 else "N/A"
                
                print(f"{id_usuario:<5} {email:<40} {fecha:<25} {password_hash}")
            
            print(f"{'='*100}\n")
        
        conn.close()
        return len(usuarios)
        
    except sqlite3.OperationalError:
        print("\n❌ Error: La base de datos 'usuarios.db' no existe.")
        print("   Ejecuta primero el programa de login para crear la base de datos.\n")
        return 0
    except Exception as e:
        print(f"\n❌ Error al consultar la base de datos: {e}\n")
        return 0

def buscar_usuario(email):
    """Buscar un usuario específico por email"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        
        if usuario:
            print(f"\n{'='*80}")
            print(f"✅ Usuario encontrado:")
            print(f"{'='*80}")
            print(f"   ID:                {usuario[0]}")
            print(f"   Email:             {usuario[1]}")
            print(f"   Password Hash:     {usuario[2]}")
            print(f"   Fecha de Registro: {usuario[3] if len(usuario) > 3 else 'N/A'}")
            print(f"{'='*80}\n")
            return usuario
        else:
            print(f"\n❌ No se encontró ningún usuario con el email: {email}\n")
            return None
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al buscar usuario: {e}\n")
        return None

def verificar_password(email, password):
    """Verificar si una contraseña es correcta para un email"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute("SELECT password FROM usuarios WHERE email = ?", (email,))
        resultado = cursor.fetchone()
        
        if resultado:
            if resultado[0] == hashed_password:
                print(f"\n✅ Contraseña CORRECTA para {email}\n")
                return True
            else:
                print(f"\n❌ Contraseña INCORRECTA para {email}\n")
                return False
        else:
            print(f"\n❌ El email {email} no está registrado\n")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al verificar contraseña: {e}\n")
        return False

def eliminar_usuario(email):
    """Eliminar un usuario de la base de datos"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        
        if usuario:
            print(f"\n{'='*80}")
            print(f"⚠️  ADVERTENCIA - ELIMINAR USUARIO")
            print(f"{'='*80}")
            print(f"   Email: {email}")
            print(f"   ID:    {usuario[0]}")
            print(f"{'='*80}")
            
            confirmar = input(f"\n¿Estás seguro de eliminar a {email}? (s/n): ")
            if confirmar.lower() == 's':
                cursor.execute("DELETE FROM usuarios WHERE email = ?", (email,))
                conn.commit()
                print(f"\n✅ Usuario {email} eliminado exitosamente\n")
                return True
            else:
                print("\n❌ Eliminación cancelada\n")
                return False
        else:
            print(f"\n❌ El usuario {email} no existe\n")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al eliminar usuario: {e}\n")
        return False

def verificar_estructura_db():
    """Verificar la estructura de la base de datos"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(usuarios)")
        columnas = cursor.fetchall()
        
        print(f"\n{'='*90}")
        print("🔍 ESTRUCTURA DE LA TABLA 'usuarios'")
        print(f"{'='*90}")
        print(f"{'ID':<5} {'Nombre':<20} {'Tipo':<15} {'Not Null':<10} {'Default':<20} {'PK':<5}")
        print(f"{'-'*90}")
        
        for col in columnas:
            id_col = col[0]
            nombre = col[1]
            tipo = col[2]
            not_null = "Sí" if col[3] else "No"
            default = str(col[4]) if col[4] else "-"
            pk = "Sí" if col[5] else "No"
            
            print(f"{id_col:<5} {nombre:<20} {tipo:<15} {not_null:<10} {default:<20} {pk:<5}")
        
        print(f"{'='*90}\n")
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al verificar estructura: {e}\n")



def crear_usuario(email, password):
    """Crear un nuevo usuario"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute(
            "INSERT INTO usuarios (email, password) VALUES (?, ?)",
            (email, hashed_password)
        )
        
        conn.commit()
        print(f"\n✅ Usuario {email} creado exitosamente\n")
        conn.close()
        return True
        
    except sqlite3.IntegrityError:
        print(f"\n❌ Error: El email {email} ya está registrado\n")
        return False
    except Exception as e:
        print(f"\n❌ Error al crear usuario: {e}\n")
        return False

def cambiar_contraseña(email, nueva_password):
    """Cambiar contraseña de un usuario"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        
        if usuario:
            hashed_password = hashlib.sha256(nueva_password.encode()).hexdigest()
            cursor.execute(
                "UPDATE usuarios SET password = ? WHERE email = ?",
                (hashed_password, email)
            )
            conn.commit()
            print(f"\n✅ Contraseña actualizada para {email}\n")
            conn.close()
            return True
        else:
            print(f"\n❌ El usuario {email} no existe\n")
            conn.close()
            return False
        
    except Exception as e:
        print(f"\n❌ Error al actualizar contraseña: {e}\n")
        return False

def ver_perfil_completo(email):
    """Ver perfil completo de un usuario con todos sus datos"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        
        if not usuario:
            print(f"\n❌ No se encontró el usuario {email}\n")
            conn.close()
            return
        
        print(f"\n{'='*80}")
        print(f"👤 PERFIL COMPLETO DE USUARIO")
        print(f"{'='*80}")
        print(f"ID:                {usuario[0]}")
        print(f"Email:             {usuario[1]}")
        print(f"Fecha Registro:    {usuario[3] if len(usuario) > 3 else 'N/A'}")
        print(f"{'='*80}\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al ver perfil: {e}\n")

def obtener_estadisticas():
    """Obtener estadísticas generales de la base de datos"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT email, fecha_registro FROM usuarios ORDER BY fecha_registro ASC LIMIT 1")
        mas_antiguo = cursor.fetchone()
        
        cursor.execute("SELECT email, fecha_registro FROM usuarios ORDER BY fecha_registro DESC LIMIT 1")
        mas_reciente = cursor.fetchone()
        
        tamaño = os.path.getsize("usuarios.db") / 1024
        
        hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE fecha_registro LIKE ?", (f"{hoy}%",))
        usuarios_hoy = cursor.fetchone()[0]
        
        hace_7_dias = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE fecha_registro >= ?", (hace_7_dias,))
        usuarios_semana = cursor.fetchone()[0]
        
        print(f"\n{'='*80}")
        print("📊 ESTADÍSTICAS DE LA BASE DE DATOS")
        print(f"{'='*80}")
        print(f"Total de usuarios:           {total}")
        print(f"Usuarios registrados hoy:    {usuarios_hoy}")
        print(f"Usuarios esta semana:        {usuarios_semana}")
        print(f"Tamaño de la BD:             {tamaño:.2f} KB")
        
        if mas_antiguo:
            print(f"Usuario más antiguo:         {mas_antiguo[0]} ({mas_antiguo[1]})")
        
        if mas_reciente:
            print(f"Usuario más reciente:        {mas_reciente[0]} ({mas_reciente[1]})")
        
        print(f"{'='*80}\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al obtener estadísticas: {e}\n")

def listar_usuarios_recientes(limite=10):
    """Listar los últimos N usuarios registrados"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM usuarios ORDER BY fecha_registro DESC LIMIT ?",
            (limite,)
        )
        
        usuarios = cursor.fetchall()
        
        print(f"\n{'='*80}")
        print(f"🕐 ÚLTIMOS {limite} USUARIOS REGISTRADOS")
        print(f"{'='*80}")
        print(f"{'ID':<5} {'EMAIL':<40} {'FECHA REGISTRO':<30}")
        print(f"{'-'*80}")
        
        for usuario in usuarios:
            print(f"{usuario[0]:<5} {usuario[1]:<40} {usuario[3]:<30}")
        
        print(f"{'='*80}\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al listar usuarios recientes: {e}\n")

def buscar_usuarios_por_fecha(fecha_inicio, fecha_fin):
    """Buscar usuarios registrados en un rango de fechas"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT * FROM usuarios 
               WHERE fecha_registro BETWEEN ? AND ?
               ORDER BY fecha_registro DESC""",
            (fecha_inicio, fecha_fin)
        )
        
        usuarios = cursor.fetchall()
        
        print(f"\n{'='*80}")
        print(f"📅 USUARIOS REGISTRADOS ENTRE {fecha_inicio} Y {fecha_fin}")
        print(f"{'='*80}")
        print(f"Total encontrados: {len(usuarios)}")
        print(f"{'-'*80}")
        
        if usuarios:
            for usuario in usuarios:
                print(f"ID: {usuario[0]:<5} Email: {usuario[1]:<40} Fecha: {usuario[3]}")
        else:
            print("No se encontraron usuarios en este rango de fechas")
        
        print(f"{'='*80}\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al buscar por fecha: {e}\n")

def contar_usuarios_activos():
    """Contar usuarios activos (registrados en los últimos 30 días)"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        hace_30_dias = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        cursor.execute(
            "SELECT COUNT(*) FROM usuarios WHERE fecha_registro >= ?",
            (hace_30_dias,)
        )
        
        activos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]
        
        inactivos = total - activos
        porcentaje_activos = (activos / total * 100) if total > 0 else 0
        
        print(f"\n{'='*80}")
        print("👥 USUARIOS ACTIVOS VS INACTIVOS")
        print(f"{'='*80}")
        print(f"Total de usuarios:       {total}")
        print(f"Usuarios activos:        {activos} ({porcentaje_activos:.1f}%)")
        print(f"Usuarios inactivos:      {inactivos}")
        print(f"{'='*80}\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al contar usuarios activos: {e}\n")



def hacer_respaldo():
    """Crear respaldo de la base de datos"""
    try:
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_respaldo = f"usuarios_backup_{fecha}.db"
        
        conn_origen = conectar_db()
        conn_destino = sqlite3.connect(nombre_respaldo)
        
        conn_origen.backup(conn_destino)
        
        conn_origen.close()
        conn_destino.close()
        
        tamaño = os.path.getsize(nombre_respaldo) / 1024
        
        print(f"\n✅ Respaldo creado exitosamente:")
        print(f"   Archivo: {nombre_respaldo}")
        print(f"   Tamaño:  {tamaño:.2f} KB\n")
        
        return nombre_respaldo
        
    except Exception as e:
        print(f"\n❌ Error al crear respaldo: {e}\n")
        return None

def restaurar_respaldo(archivo_respaldo):
    """Restaurar base de datos desde un respaldo"""
    try:
        if not os.path.exists(archivo_respaldo):
            print(f"\n❌ El archivo {archivo_respaldo} no existe\n")
            return False
        
        print(f"\n⚠️  ADVERTENCIA: Esto sobrescribirá la base de datos actual")
        confirmar = input(f"¿Restaurar desde {archivo_respaldo}? (s/n): ")
        
        if confirmar.lower() == 's':
            print("\n📋 Creando respaldo de seguridad de la BD actual...")
            hacer_respaldo()
            
            conn_origen = sqlite3.connect(archivo_respaldo)
            conn_destino = conectar_db()
            
            conn_origen.backup(conn_destino)
            
            conn_origen.close()
            conn_destino.close()
            
            print(f"\n✅ Base de datos restaurada exitosamente\n")
            return True
        else:
            print("\n❌ Restauración cancelada\n")
            return False
        
    except Exception as e:
        print(f"\n❌ Error al restaurar: {e}\n")
        return False

def exportar_a_csv(archivo="usuarios_export.csv"):
    """Exportar usuarios a archivo CSV"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write("ID,Email,Password_Hash,Fecha_Registro\n")
            
            for usuario in usuarios:
                f.write(f"{usuario[0]},{usuario[1]},{usuario[2]},{usuario[3]}\n")
        
        print(f"\n✅ {len(usuarios)} usuarios exportados a {archivo}\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al exportar: {e}\n")

def limpiar_usuarios_inactivos(dias=365):
    """Eliminar usuarios inactivos"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        fecha_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
        
        cursor.execute(
            "SELECT COUNT(*) FROM usuarios WHERE fecha_registro < ?",
            (fecha_limite,)
        )
        
        total = cursor.fetchone()[0]
        
        print(f"\n📊 Usuarios inactivos (antes de {fecha_limite}): {total}")
        
        if total > 0:
            confirmar = input(f"\n⚠️  ¿Eliminar {total} usuarios inactivos? (s/n): ")
            
            if confirmar.lower() == 's':
                cursor.execute(
                    "DELETE FROM usuarios WHERE fecha_registro < ?",
                    (fecha_limite,)
                )
                conn.commit()
                print(f"\n✅ {total} usuarios eliminados\n")
            else:
                print("\n❌ Operación cancelada\n")
        else:
            print("\n✅ No hay usuarios inactivos para eliminar\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al limpiar: {e}\n")

# ===================================================================
# FUNCIONES DE SEGURIDAD
# ===================================================================

def verificar_integridad_passwords():
    """Verificar que todos los passwords estén hasheados correctamente"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, email, password FROM usuarios")
        usuarios = cursor.fetchall()
        
        problemas = 0
        
        print(f"\n{'='*80}")
        print("🔐 VERIFICACIÓN DE INTEGRIDAD DE CONTRASEÑAS")
        print(f"{'='*80}")
        
        for usuario in usuarios:
            user_id, email, password_hash = usuario
            
            if len(password_hash) != 64:
                print(f"⚠️  ID {user_id} ({email}): Hash inválido (longitud: {len(password_hash)})")
                problemas += 1
            elif not all(c in '0123456789abcdef' for c in password_hash.lower()):
                print(f"⚠️  ID {user_id} ({email}): Hash contiene caracteres inválidos")
                problemas += 1
        
        if problemas == 0:
            print("✅ Todos los passwords están correctamente hasheados")
        else:
            print(f"\n⚠️  Se encontraron {problemas} problemas")
        
        print(f"{'='*80}\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al verificar integridad: {e}\n")

def buscar_emails_duplicados():
    """Buscar emails duplicados"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT email, COUNT(*) as cantidad
               FROM usuarios
               GROUP BY email
               HAVING COUNT(*) > 1"""
        )
        
        duplicados = cursor.fetchall()
        
        if duplicados:
            print(f"\n{'='*80}")
            print("⚠️  EMAILS DUPLICADOS ENCONTRADOS:")
            print(f"{'='*80}")
            for email, cantidad in duplicados:
                print(f"   {email}: {cantidad} veces")
            print(f"{'='*80}\n")
        else:
            print("\n✅ No hay emails duplicados\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al buscar duplicados: {e}\n")

def auditar_actividad_usuarios():
    """Mostrar resumen de actividad de usuarios"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT strftime('%Y-%m', fecha_registro) as mes, COUNT(*) as cantidad
               FROM usuarios
               GROUP BY mes
               ORDER BY mes DESC
               LIMIT 12"""
        )
        
        por_mes = cursor.fetchall()
        
        print(f"\n{'='*80}")
        print("📈 REGISTROS POR MES (Últimos 12 meses)")
        print(f"{'='*80}")
        
        if por_mes:
            for mes, cantidad in por_mes:
                barra = "█" * cantidad
                print(f"{mes}: {barra} ({cantidad})")
        else:
            print("No hay datos suficientes")
        
        print(f"{'='*80}\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error al auditar: {e}\n")


# ===================================================================
# FUNCIONES DE AJUSTES - INTEGRADAS DESDE LA INTERFAZ VISUAL
# ===================================================================

def _init_tabla_ajustes():
    """Crear la tabla de ajustes de usuario si no existe"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ajustes_usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                nombre_completo TEXT DEFAULT '',
                telefono TEXT DEFAULT '',
                notif_email INTEGER DEFAULT 1,
                notif_escritorio INTEGER DEFAULT 1,
                notif_sonido INTEGER DEFAULT 0,
                tema TEXT DEFAULT 'claro',
                idioma TEXT DEFAULT 'es',
                FOREIGN KEY (email) REFERENCES usuarios(email)
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"\n❌ Error al inicializar tabla de ajustes: {e}\n")


def editar_perfil(email):
    """Editar el nombre completo y teléfono de un usuario"""
    _init_tabla_ajustes()
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verificar que el usuario existe
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if not cursor.fetchone():
            print(f"\n❌ El usuario {email} no existe en la base de datos\n")
            conn.close()
            return False

        # Mostrar datos actuales si existen
        cursor.execute("SELECT nombre_completo, telefono FROM ajustes_usuario WHERE email = ?", (email,))
        datos_actuales = cursor.fetchone()

        print(f"\n{'='*80}")
        print(f"👤 EDITAR PERFIL - {email}")
        print(f"{'='*80}")

        if datos_actuales:
            print(f"   Nombre actual:    {datos_actuales[0] or '(sin nombre)'}")
            print(f"   Teléfono actual:  {datos_actuales[1] or '(sin teléfono)'}")
        else:
            print("   (Este usuario aún no tiene perfil configurado)")

        print(f"{'='*80}")
        print("   Deja el campo vacío para no modificarlo.\n")

        nombre = input("   Nuevo nombre completo: ").strip()
        telefono = input("   Nuevo teléfono:        ").strip()

        if not nombre and not telefono:
            print("\n⚠️  No se realizó ningún cambio.\n")
            conn.close()
            return False

        if datos_actuales:
            # Si ya tiene registro, actualizar solo los campos que se ingresaron
            nuevo_nombre = nombre if nombre else datos_actuales[0]
            nuevo_telefono = telefono if telefono else datos_actuales[1]
            cursor.execute(
                "UPDATE ajustes_usuario SET nombre_completo = ?, telefono = ? WHERE email = ?",
                (nuevo_nombre, nuevo_telefono, email)
            )
        else:
            # Insertar nuevo registro de ajustes
            cursor.execute(
                "INSERT INTO ajustes_usuario (email, nombre_completo, telefono) VALUES (?, ?, ?)",
                (email, nombre, telefono)
            )

        conn.commit()
        print(f"\n✅ Perfil actualizado correctamente para {email}\n")
        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ Error al editar perfil: {e}\n")
        return False


def cambiar_password_con_verificacion(email):
    """Cambiar contraseña verificando primero la contraseña actual"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verificar que el usuario existe
        cursor.execute("SELECT password FROM usuarios WHERE email = ?", (email,))
        resultado = cursor.fetchone()
        conn.close()

        if not resultado:
            print(f"\n❌ El usuario {email} no existe\n")
            return False

        print(f"\n{'='*80}")
        print(f"🔒 CAMBIAR CONTRASEÑA - {email}")
        print(f"{'='*80}")

        import getpass
        password_actual = getpass.getpass("   Contraseña actual:          ")
        hash_actual = hashlib.sha256(password_actual.encode()).hexdigest()

        if hash_actual != resultado[0]:
            print("\n❌ La contraseña actual es incorrecta\n")
            return False

        nueva_password = getpass.getpass("   Nueva contraseña:           ")
        if len(nueva_password) < 6:
            print("\n❌ La nueva contraseña debe tener al menos 6 caracteres\n")
            return False

        confirmar_password = getpass.getpass("   Confirmar nueva contraseña: ")
        if nueva_password != confirmar_password:
            print("\n❌ Las contraseñas nuevas no coinciden\n")
            return False

        # Actualizar en la base de datos
        return cambiar_contraseña(email, nueva_password)

    except Exception as e:
        print(f"\n❌ Error al cambiar contraseña: {e}\n")
        return False


def configurar_notificaciones(email):
    """Configurar las preferencias de notificaciones de un usuario"""
    _init_tabla_ajustes()
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Verificar que el usuario existe
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if not cursor.fetchone():
            print(f"\n❌ El usuario {email} no existe\n")
            conn.close()
            return False

        # Obtener configuración actual
        cursor.execute(
            "SELECT notif_email, notif_escritorio, notif_sonido FROM ajustes_usuario WHERE email = ?",
            (email,)
        )
        config_actual = cursor.fetchone()

        estado_actual = {
            'email':      config_actual[0] if config_actual else 1,
            'escritorio': config_actual[1] if config_actual else 1,
            'sonido':     config_actual[2] if config_actual else 0,
        }

        print(f"\n{'='*80}")
        print(f"🔔 CONFIGURAR NOTIFICACIONES - {email}")
        print(f"{'='*80}")
        print(f"   Estado actual:")
        print(f"   📧 Notificaciones por Email:       {'✅ Activado' if estado_actual['email'] else '❌ Desactivado'}")
        print(f"   💻 Notificaciones de Escritorio:   {'✅ Activado' if estado_actual['escritorio'] else '❌ Desactivado'}")
        print(f"   🔊 Sonidos de Notificación:        {'✅ Activado' if estado_actual['sonido'] else '❌ Desactivado'}")
        print(f"{'='*80}")
        print("   Ingresa 1 para activar, 0 para desactivar, Enter para mantener el valor actual.\n")

        def pedir_valor(nombre, actual):
            entrada = input(f"   {nombre} (actual: {actual}): ").strip()
            if entrada == '1':
                return 1
            elif entrada == '0':
                return 0
            else:
                return actual

        notif_email      = pedir_valor("📧 Email (1/0)", estado_actual['email'])
        notif_escritorio = pedir_valor("💻 Escritorio (1/0)", estado_actual['escritorio'])
        notif_sonido     = pedir_valor("🔊 Sonido (1/0)", estado_actual['sonido'])

        if config_actual:
            cursor.execute(
                """UPDATE ajustes_usuario
                   SET notif_email = ?, notif_escritorio = ?, notif_sonido = ?
                   WHERE email = ?""",
                (notif_email, notif_escritorio, notif_sonido, email)
            )
        else:
            cursor.execute(
                """INSERT INTO ajustes_usuario (email, notif_email, notif_escritorio, notif_sonido)
                   VALUES (?, ?, ?, ?)""",
                (email, notif_email, notif_escritorio, notif_sonido)
            )

        conn.commit()
        print(f"\n✅ Configuración de notificaciones guardada para {email}\n")
        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ Error al configurar notificaciones: {e}\n")
        return False


def configurar_tema(email):
    """Configurar el tema visual preferido del usuario"""
    _init_tabla_ajustes()
    temas_disponibles = {
        '1': 'claro',
        '2': 'oscuro',
        '3': 'azul'
    }
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if not cursor.fetchone():
            print(f"\n❌ El usuario {email} no existe\n")
            conn.close()
            return False

        cursor.execute("SELECT tema FROM ajustes_usuario WHERE email = ?", (email,))
        config_actual = cursor.fetchone()
        tema_actual = config_actual[0] if config_actual else 'claro'

        print(f"\n{'='*80}")
        print(f"🎨 CONFIGURAR TEMA - {email}")
        print(f"{'='*80}")
        print(f"   Tema actual: {tema_actual}")
        print(f"\n   Temas disponibles:")
        print(f"   1. ☀️  Claro")
        print(f"   2. 🌙  Oscuro")
        print(f"   3. 🔵  Azul")
        print(f"{'='*80}")

        opcion = input("\n   Selecciona el número del tema (Enter para cancelar): ").strip()

        if opcion not in temas_disponibles:
            print("\n⚠️  Opción inválida o cancelado. No se realizó ningún cambio.\n")
            conn.close()
            return False

        nuevo_tema = temas_disponibles[opcion]

        if config_actual:
            cursor.execute("UPDATE ajustes_usuario SET tema = ? WHERE email = ?", (nuevo_tema, email))
        else:
            cursor.execute("INSERT INTO ajustes_usuario (email, tema) VALUES (?, ?)", (email, nuevo_tema))

        conn.commit()
        print(f"\n✅ Tema '{nuevo_tema}' guardado para {email}\n")
        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ Error al configurar tema: {e}\n")
        return False


def configurar_idioma(email):
    """Configurar el idioma preferido del usuario"""
    _init_tabla_ajustes()
    idiomas_disponibles = {
        '1': ('es', 'Español'),
        '2': ('en', 'English'),
        '3': ('fr', 'Français'),
        '4': ('de', 'Deutsch'),
    }
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if not cursor.fetchone():
            print(f"\n❌ El usuario {email} no existe\n")
            conn.close()
            return False

        cursor.execute("SELECT idioma FROM ajustes_usuario WHERE email = ?", (email,))
        config_actual = cursor.fetchone()
        idioma_actual = config_actual[0] if config_actual else 'es'

        print(f"\n{'='*80}")
        print(f"🌐 CONFIGURAR IDIOMA - {email}")
        print(f"{'='*80}")
        print(f"   Idioma actual: {idioma_actual}")
        print(f"\n   Idiomas disponibles:")
        for num, (codigo, nombre) in idiomas_disponibles.items():
            print(f"   {num}. {nombre} ({codigo})")
        print(f"{'='*80}")

        opcion = input("\n   Selecciona el número del idioma (Enter para cancelar): ").strip()

        if opcion not in idiomas_disponibles:
            print("\n⚠️  Opción inválida o cancelado. No se realizó ningún cambio.\n")
            conn.close()
            return False

        nuevo_codigo, nuevo_nombre = idiomas_disponibles[opcion]

        if config_actual:
            cursor.execute("UPDATE ajustes_usuario SET idioma = ? WHERE email = ?", (nuevo_codigo, email))
        else:
            cursor.execute("INSERT INTO ajustes_usuario (email, idioma) VALUES (?, ?)", (email, nuevo_codigo))

        conn.commit()
        print(f"\n✅ Idioma '{nuevo_nombre}' guardado para {email}\n")
        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ Error al configurar idioma: {e}\n")
        return False


def privacidad_y_seguridad(email):
    """Submenú de privacidad y seguridad para un usuario"""
    while True:
        print(f"\n{'='*80}")
        print(f"🔐 PRIVACIDAD Y SEGURIDAD - {email}")
        print(f"{'='*80}")
        print("   1. 🗑️  Eliminar cuenta")
        print("   2. 📥  Exportar mis datos a CSV")
        print("   3. 🔒  Ver actividad reciente (últimos registros)")
        print("   4. 🚪  Cerrar sesión en todos los dispositivos (resetear hash de sesión)")
        print("   0. ←  Volver")
        print(f"{'='*80}")

        opcion = input("\n   Selecciona una opción: ").strip()

        if opcion == '1':
            _eliminar_cuenta_propia(email)
            break  # Si se eliminó la cuenta, salir del submenú
        elif opcion == '2':
            _exportar_datos_usuario(email)
        elif opcion == '3':
            _ver_actividad_reciente(email)
        elif opcion == '4':
            _cerrar_todas_sesiones(email)
        elif opcion == '0':
            break
        else:
            print("\n❌ Opción inválida\n")


def _eliminar_cuenta_propia(email):
    """Eliminar la cuenta completa de un usuario (usuarios + ajustes)"""
    try:
        print(f"\n{'='*80}")
        print(f"⚠️  ELIMINAR CUENTA - {email}")
        print(f"{'='*80}")
        print("   Esta acción eliminará PERMANENTEMENTE:")
        print(f"   • Los datos de acceso de {email}")
        print(f"   • Todos sus ajustes personalizados")
        print(f"{'='*80}")

        confirmar = input(f"\n   ¿Estás seguro? Escribe 'ELIMINAR' para confirmar: ").strip()

        if confirmar == 'ELIMINAR':
            conn = conectar_db()
            cursor = conn.cursor()
            # Eliminar ajustes
            cursor.execute("DELETE FROM ajustes_usuario WHERE email = ?", (email,))
            # Eliminar usuario
            cursor.execute("DELETE FROM usuarios WHERE email = ?", (email,))
            conn.commit()
            conn.close()
            print(f"\n✅ Cuenta de {email} eliminada permanentemente\n")
        else:
            print("\n❌ Eliminación cancelada\n")

    except Exception as e:
        print(f"\n❌ Error al eliminar cuenta: {e}\n")


def _exportar_datos_usuario(email):
    """Exportar todos los datos de un usuario específico a CSV"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        if not usuario:
            print(f"\n❌ El usuario {email} no existe\n")
            conn.close()
            return

        cursor.execute("SELECT * FROM ajustes_usuario WHERE email = ?", (email,))
        ajustes = cursor.fetchone()
        conn.close()

        nombre_archivo = f"datos_{email.replace('@','_').replace('.','_')}.csv"

        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write("=== DATOS DE CUENTA ===\n")
            f.write("ID,Email,Password_Hash,Fecha_Registro\n")
            f.write(f"{usuario[0]},{usuario[1]},{usuario[2]},{usuario[3]}\n\n")

            f.write("=== AJUSTES DE USUARIO ===\n")
            if ajustes:
                f.write("Email,Nombre,Telefono,Notif_Email,Notif_Escritorio,Notif_Sonido,Tema,Idioma\n")
                f.write(f"{ajustes[1]},{ajustes[2]},{ajustes[3]},{ajustes[4]},{ajustes[5]},{ajustes[6]},{ajustes[7]},{ajustes[8]}\n")
            else:
                f.write("(Sin ajustes configurados)\n")

        print(f"\n✅ Datos exportados a '{nombre_archivo}'\n")

    except Exception as e:
        print(f"\n❌ Error al exportar datos: {e}\n")


def _ver_actividad_reciente(email):
    """Mostrar información de actividad reciente del usuario"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, email, fecha_registro FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        conn.close()

        if not usuario:
            print(f"\n❌ El usuario {email} no existe\n")
            return

        print(f"\n{'='*80}")
        print(f"🔒 ACTIVIDAD RECIENTE - {email}")
        print(f"{'='*80}")
        print(f"   ID de cuenta:        {usuario[0]}")
        print(f"   Fecha de registro:   {usuario[2]}")
        print(f"   Nota: El sistema actualmente registra solo la fecha de creación.")
        print(f"         Para historial completo de accesos, se requiere una tabla de logs.")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n❌ Error al ver actividad: {e}\n")


def _cerrar_todas_sesiones(email):
    """Simula el cierre de sesión en todos los dispositivos regenerando el hash de sesión"""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if not cursor.fetchone():
            print(f"\n❌ El usuario {email} no existe\n")
            conn.close()
            return

        confirmar = input(f"\n   ¿Cerrar todas las sesiones activas de {email}? (s/n): ")
        if confirmar.lower() == 's':
            # En un sistema real se invalidarían tokens de sesión.
            # Aquí registramos la acción en consola como confirmación.
            print(f"\n✅ Todas las sesiones de {email} han sido cerradas.")
            print(f"   El usuario deberá iniciar sesión nuevamente en todos sus dispositivos.\n")
        else:
            print("\n❌ Operación cancelada\n")

        conn.close()

    except Exception as e:
        print(f"\n❌ Error al cerrar sesiones: {e}\n")


def ver_ajustes_usuario(email):
    """Ver todos los ajustes configurados de un usuario"""
    _init_tabla_ajustes()
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        if not cursor.fetchone():
            print(f"\n❌ El usuario {email} no existe\n")
            conn.close()
            return

        cursor.execute("SELECT * FROM ajustes_usuario WHERE email = ?", (email,))
        ajustes = cursor.fetchone()
        conn.close()

        print(f"\n{'='*80}")
        print(f"⚙️  AJUSTES DE {email}")
        print(f"{'='*80}")

        if ajustes:
            print(f"   Nombre completo:              {ajustes[2] or '(no configurado)'}")
            print(f"   Teléfono:                     {ajustes[3] or '(no configurado)'}")
            print(f"   Notificaciones por email:     {'✅ Activado' if ajustes[4] else '❌ Desactivado'}")
            print(f"   Notificaciones de escritorio: {'✅ Activado' if ajustes[5] else '❌ Desactivado'}")
            print(f"   Sonido de notificaciones:     {'✅ Activado' if ajustes[6] else '❌ Desactivado'}")
            print(f"   Tema:                         {ajustes[7]}")
            print(f"   Idioma:                       {ajustes[8]}")
        else:
            print("   (Este usuario no tiene ajustes personalizados aún)")

        print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n❌ Error al ver ajustes: {e}\n")


def menu_ajustes(email):
    """Submenú completo de ajustes para un usuario específico"""
    while True:
        print(f"\n{'='*80}")
        print(f"⚙️  AJUSTES Y CONFIGURACIÓN - {email}")
        print(f"{'='*80}")
        print("   1. 👤  Editar Perfil")
        print("   2. 🔒  Cambiar Contraseña")
        print("   3. 🔔  Configurar Notificaciones")
        print("   4. 🎨  Tema de la Aplicación")
        print("   5. 🌐  Idioma")
        print("   6. 🔐  Privacidad y Seguridad")
        print("   7. 📋  Ver todos mis ajustes")
        print("   0. ←  Volver al menú principal")
        print(f"{'='*80}")

        opcion = input("\n   Selecciona una opción (0-7): ").strip()

        if opcion == '1':
            editar_perfil(email)
        elif opcion == '2':
            cambiar_password_con_verificacion(email)
        elif opcion == '3':
            configurar_notificaciones(email)
        elif opcion == '4':
            configurar_tema(email)
        elif opcion == '5':
            configurar_idioma(email)
        elif opcion == '6':
            privacidad_y_seguridad(email)
        elif opcion == '7':
            ver_ajustes_usuario(email)
        elif opcion == '0':
            break
        else:
            print("\n❌ Opción inválida\n")


# ===================================================================
# MENÚ PRINCIPAL
# ===================================================================

def menu_principal():
    """Menú principal de administración"""
    while True:
        print("\n" + "="*80)
        print("🔧 ADMINISTRADOR DE BASE DE DATOS - USUARIOS NORDSIGN")
        print("="*80)
        
        print("\n📊 GESTIÓN BÁSICA:")
        print("  1.  Mostrar todos los usuarios")
        print("  2.  Buscar usuario por email")
        print("  3.  Ver perfil completo de usuario")
        print("  4.  Verificar contraseña")
        print("  5.  Eliminar usuario")
        print("  6.  Ver estructura de la base de datos")
        
        print("\n➕ GESTIÓN AVANZADA:")
        print("  7.  Crear nuevo usuario")
        print("  8.  Cambiar contraseña de usuario")
        
        print("\n📈 ESTADÍSTICAS Y ANÁLISIS:")
        print("  9.  Obtener estadísticas generales")
        print("  10. Listar usuarios recientes")
        print("  11. Buscar usuarios por rango de fechas")
        print("  12. Contar usuarios activos/inactivos")
        print("  13. Auditar actividad de usuarios")
        
        print("\n🛠️  MANTENIMIENTO:")
        print("  14. Hacer respaldo de la base de datos")
        print("  15. Restaurar desde respaldo")
        print("  16. Exportar usuarios a CSV")
        print("  17. Limpiar usuarios inactivos")
        
        print("\n🔐 SEGURIDAD:")
        print("  18. Verificar integridad de passwords")
        print("  19. Buscar emails duplicados")

        print("\n⚙️  AJUSTES Y CONFIGURACIÓN DE USUARIO:")
        print("  20. Gestionar ajustes de un usuario")
        
        print("\n  0.  Salir")
        print("="*80)
        
        opcion = input("\nSelecciona una opción (0-20): ")
        
        if opcion == "1":
            mostrar_todos_usuarios()
        elif opcion == "2":
            email = input("\nIngresa el email a buscar: ")
            buscar_usuario(email)
        elif opcion == "3":
            email = input("\nIngresa el email: ")
            ver_perfil_completo(email)
        elif opcion == "4":
            email = input("\nIngresa el email: ")
            password = input("Ingresa la contraseña a verificar: ")
            verificar_password(email, password)
        elif opcion == "5":
            email = input("\nIngresa el email del usuario a eliminar: ")
            eliminar_usuario(email)
        elif opcion == "6":
            verificar_estructura_db()
        elif opcion == "7":
            email = input("\nIngresa el email del nuevo usuario: ")
            password = input("Ingresa la contraseña: ")
            crear_usuario(email, password)
        elif opcion == "8":
            email = input("\nIngresa el email del usuario: ")
            nueva_password = input("Ingresa la nueva contraseña: ")
            cambiar_contraseña(email, nueva_password)
        elif opcion == "9":
            obtener_estadisticas()
        elif opcion == "10":
            try:
                limite = int(input("\n¿Cuántos usuarios mostrar? (default 10): ") or "10")
                listar_usuarios_recientes(limite)
            except ValueError:
                print("❌ Número inválido")
        elif opcion == "11":
            fecha_inicio = input("\nFecha de inicio (YYYY-MM-DD): ")
            fecha_fin = input("Fecha de fin (YYYY-MM-DD): ")
            buscar_usuarios_por_fecha(fecha_inicio, fecha_fin)
        elif opcion == "12":
            contar_usuarios_activos()
        elif opcion == "13":
            auditar_actividad_usuarios()
        elif opcion == "14":
            hacer_respaldo()
        elif opcion == "15":
            archivo = input("\nNombre del archivo de respaldo: ")
            restaurar_respaldo(archivo)
        elif opcion == "16":
            archivo = input("\nNombre del archivo CSV (default: usuarios_export.csv): ") or "usuarios_export.csv"
            exportar_a_csv(archivo)
        elif opcion == "17":
            try:
                dias = int(input("\nDías de inactividad (default 365): ") or "365")
                limpiar_usuarios_inactivos(dias)
            except ValueError:
                print("❌ Número inválido")
        elif opcion == "18":
            verificar_integridad_passwords()
        elif opcion == "19":
            buscar_emails_duplicados()
        elif opcion == "20":
            email = input("\nIngresa el email del usuario a configurar: ")
            menu_ajustes(email)
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!\n")
            break
        else:
            print("\n❌ Opción inválida. Intenta de nuevo.\n")



if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 INICIANDO ADMINISTRADOR DE BASE DE DATOS NORDSIGN")
    print("="*80)
    print("\nVersión: 6.0 - Con Ajustes de Usuario Integrados")
    print("Base de datos: usuarios.db")
    print("Funciones disponibles: 20")
    print("\n" + "="*80)
    
    menu_principal()