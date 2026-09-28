import os

import cv2
import joblib
import mediapipe as mp
import pandas as pd

from validaciones import (
    es_b_valida,
    es_o_valida,
    diagnostico_b
)


# ============================================================
# NORDSIGN
# 03_reconocimiento.py
#
# Reconocimiento en tiempo real:
#
# Cámara
#   ↓
# MediaPipe Hands
#   ↓
# 63 características
#   ↓
# Random Forest
#   ↓
# Validaciones geométricas B / O
#   ↓
# Resultado final
# ============================================================


# ============================================================
# RUTAS
# ============================================================

# Carpeta:
# interfaz-visual/codigos/
RUTA_CODIGOS = os.path.dirname(
    os.path.abspath(__file__)
)

# Carpeta:
# interfaz-visual/
RUTA_PROYECTO = os.path.dirname(
    RUTA_CODIGOS
)

# Modelo:
# interfaz-visual/modelos de IA/modelo_lsc.pkl
RUTA_MODELO = os.path.join(
    RUTA_PROYECTO,
    "modelos de IA",
    "modelo_lsc.pkl"
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Confianza mínima que exigiremos al Random Forest.
#
# Por ahora la dejamos en 70%.
# Después podemos ajustarla.
CONFIANZA_MINIMA = 0.70


# Si quieres ver información adicional de B,
# cambia False por True.
MODO_DEPURACION_B = False


# ============================================================
# COMPROBAR MODELO
# ============================================================

print("\n========================================")
print("      NORDSIGN - RECONOCIMIENTO")
print("========================================")

print("\nBuscando modelo en:")

print(
    RUTA_MODELO
)


if not os.path.exists(
    RUTA_MODELO
):

    print(
        "\n❌ ERROR:"
    )

    print(
        "No se encontro modelo_lsc.pkl"
    )

    print(
        "\nEjecuta primero:"
    )

    print(
        "python .\\codigos\\02_entrenar_modelo.py"
    )

    raise SystemExit


# ============================================================
# CARGAR MODELO
# ============================================================

print(
    "\n📦 Cargando modelo..."
)


modelo = joblib.load(
    RUTA_MODELO
)


print(
    "✅ Modelo cargado."
)


# ============================================================
# MOSTRAR INFORMACIÓN
# ============================================================

print(
    "\nClases aprendidas:"
)

print(
    modelo.classes_
)


print(
    f"\nCaracteristicas esperadas: "
    f"{modelo.n_features_in_}"
)


if hasattr(
    modelo,
    "feature_names_in_"
):

    COLUMNAS_MODELO = list(
        modelo.feature_names_in_
    )

else:

    COLUMNAS_MODELO = None


# ============================================================
# MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands

mp_drawing = (
    mp.solutions.drawing_utils
)


hands = mp_hands.Hands(

    static_image_mode=False,

    max_num_hands=1,

    min_detection_confidence=0.75,

    min_tracking_confidence=0.60
)


# ============================================================
# EXTRAER LANDMARKS
# ============================================================

def extraer_landmarks(
    hand_landmarks
):
    """
    Convierte los 21 landmarks de MediaPipe
    en las mismas 63 características utilizadas
    durante el entrenamiento.

    Orden:

    x0 y0 z0
    x1 y1 z1
    ...
    x20 y20 z20
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
# PREPARAR DATOS PARA RANDOM FOREST
# ============================================================

def preparar_datos_modelo(
    datos
):
    """
    Crea un DataFrame utilizando EXACTAMENTE
    los nombres de columnas con los que fue
    entrenado el Random Forest.

    Esto evita el warning:

    X does not have valid feature names
    """

    if COLUMNAS_MODELO is not None:

        return pd.DataFrame(
            [datos],
            columns=COLUMNAS_MODELO
        )


    # Solo se utilizaría si el modelo no tuviera
    # feature_names_in_.
    return pd.DataFrame(
        [datos]
    )


# ============================================================
# ABRIR CÁMARA
# ============================================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print(
        "\n❌ No se pudo abrir la camara."
    )

    hands.close()

    raise SystemExit


print(
    "\n🟢 Camara iniciada."
)

print(
    "Haz una de las senas aprendidas:"
)

print(
    "A - B - O"
)

print(
    "\nPresiona Q para salir."
)


# ============================================================
# BUCLE PRINCIPAL
# ============================================================

while True:

    ret, frame = cap.read()


    if not ret:

        print(
            "❌ No se pudo leer la camara."
        )

        break


    # ========================================================
    # EFECTO ESPEJO
    # ========================================================

    frame = cv2.flip(
        frame,
        1
    )


    # ========================================================
    # CONVERTIR BGR → RGB
    # ========================================================

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # ========================================================
    # MEDIAPIPE
    # ========================================================

    resultado = hands.process(
        rgb
    )


    # Valores predeterminados
    letra_modelo = ""

    letra_final = ""

    confianza = 0.0

    estado_validacion = ""


    # ========================================================
    # SI HAY UNA MANO
    # ========================================================

    if resultado.multi_hand_landmarks:

        hand = (
            resultado
            .multi_hand_landmarks[0]
        )


        # ====================================================
        # DIBUJAR LANDMARKS
        # ====================================================

        mp_drawing.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )


        # ====================================================
        # EXTRAER 63 DATOS
        # ====================================================

        datos = extraer_landmarks(
            hand
        )


        # ====================================================
        # COMPROBAR LONGITUD
        # ====================================================

        if len(datos) == 63:

            datos_modelo = (
                preparar_datos_modelo(
                    datos
                )
            )


            # ================================================
            # PREDICCIÓN
            # ================================================

            probabilidades = (
                modelo.predict_proba(
                    datos_modelo
                )[0]
            )


            indice_mejor = (
                probabilidades.argmax()
            )


            letra_modelo = str(
                modelo.classes_[
                    indice_mejor
                ]
            )


            confianza = float(
                probabilidades[
                    indice_mejor
                ]
            )


            # ================================================
            # FILTRO DE CONFIANZA
            # ================================================

            if (
                confianza
                >=
                CONFIANZA_MINIMA
            ):

                letra_final = (
                    letra_modelo
                )


                # ============================================
                # VALIDACIÓN DE B
                # ============================================

                if letra_modelo == "B":

                    if es_b_valida(
                        hand
                    ):

                        letra_final = "B"

                        estado_validacion = (
                            "Geometria B: OK"
                        )

                    else:

                        letra_final = ""

                        estado_validacion = (
                            "Geometria B: NO"
                        )


                # ============================================
                # VALIDACIÓN DE O
                # ============================================

                elif letra_modelo == "O":

                    if es_o_valida(
                        hand
                    ):

                        letra_final = "O"

                        estado_validacion = (
                            "Geometria O: OK"
                        )

                    else:

                        letra_final = ""

                        estado_validacion = (
                            "Geometria O: NO"
                        )


            else:

                letra_final = ""

                estado_validacion = (
                    "Confianza insuficiente"
                )


            # ================================================
            # DEPURACIÓN B
            # ================================================

            if (
                MODO_DEPURACION_B
                and
                letra_modelo == "B"
            ):

                diag = diagnostico_b(
                    hand
                )


                print(
                    "\n--- B ---"
                )

                print(
                    "Rectos:",
                    diag["dedos_rectos"]
                )

                print(
                    "Juntos:",
                    diag["dedos_juntos"]
                )

                print(
                    "Pulgar:",
                    diag["pulgar_dentro"]
                )

                print(
                    "Angulos:",
                    diag["angulos"]
                )

                print(
                    "Distancias:",
                    diag["distancias"]
                )


    # ========================================================
    # INTERFAZ DE PRUEBA
    # ========================================================

    altura, ancho = (
        frame.shape[:2]
    )


    # Fondo superior
    overlay = frame.copy()


    cv2.rectangle(
        overlay,
        (0, 0),
        (ancho, 145),
        (20, 20, 20),
        -1
    )


    cv2.addWeighted(
        overlay,
        0.70,
        frame,
        0.30,
        0,
        frame
    )


    # ========================================================
    # PREDICCIÓN DEL MODELO
    # ========================================================

    if letra_modelo:

        texto_modelo = (
            f"Modelo: {letra_modelo}"
        )

        texto_confianza = (
            f"Confianza: "
            f"{confianza * 100:.1f}%"
        )

    else:

        texto_modelo = (
            "Modelo: ---"
        )

        texto_confianza = (
            "Confianza: ---"
        )


    cv2.putText(
        frame,
        texto_modelo,
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.70,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        texto_confianza,
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    # ========================================================
    # VALIDACIÓN
    # ========================================================

    if estado_validacion:

        cv2.putText(
            frame,
            estado_validacion,
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            (0, 220, 255),
            2
        )


    # ========================================================
    # RESULTADO FINAL
    # ========================================================

    if letra_final:

        cv2.putText(
            frame,
            f"Resultado: {letra_final}",
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            (0, 255, 0),
            3
        )


        # Letra grande
        cv2.putText(
            frame,
            letra_final,
            (
                ancho - 110,
                115
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            3,
            (0, 255, 0),
            6
        )


    elif letra_modelo:

        cv2.putText(
            frame,
            "Resultado: NO VALIDA",
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 255),
            2
        )


    else:

        cv2.putText(
            frame,
            "Muestra la mano",
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.70,
            (180, 180, 180),
            2
        )


    # ========================================================
    # SALIR
    # ========================================================

    cv2.putText(
        frame,
        "[Q] Salir",
        (
            ancho - 120,
            altura - 20
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1
    )


    # ========================================================
    # MOSTRAR
    # ========================================================

    cv2.imshow(
        "NordSign - Prueba del modelo",
        frame
    )


    key = (
        cv2.waitKey(1)
        &
        0xFF
    )


    if (
        key == ord("q")
        or
        key == ord("Q")
    ):

        break


# ============================================================
# CERRAR
# ============================================================

cap.release()

cv2.destroyAllWindows()

hands.close()


print(
    "\n✅ Reconocimiento finalizado."
)