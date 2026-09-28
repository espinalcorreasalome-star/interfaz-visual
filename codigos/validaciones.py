import math
import numpy as np


# ============================================================
# NORDSIGN
# validaciones.py
#
# Validaciones geométricas adicionales para las señas.
#
# Actualmente:
#   - Letra B
#   - Letra O
#
# Estas reglas se utilizan tanto durante la recolección
# como posteriormente durante el reconocimiento.
# ============================================================


# ============================================================
# UMBRALES AJUSTABLES
# ============================================================

# ------------------------------------------------------------
# LETRA B
# ------------------------------------------------------------

# Distancia máxima permitida entre los dedos superiores
# para considerar que están juntos.
UMBRAL_DEDOS_JUNTOS_B = 0.80

# Distancia máxima del pulgar respecto a la zona interna
# de la palma.
UMBRAL_PULGAR_DENTRO_B = 0.95

# Ángulo mínimo para considerar un dedo recto.
# 180 grados representa aproximadamente un dedo totalmente recto.
UMBRAL_DEDO_RECTO_B = 170


# ------------------------------------------------------------
# LETRA O
# ------------------------------------------------------------

# Distancia máxima entre las puntas de los dedos
# y la punta del pulgar.
UMBRAL_O = 0.45


# ============================================================
# FUNCIONES BASE
# ============================================================

def distancia_landmarks(hand_landmarks, i, j):
    """
    Calcula la distancia tridimensional entre dos landmarks.

    Parámetros:
        hand_landmarks:
            Mano detectada por MediaPipe.

        i:
            Número del primer landmark.

        j:
            Número del segundo landmark.

    Retorna:
        Distancia entre ambos puntos.
    """

    p1 = hand_landmarks.landmark[i]
    p2 = hand_landmarks.landmark[j]

    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2 +
        (p1.z - p2.z) ** 2
    )


def angulo_entre_puntos(
    hand_landmarks,
    a,
    b,
    c
):
    """
    Calcula el ángulo formado por tres landmarks.

    El punto B es el vértice del ángulo:

        A ---- B ---- C

    Un ángulo cercano a 180 grados indica
    que la articulación está aproximadamente recta.
    """

    pa = np.array([
        hand_landmarks.landmark[a].x,
        hand_landmarks.landmark[a].y,
        hand_landmarks.landmark[a].z
    ])

    pb = np.array([
        hand_landmarks.landmark[b].x,
        hand_landmarks.landmark[b].y,
        hand_landmarks.landmark[b].z
    ])

    pc = np.array([
        hand_landmarks.landmark[c].x,
        hand_landmarks.landmark[c].y,
        hand_landmarks.landmark[c].z
    ])


    # Vectores que salen desde B
    ba = pa - pb
    bc = pc - pb


    # Producto punto
    coseno = np.dot(
        ba,
        bc
    ) / (
        np.linalg.norm(ba)
        *
        np.linalg.norm(bc)
        +
        1e-6
    )


    # Evita valores fuera del rango
    # permitido por arccos.
    coseno = np.clip(
        coseno,
        -1.0,
        1.0
    )


    # Convertir de radianes a grados
    angulo = np.degrees(
        np.arccos(coseno)
    )


    return angulo


# ============================================================
# ÁNGULOS DE LOS DEDOS
# ============================================================

