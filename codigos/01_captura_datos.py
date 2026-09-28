import cv2
import mediapipe as mp
import pandas as pd
import os

from validaciones import (
    es_b_valida,
    es_o_valida,
    diagnostico_b,
    UMBRAL_DEDO_RECTO_B
)


# ============================================================
# NORDSIGN
# 01_recolectar_datos.py
#
# Recolección de landmarks de la mano para entrenar
# el modelo de reconocimiento de LSC.
# ============================================================


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

# Letras que puede recolectar el sistema
LETRAS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Cantidad de muestras que captura cada vez que
# presionamos una letra.
MUESTRAS_META = 100

# Archivo donde se guardará el dataset
ARCHIVO_CSV = "dat_lsc.csv"

# Activar para mostrar información de diagnóstico
# de la letra B en la cámara.
MODO_DEPURACION_B = False


# ============================================================
# CONFIGURACIÓN DE MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


# ============================================================
# NOMBRES DE LAS 63 CARACTERÍSTICAS
# ============================================================

def obtener_columnas():
    """
    Crea los nombres de las 63 características.

    MediaPipe Hands tiene 21 landmarks.

    Cada landmark contiene:
        x
        y
        z

    Por lo tanto:
        21 × 3 = 63 características.

    Resultado:

    x0, y0, z0,
    x1, y1, z1,
    ...
    x20, y20, z20
    """

    columnas = []

    for i in range(21):
        columnas.extend([
            f"x{i}",
            f"y{i}",
            f"z{i}"
        ])

    return columnas


COLUMNAS_LANDMARKS = obtener_columnas()
COLUMNAS_DATASET = COLUMNAS_LANDMARKS + ["label"]


# ============================================================
# EXTRAER LANDMARKS
# ============================================================

def extraer_landmarks(hand_landmarks):
    """
    Convierte los 21 landmarks detectados por MediaPipe
    en una lista de 63 números.

    Orden:

    x0, y0, z0,
    x1, y1, z1,
    ...
    x20, y20, z20
    """

    datos = []

    for lm in hand_landmarks.landmark:
        datos.extend([
            lm.x,
            lm.y,
            lm.z
        ])

    return datos


# ============================================================
# CARGAR DATASET
# ============================================================

def cargar_progreso():
    """
    Si dat_lsc.csv ya existe, carga las muestras existentes.

    Si no existe, crea un DataFrame vacío utilizando
    las columnas oficiales del proyecto.
    """

    if os.path.exists(ARCHIVO_CSV):

        df = pd.read_csv(ARCHIVO_CSV)

        # ----------------------------------------------------
        # COMPROBAR FORMATO DEL DATASET
        # ----------------------------------------------------

        columnas_actuales = list(df.columns)

        if columnas_actuales != COLUMNAS_DATASET:

            print("\n❌ ERROR: El archivo dat_lsc.csv tiene")
            print("un formato diferente al nuevo formato NordSign.")

            print("\nEl nuevo formato utiliza:")
            print("x0, y0, z0 ... x20, y20, z20, label")

            print("\nTu archivo actual comienza con:")
            print(columnas_actuales[:10])

            print(
                "\n⚠ Renombra o elimina el dat_lsc.csv antiguo "
                "antes de continuar."
            )

            return None

        print(
            f"\n📂 Dataset existente cargado: "
            f"{len(df)} muestras totales"
        )

        return df

    # --------------------------------------------------------
    # CREAR DATASET NUEVO
    # --------------------------------------------------------

    print("\n📄 No existe dat_lsc.csv.")
    print("Se creará un dataset nuevo.")

    return pd.DataFrame(
        columns=COLUMNAS_DATASET
    )


# ============================================================
# CONTAR MUESTRAS POR LETRA
# ============================================================

def contar_por_letra(df):
    """
    Devuelve cuántas muestras existen de cada letra.
    """

    if df.empty:
        return {}

    return df["label"].value_counts().to_dict()


# ============================================================
# GUARDAR DATOS
# ============================================================

def guardar(df, nuevas_filas):
    """
    Agrega las nuevas muestras al dataset existente
    y guarda todo en dat_lsc.csv.
    """

    if not nuevas_filas:
        return df

    df_nuevo = pd.DataFrame(
        nuevas_filas,
        columns=COLUMNAS_DATASET
    )

    df = pd.concat(
        [df, df_nuevo],
        ignore_index=True
    )

    df.to_csv(
        ARCHIVO_CSV,
        index=False
    )

    return df


# ============================================================
# VALIDACIONES GEOMÉTRICAS
# ============================================================

