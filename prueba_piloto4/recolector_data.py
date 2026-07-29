import cv2
import mediapipe as mp
import pandas as pd
import numpy as np
import os
import math




# ── Configuración
LETRAS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
MUESTRAS_META = 100
ARCHIVO_CSV = "dat_lsc.csv"
UMBRAL_3_5_B = 0.55
UMBRAL_4_17_B = 0.85




mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils




def extraer_landmarks(hand_landmarks):
    """Devuelve lista de 63 valores (21 puntos × x, y, z)."""
    datos = []
    for lm in hand_landmarks.landmark:
        datos.extend([lm.x, lm.y, lm.z])
    return datos




# =========================
# FUNCIONES PARA VALIDAR B
# =========================
def distancia_landmarks(hand_landmarks, i, j):
    p1 = hand_landmarks.landmark[i]
    p2 = hand_landmarks.landmark[j]
    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2 +
        (p1.z - p2.z) ** 2
    )






    lm = hand_landmarks.landmark


    ancho_palma = distancia_landmarks(hand_landmarks, 5, 17)


    if ancho_palma == 0:
        return False


    # =========================
    # DEDOS EXTENDIDOS
    # =========================
    dedos_extendidos = (
        lm[8].y < lm[6].y and
        lm[12].y < lm[10].y and
        lm[16].y < lm[14].y and
        lm[20].y < lm[18].y
    )


    # =========================
    # DEDOS JUNTOS
    # =========================
    d_8_12 = distancia_landmarks(hand_landmarks, 8, 12) / ancho_palma
    d_12_16 = distancia_landmarks(hand_landmarks, 12, 16) / ancho_palma
    d_16_20 = distancia_landmarks(hand_landmarks, 16, 20) / ancho_palma


    dedos_juntos = (
        d_8_12 < 0.60 and
        d_12_16 < 0.60 and
        d_16_20 < 0.60
    )


    # =========================
    # PULGAR DENTRO DE LA PALMA
    # =========================
    pulgar_dentro = (
        lm[4].x > lm[5].x and
        lm[4].x < lm[17].x
    )


    return (
        dedos_extendidos and
        dedos_juntos and
        pulgar_dentro
    )


def es_b_valida(hand_landmarks):
    """
    B válida cuando:
    1. Los dedos están estirados.
    2. Punto 3 cerca/tocando el 5 O punto 4 cerca/tocando el 17.
    """


    lm = hand_landmarks.landmark
    ancho_palma = distancia_landmarks(hand_landmarks, 5, 17)


    if ancho_palma == 0:
        return False


    # Dedos estirados
    dedos_estirados = (
        lm[8].y < lm[6].y and
        lm[12].y < lm[10].y and
        lm[16].y < lm[14].y and
        lm[20].y < lm[18].y
    )


    # Punto 3 cerca del 5
    d_3_5 = distancia_landmarks(hand_landmarks, 3, 5) / ancho_palma


    # Punto 4 cerca del 17
    d_4_17 = distancia_landmarks(hand_landmarks, 4, 17) / ancho_palma


    pulgar_valido = (
        d_3_5 <= 0.55 or
        d_4_17 <= 0.85
    )


    return dedos_estirados and pulgar_valido
def cargar_progreso():
    """Devuelve DataFrame existente o vacío."""
    if os.path.exists(ARCHIVO_CSV):
        df = pd.read_csv(ARCHIVO_CSV)
        print(f"📂 Archivo existente cargado: {len(df)} muestras totales")
        return df


    columnas = [f"x{i}" for i in range(63)] + ["label"]
    return pd.DataFrame(columns=columnas)




def contar_por_letra(df):
    if df.empty:
        return {}
    return df["label"].value_counts().to_dict()




def guardar(df, nuevas_filas):
    """Agrega nuevas_filas al df y guarda CSV. Devuelve df actualizado."""
    if not nuevas_filas:
        return df


    columnas = [f"x{i}" for i in range(63)] + ["label"]
    df_nuevo = pd.DataFrame(nuevas_filas, columns=columnas)
    df = pd.concat([df, df_nuevo], ignore_index=True)
    df.to_csv(ARCHIVO_CSV, index=False)
    return df