def obtener_angulos_dedos(
    hand_landmarks
):
    """
    Obtiene un valor representativo del ángulo
    de índice, medio, anular y meñique.

    Se utilizan dos articulaciones de cada dedo.

    Si cualquiera de ellas está doblada,
    el valor mínimo será el utilizado.
    """

    return {

        # ----------------------------------------------------
        # ÍNDICE
        # Landmarks:
        # 5 - 6 - 7 - 8
        # ----------------------------------------------------

        "Indice": min(

            angulo_entre_puntos(
                hand_landmarks,
                5,
                6,
                7
            ),

            angulo_entre_puntos(
                hand_landmarks,
                6,
                7,
                8
            )
        ),


        # ----------------------------------------------------
        # MEDIO
        # Landmarks:
        # 9 - 10 - 11 - 12
        # ----------------------------------------------------

        "Medio": min(

            angulo_entre_puntos(
                hand_landmarks,
                9,
                10,
                11
            ),

            angulo_entre_puntos(
                hand_landmarks,
                10,
                11,
                12
            )
        ),


        # ----------------------------------------------------
        # ANULAR
        # Landmarks:
        # 13 - 14 - 15 - 16
        # ----------------------------------------------------

        "Anular": min(

            angulo_entre_puntos(
                hand_landmarks,
                13,
                14,
                15
            ),

            angulo_entre_puntos(
                hand_landmarks,
                14,
                15,
                16
            )
        ),


        # ----------------------------------------------------
        # MEÑIQUE
        # Landmarks:
        # 17 - 18 - 19 - 20
        # ----------------------------------------------------

        "Menique": min(

            angulo_entre_puntos(
                hand_landmarks,
                17,
                18,
                19
            ),

            angulo_entre_puntos(
                hand_landmarks,
                18,
                19,
                20
            )
        )
    }


# ============================================================
# DIAGNÓSTICO DE LA LETRA B
# ============================================================

def diagnostico_b(
    hand_landmarks
):
    """
    Analiza todas las condiciones geométricas
    utilizadas actualmente para reconocer la B.

    La B requiere:

    1. Índice recto.
    2. Medio recto.
    3. Anular recto.
    4. Meñique recto.
    5. Los cuatro dedos juntos.
    6. Pulgar dentro/sobre la palma.

    Retorna un diccionario con todos los resultados
    para facilitar la depuración.
    """

    lm = hand_landmarks.landmark


    # ========================================================
    # TAMAÑO DE REFERENCIA DE LA MANO
    # ========================================================

    # Distancia entre la base del índice (5)
    # y la base del meñique (17).
    #
    # Esto representa aproximadamente el ancho
    # de la palma.
    ancho_palma = distancia_landmarks(
        hand_landmarks,
        5,
        17
    )


    # Protección contra división por cero.
    if ancho_palma <= 1e-6:

        return {
            "dedos_rectos": False,
            "dedos_juntos": False,
            "pulgar_dentro": False,
            "b_valida": False,
            "angulos": {},
            "distancias": {}
        }


    # ========================================================
    # 1. DEDOS RECTOS
    # ========================================================

    angulos = obtener_angulos_dedos(
        hand_landmarks
    )


    # Todos los dedos deben superar
    # el ángulo mínimo.
    dedos_rectos_por_angulo = all(

        angulo >= UMBRAL_DEDO_RECTO_B

        for angulo
        in angulos.values()
    )


    # ========================================================
    # 2. DEDOS HACIA ARRIBA
    # ========================================================

    # En las coordenadas de MediaPipe:
    #
    # y pequeño = más arriba en pantalla
    # y grande  = más abajo
    #
    # Por eso las puntas deben tener una Y menor
    # que las articulaciones anteriores.

    dedos_hacia_arriba = (

        # Índice
        lm[8].y < lm[6].y

        and

        # Medio
        lm[12].y < lm[10].y

        and

        # Anular
        lm[16].y < lm[14].y

        and

        # Meñique
        lm[20].y < lm[18].y
    )


    # Para considerar los dedos rectos,
    # ambas condiciones deben cumplirse.
    dedos_rectos = (

        dedos_rectos_por_angulo
        and
        dedos_hacia_arriba
    )


    # ========================================================
    # 3. DEDOS JUNTOS
    # ========================================================

    # Calculamos distancias entre las puntas.
    #
    # Después dividimos por el ancho de la palma.
    #
    # De esta manera la regla funciona aunque
    # la mano esté más cerca o más lejos
    # de la cámara.


    # Índice → Medio
    d_8_12 = (

        distancia_landmarks(
            hand_landmarks,
            8,
            12
        )

        /

        ancho_palma
    )


    # Medio → Anular
    d_12_16 = (

        distancia_landmarks(
            hand_landmarks,
            12,
            16
        )

        /

        ancho_palma
    )


    # Anular → Meñique
    d_16_20 = (

        distancia_landmarks(
            hand_landmarks,
            16,
            20
        )

        /

        ancho_palma
    )


    dedos_juntos = (

        d_8_12
        <=
        UMBRAL_DEDOS_JUNTOS_B

        and

        d_12_16
        <=
        UMBRAL_DEDOS_JUNTOS_B

        and

        d_16_20
        <=
        UMBRAL_DEDOS_JUNTOS_B
    )


    # ========================================================
    # 4. PULGAR DENTRO DE LA PALMA
    # ========================================================

    # Punta del pulgar = landmark 4.
    #
    # Comparamos con las bases de:
    #
    # 13 = anular
    # 17 = meñique


    d_4_13 = (

        distancia_landmarks(
            hand_landmarks,
            4,
            13
        )

        /

        ancho_palma
    )


    d_4_17 = (

        distancia_landmarks(
            hand_landmarks,
            4,
            17
        )

        /

        ancho_palma
    )


    # Basta con que esté suficientemente cerca
    # de una de las dos zonas.

    pulgar_dentro = (

        d_4_13
        <=
        UMBRAL_PULGAR_DENTRO_B

        or

        d_4_17
        <=
        UMBRAL_PULGAR_DENTRO_B
    )


    # ========================================================
    # RESULTADO FINAL DE B
    # ========================================================

    b_valida = (

        dedos_rectos
        and
        dedos_juntos
        and
        pulgar_dentro
    )


    # ========================================================
    # DEVOLVER DIAGNÓSTICO
    # ========================================================

    return {

        "dedos_rectos":
            dedos_rectos,

        "dedos_juntos":
            dedos_juntos,

        "pulgar_dentro":
            pulgar_dentro,

        "b_valida":
            b_valida,

        "angulos":
            angulos,

        "distancias": {

            "8-12":
                d_8_12,

            "12-16":
                d_12_16,

            "16-20":
                d_16_20,

            "4-13":
                d_4_13,

            "4-17":
                d_4_17
        }
    }


