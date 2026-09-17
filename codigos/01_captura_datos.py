import cv2
import mediapipe as mp
import csv
import os

# ===== CONFIGURACIÓN =====
LETRAS = ['A', 'E', 'I', 'O', 'U', 'L', 'S', 'C', 'B']
MUESTRAS_POR_LETRA = 50 # empieza con 50, luego sube
ARCHIVO = 'dataset.csv'

# ===== MEDIAPIPE =====
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)

cap = cv2.VideoCapture(0)

# Crear CSV si no existe
if not os.path.exists(ARCHIVO):
    with open(ARCHIVO, 'w', newline='') as f:
        writer = csv.writer(f)
        header = []
        for i in range(21):
            header += [f'x{i}', f'y{i}', f'z{i}']
        header.append('letra')
        writer.writerow(header)

print("Presiona la letra que quieras capturar (A,E,I,O,U,L,S,C,B)")
print("Presiona ESC para salir")

contador = 0
letra_actual = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(frame_rgb)

    if resultado.multi_hand_landmarks:
        hand = resultado.multi_hand_landmarks[0]
        mp.solutions.drawing_utils.draw_landmarks(
            frame, hand, mp_hands.HAND_CONNECTIONS
        )

        if letra_actual is not None and contador < MUESTRAS_POR_LETRA:
            fila = []
            for lm in hand.landmark:
                fila.extend([lm.x, lm.y, lm.z])
            fila.append(letra_actual)

            with open(ARCHIVO, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(fila)

            contador += 1
            print(f"{letra_actual}: {contador}/{MUESTRAS_POR_LETRA}")

        if contador == MUESTRAS_POR_LETRA:
            letra_actual = None
            contador = 0
            print("✔ Letra completada")

    cv2.imshow("Captura de datos", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    elif chr(key).upper() in LETRAS:
        letra_actual = chr(key).upper()
        contador = 0
        print(f"Capturando letra {letra_actual}")

cap.release()
cv2.destroyAllWindows()