def main():
    df = cargar_progreso()
    conteo = contar_por_letra(df)


    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara.")
        return


    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.6
    )


    capturando = False
    letra_captura = ""
    frames_restantes = 0
    nuevas_filas = []


    print("\n🟢 Cámara lista.")
    print("Presiona cualquier letra (A-Z) para capturar 100 frames automáticamente.")
    print("Puedes presionar la misma letra varias veces para agregar más muestras.")
    print("[Q] → guardar y salir\n")


    for l in LETRAS:
        n = conteo.get(l, 0)
        barra = "█" * (n // 10)
        print(f"{l}: {n:>4} {barra}")
    print()


    while True:
        ret, frame = cap.read()
        if not ret:
            break


        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)


        h, w = frame.shape[:2]
        mano_visible = result.multi_hand_landmarks is not None


        # Captura con validación extra para la B
        if capturando and frames_restantes > 0:
            if mano_visible:
                hand = result.multi_hand_landmarks[0]
       
               
        if mano_visible:
            mp_drawing.draw_landmarks(
                frame,
                result.multi_hand_landmarks[0],
                mp_hands.HAND_CONNECTIONS
            )


        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 95), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)


        if capturando:
            cv2.putText(
                frame,
                letra_captura,
                (15, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                2.8,
                (0, 220, 255),
                6
            )


            progreso_rafaga = (MUESTRAS_META - frames_restantes) / MUESTRAS_META
            bar_x, bar_y, bar_w, bar_h = 120, 30, w - 140, 18


            cv2.rectangle(
                frame,
                (bar_x, bar_y),
                (bar_x + bar_w, bar_y + bar_h),
                (60, 60, 60),
                -1
            )


            fill = int(bar_w * progreso_rafaga)


            cv2.rectangle(
                frame,
                (bar_x, bar_y),
                (bar_x + fill, bar_y + bar_h),
                (0, 210, 90),
                -1
            )


            texto_prog = f"{MUESTRAS_META - frames_restantes}/{MUESTRAS_META}"


            cv2.putText(
                frame,
                texto_prog,
                (bar_x, bar_y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )


            if not mano_visible:
                cv2.putText(
                    frame,
                    "Pon la mano en camara",
                    (bar_x, bar_y + bar_h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 80, 255),
                    2
                )


        else:
            cv2.putText(
                frame,
                "Presiona A-Z para capturar",
                (15, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (200, 200, 200),
                2
            )


            x_offset = 15


            for l in LETRAS:
                n = conteo.get(l, 0)
                color = (0, 200, 80) if n >= MUESTRAS_META else (80, 80, 80)


                cv2.putText(
                    frame,
                    l,
                    (x_offset, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    color,
                    2
                )


                x_offset += 23


        estado_mano = "Mano OK" if mano_visible else "Sin mano"
        color_mano = (0, 220, 80) if mano_visible else (0, 80, 220)


        cv2.putText(
            frame,
            estado_mano,
            (15, h - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color_mano,
            2
        )


        cv2.putText(
            frame,
            "[Q] Guardar y salir",
            (w - 210, h - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (180, 180, 180),
            1
        )


        cv2.imshow("NordSign - Recoleccion LSC | Presiona A-Z", frame)


        key = cv2.waitKey(1) & 0xFF


        if key == ord("q") or key == ord("Q"):
            break


        if not capturando:
            char = chr(key).upper()


            if char in LETRAS and mano_visible:
                letra_captura = char
                frames_restantes = MUESTRAS_META
                capturando = True
                print(f"\n🔴 Capturando [{letra_captura}] — mantén la seña fija...")


            elif char in LETRAS and not mano_visible:
                print(f"\n⚠️ Pon la mano en cámara antes de capturar [{char}]")


    if nuevas_filas:
        df = guardar(df, nuevas_filas)


    if not df.empty:
        conteo_final = contar_por_letra(df)


        print(f"\n✅ Datos guardados en '{ARCHIVO_CSV}'")
        print(f"Total muestras : {len(df)}")
        print("Resumen final:")


        for l in LETRAS:
            n = conteo_final.get(l, 0)
            barra = "█" * (n // 10)
            ok = "✅" if n >= MUESTRAS_META else " "
            print(f"{ok} {l}: {n:>4} {barra}")


        print("\n▶ Ahora ejecuta: python entrenar_modelo.py")


    else:
        print("\n⚠️ No se capturaron datos.")


    cap.release()
    cv2.destroyAllWindows()
    hands.close()




if __name__ == "__main__":
    main()
