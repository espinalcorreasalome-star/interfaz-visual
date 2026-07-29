import cv2
import mediapipe as mp
import joblib
import numpy as np

# Cargar modelo
modelo = joblib.load('modelo_lsc.pkl')

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7
)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(rgb)

    if resultado.multi_hand_landmarks:
        hand = resultado.multi_hand_landmarks[0]
        mp.solutions.drawing_utils.draw_landmarks(
            frame, hand, mp_hands.HAND_CONNECTIONS
        )

        datos = []
        for lm in hand.landmark:
            datos.extend([lm.x, lm.y, lm.z])

        datos = np.array(datos).reshape(1, -1)

        letra = modelo.predict(datos)[0]

        cv2.putText(frame, letra, (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    4, (0, 0, 255), 6)

    cv2.imshow("Reconocimiento LSC", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