def validar_letra_para_guardar(
    letra,
    hand_landmarks
):
    """
    Decide si una muestra puede guardarse.

    Por ahora:

    B:
        utiliza las reglas geométricas de validaciones.py

    O:
        utiliza las reglas geométricas de validaciones.py

    Las demás letras:
        se guardan normalmente.
    """

    # --------------------------------------------------------
    # LETRA B
    # --------------------------------------------------------

    if letra == "B":

        if es_b_valida(hand_landmarks):
            return True, ""

        return (
            False,
            "B invalida: revisa dedos y pulgar"
        )

    # --------------------------------------------------------
    # LETRA O
    # --------------------------------------------------------

    if letra == "O":

        if es_o_valida(hand_landmarks):
            return True, ""

        return (
            False,
            "O invalida: junta las puntas con el pulgar"
        )

    # --------------------------------------------------------
    # RESTO DE LETRAS
    # --------------------------------------------------------

    return True, ""


# ============================================================
# PANEL DE DIAGNÓSTICO PARA B
# ============================================================

def dibujar_panel_b(
    frame,
    hand_landmarks
):
    """
    Muestra las condiciones geométricas de B.

    Sirve para ajustar los umbrales sin tener
    que adivinar qué condición está fallando.
    """

    diag = diagnostico_b(
        hand_landmarks
    )

    x = 15
    y = 125
    salto = 24


    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    cv2.putText(
        frame,
        "DEPURACION B",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )

    y += salto


    # --------------------------------------------------------
    # ÁNGULOS DE LOS DEDOS
    # --------------------------------------------------------

    for nombre, angulo in diag["angulos"].items():

        if angulo >= UMBRAL_DEDO_RECTO_B:
            color = (0, 220, 0)
        else:
            color = (0, 0, 255)

        cv2.putText(
            frame,
            f"{nombre}: {angulo:.1f} grados",
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2
        )

        y += salto


    # --------------------------------------------------------
    # ESTADOS DE LAS REGLAS
    # --------------------------------------------------------

    estados = [
        (
            "Dedos rectos",
            diag["dedos_rectos"]
        ),
        (
            "Dedos juntos",
            diag["dedos_juntos"]
        ),
        (
            "Pulgar dentro",
            diag["pulgar_dentro"]
        ),
        (
            "B valida",
            diag["b_valida"]
        )
    ]


    for nombre, estado in estados:

        if estado:
            color = (0, 220, 0)
            texto = "SI"

        else:
            color = (0, 0, 255)
            texto = "NO"

        cv2.putText(
            frame,
            f"{nombre}: {texto}",
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2
        )

        y += salto


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    # --------------------------------------------------------
    # CARGAR DATASET
    # --------------------------------------------------------

    df = cargar_progreso()

    # Si hubo problema con el formato del CSV,
    # detenemos el programa.
    if df is None:
        return


    conteo = contar_por_letra(df)


    # ========================================================
    # ABRIR CÁMARA
    # ========================================================

    cap = cv2.VideoCapture(0)


    if not cap.isOpened():

        print(
            "❌ No se pudo abrir la cámara."
        )

        return


    # ========================================================
    # MEDIAPIPE HANDS
    # ========================================================

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.60
    )


    # ========================================================
    # VARIABLES DE CAPTURA
    # ========================================================

    capturando = False

    letra_captura = ""

    frames_restantes = 0

    nuevas_filas = []


    # ========================================================
    # INFORMACIÓN INICIAL
    # ========================================================

    print("\n========================================")
    print("       NORDSIGN - RECOLECCION LSC")
    print("========================================")

    print("\n🟢 Cámara lista.")

    print(
        "\nPresiona una letra A-Z para comenzar "
        "la captura."
    )

    print(
        f"Cada captura guardará "
        f"{MUESTRAS_META} muestras válidas."
    )

    print(
        "Puedes capturar una misma letra varias "
        "veces para agregar más datos."
    )

    print("\n[Q] Guardar y salir\n")


    # ========================================================
    # MOSTRAR PROGRESO EXISTENTE
    # ========================================================

    for letra in LETRAS:

        cantidad = conteo.get(
            letra,
            0
        )

        barra = "█" * (
            cantidad // 10
        )

        print(
            f"{letra}: "
            f"{cantidad:>4} "
            f"{barra}"
        )


    print()


    # ========================================================
    # BUCLE DE CÁMARA
    # ========================================================

    while True:

        ret, frame = cap.read()


        if not ret:
            print("❌ Error leyendo la cámara.")
            break


        # ----------------------------------------------------
        # EFECTO ESPEJO
        # ----------------------------------------------------

        frame = cv2.flip(
            frame,
            1
        )


        # ----------------------------------------------------
        # BGR → RGB
        # ----------------------------------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        # ----------------------------------------------------
        # DETECTAR MANO
        # ----------------------------------------------------

        resultado = hands.process(
            rgb
        )


        h, w = frame.shape[:2]


        mano_visible = (
            resultado.multi_hand_landmarks
            is not None
        )


        hand = None


        # ====================================================
        # DIBUJAR MANO
        # ====================================================

        if mano_visible:

            hand = (
                resultado
                .multi_hand_landmarks[0]
            )


            mp_drawing.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )


        # ====================================================
        # CAPTURAR DATOS
        # ====================================================

        if (
            capturando
            and
            frames_restantes > 0
        ):

            if (
                mano_visible
                and
                hand is not None
            ):

                valido, mensaje_error = (
                    validar_letra_para_guardar(
                        letra_captura,
                        hand
                    )
                )


                # --------------------------------------------
                # MUESTRA RECHAZADA
                # --------------------------------------------

                if not valido:

                    cv2.putText(
                        frame,
                        mensaje_error,
                        (15, 110),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.60,
                        (0, 0, 255),
                        2
                    )


                # --------------------------------------------
                # MUESTRA VÁLIDA
                # --------------------------------------------

                else:

                    lm_data = (
                        extraer_landmarks(
                            hand
                        )
                    )


                    nuevas_filas.append(
                        lm_data
                        +
                        [letra_captura]
                    )


                    frames_restantes -= 1


                    capturadas = (
                        MUESTRAS_META
                        -
                        frames_restantes
                    )


                    print(
                        f"[{letra_captura}] "
                        f"capturando... "
                        f"{capturadas}/"
                        f"{MUESTRAS_META}",
                        end="\r"
                    )


                    # ----------------------------------------
                    # TERMINÓ LA RONDA
                    # ----------------------------------------

                    if frames_restantes == 0:

                        df = guardar(
                            df,
                            nuevas_filas
                        )


                        conteo = (
                            contar_por_letra(
                                df
                            )
                        )


                        nuevas_filas = []

                        capturando = False


                        total = conteo.get(
                            letra_captura,
                            0
                        )


                        print(
                            f"\n✅ "
                            f"[{letra_captura}] "
                            f"completado."
                        )

                        print(
                            f"Total acumulado: "
                            f"{total} muestras"
                        )


        # ====================================================
        # PANEL SUPERIOR
        # ====================================================

        overlay = frame.copy()


        cv2.rectangle(
            overlay,
            (0, 0),
            (w, 95),
            (20, 20, 20),
            -1
        )


        cv2.addWeighted(
            overlay,
            0.65,
            frame,
            0.35,
            0,
            frame
        )


        # ====================================================
        # SI ESTÁ CAPTURANDO
        # ====================================================

        if capturando:

            # Letra grande
            cv2.putText(
                frame,
                letra_captura,
                (15, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                2.8,
                (0, 220, 255),
                6
            )


            # -----------------------------------------------
            # BARRA DE PROGRESO
            # -----------------------------------------------

            progreso = (
                MUESTRAS_META
                -
                frames_restantes
            ) / MUESTRAS_META


            bar_x = 120
            bar_y = 30

            bar_w = max(
                50,
                w - 140
            )

            bar_h = 18


            # Fondo
            cv2.rectangle(
                frame,
                (bar_x, bar_y),
                (
                    bar_x + bar_w,
                    bar_y + bar_h
                ),
                (60, 60, 60),
                -1
            )


            # Progreso
            fill = int(
                bar_w * progreso
            )


            cv2.rectangle(
                frame,
                (bar_x, bar_y),
                (
                    bar_x + fill,
                    bar_y + bar_h
                ),
                (0, 210, 90),
                -1
            )


            # Texto
            capturadas = (
                MUESTRAS_META
                -
                frames_restantes
            )


            texto_progreso = (
                f"{capturadas}/"
                f"{MUESTRAS_META}"
            )


            cv2.putText(
                frame,
                texto_progreso,
                (
                    bar_x,
                    bar_y - 5
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )


            # -----------------------------------------------
            # MANO NO DETECTADA
            # -----------------------------------------------

            if not mano_visible:

                cv2.putText(
                    frame,
                    "Pon la mano en camara",
                    (
                        bar_x,
                        bar_y
                        +
                        bar_h
                        +
                        25
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 80, 255),
                    2
                )


        # ====================================================
        # SI NO ESTÁ CAPTURANDO
        # ====================================================

        else:

            cv2.putText(
                frame,
                "Presiona A-Z para capturar",
                (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.70,
                (200, 200, 200),
                2
            )


            # Mostrar letras disponibles
            x_offset = 15


            for letra in LETRAS:

                cantidad = conteo.get(
                    letra,
                    0
                )


                if cantidad >= MUESTRAS_META:

                    color = (
                        0,
                        200,
                        80
                    )

                else:

                    color = (
                        80,
                        80,
                        80
                    )


                cv2.putText(
                    frame,
                    letra,
                    (
                        x_offset,
                        78
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    color,
                    2
                )


                x_offset += 23


        # ====================================================
        # DEPURACIÓN DE B
        # ====================================================

        if (
            MODO_DEPURACION_B
            and
            mano_visible
            and
            hand is not None
        ):

            dibujar_panel_b(
                frame,
                hand
            )


        # ====================================================
        # ESTADO DE LA MANO
        # ====================================================

        if mano_visible:

            estado_mano = "Mano OK"

            color_mano = (
                0,
                220,
                80
            )

        else:

            estado_mano = "Sin mano"

            color_mano = (
                0,
                80,
                220
            )


        cv2.putText(
            frame,
            estado_mano,
            (15, h - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color_mano,
            2
        )


        # ====================================================
        # MENSAJE PARA SALIR
        # ====================================================

        cv2.putText(
            frame,
            "[Q] Guardar y salir",
            (
                max(15, w - 210),
                h - 15
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (180, 180, 180),
            1
        )


        # ====================================================
        # MOSTRAR VENTANA
        # ====================================================

        cv2.imshow(
            "NordSign - Recoleccion LSC",
            frame
        )


        # ====================================================
        # TECLADO
        # ====================================================

        key = (
            cv2.waitKey(1)
            &
            0xFF
        )


        # ----------------------------------------------------
        # Q = GUARDAR Y SALIR
        # ----------------------------------------------------

        if (
            key == ord("q")
            or
            key == ord("Q")
        ):
            break


        # ----------------------------------------------------
        # A-Z = COMENZAR CAPTURA
        # ----------------------------------------------------

        if not capturando:

            # Evita problemas cuando no hay
            # ninguna tecla presionada.
            if key != 255:

                try:
                    char = chr(key).upper()

                except ValueError:
                    char = ""


                if char in LETRAS:

                    # ----------------------------------------
                    # HAY MANO
                    # ----------------------------------------

                    if mano_visible:

                        letra_captura = char

                        frames_restantes = (
                            MUESTRAS_META
                        )

                        capturando = True

                        nuevas_filas = []


                        print(
                            f"\n🔴 Capturando "
                            f"[{letra_captura}]"
                        )

                        print(
                            "Mueve ligeramente la mano "
                            "durante la captura."
                        )


                    # ----------------------------------------
                    # NO HAY MANO
                    # ----------------------------------------

                    else:

                        print(
                            f"\n⚠️ Pon la mano en cámara "
                            f"antes de capturar [{char}]"
                        )


    # ========================================================
    # GUARDAR CAPTURA INCOMPLETA
    # ========================================================

    if nuevas_filas:

        df = guardar(
            df,
            nuevas_filas
        )


        print(
            "\n💾 Se guardaron también las muestras "
            "de la captura incompleta."
        )


    # ========================================================
    # RESUMEN FINAL
    # ========================================================

    if not df.empty:

        conteo_final = (
            contar_por_letra(
                df
            )
        )


        print(
            f"\n✅ Datos guardados en "
            f"'{ARCHIVO_CSV}'"
        )


        print(
            f"Total de muestras: "
            f"{len(df)}"
        )


        print(
            "\n========== RESUMEN =========="
        )


        for letra in LETRAS:

            cantidad = (
                conteo_final.get(
                    letra,
                    0
                )
            )


            barra = (
                "█"
                *
                (cantidad // 10)
            )


            if cantidad >= MUESTRAS_META:
                estado = "✅"
            else:
                estado = "  "


            print(
                f"{estado} "
                f"{letra}: "
                f"{cantidad:>4} "
                f"{barra}"
            )


        print(
            "\n▶ Siguiente paso:"
        )

        print(
            "python 02_entrenar_modelo.py"
        )


    else:

        print(
            "\n⚠️ No existen muestras "
            "en el dataset."
        )


    # ========================================================
    # CERRAR RECURSOS
    # ========================================================

    cap.release()

    cv2.destroyAllWindows()

    hands.close()


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":
    main()