# ============================================================
# VALIDACIÓN FINAL DE B
# ============================================================

def es_b_valida(
    hand_landmarks
):
    """
    Devuelve True únicamente cuando
    todas las condiciones actuales
    de la letra B se cumplen.
    """

    diagnostico = diagnostico_b(
        hand_landmarks
    )

    return diagnostico["b_valida"]


# ============================================================
# VALIDACIÓN DE LA LETRA O
# ============================================================

def es_o_valida(
    hand_landmarks
):
    """
    La letra O se considera válida cuando:

    punta del índice  (8)
    punta del medio   (12)
    punta del anular  (16)
    punta del meñique (20)

    están cerca de:

    punta del pulgar  (4)

    Las distancias se normalizan usando
    el ancho de la palma.
    """


    # ========================================================
    # TAMAÑO DE REFERENCIA
    # ========================================================

    ancho_palma = distancia_landmarks(
        hand_landmarks,
        5,
        17
    )


    if ancho_palma <= 1e-6:
        return False


    # ========================================================
    # DISTANCIAS AL PULGAR
    # ========================================================

    # Pulgar → Índice
    d_4_8 = (

        distancia_landmarks(
            hand_landmarks,
            4,
            8
        )

        /

        ancho_palma
    )


    # Pulgar → Medio
    d_4_12 = (

        distancia_landmarks(
            hand_landmarks,
            4,
            12
        )

        /

        ancho_palma
    )


    # Pulgar → Anular
    d_4_16 = (

        distancia_landmarks(
            hand_landmarks,
            4,
            16
        )

        /

        ancho_palma
    )


    # Pulgar → Meñique
    d_4_20 = (

        distancia_landmarks(
            hand_landmarks,
            4,
            20
        )

        /

        ancho_palma
    )


    # ========================================================
    # RESULTADO FINAL
    # ========================================================

    o_valida = (

        d_4_8
        <=
        UMBRAL_O

        and

        d_4_12
        <=
        UMBRAL_O

        and

        d_4_16
        <=
        UMBRAL_O

        and

        d_4_20
        <=
        UMBRAL_O
    )


    return o_valida