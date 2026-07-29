"""
probar_modelo.py — NordSign LSC
=================================
Prueba visual del modelo entrenado (model_NS.pkl).
Muestra en tiempo real la seña detectada, confianza, estabilidad
y un panel con el top-3 de predicciones.

USO:
    python probar_modelo.py

CONTROLES:
    ESC  → salir

REQUISITOS:
    pip install opencv-python mediapipe joblib numpy scikit-learn
"""

import cv2
import mediapipe as mp
import joblib
import numpy as np
from collections import deque
from datetime import datetime
import os

# ── Configuración ──────────────────────────────────────────────────────────────
MODELO_PATH        = "model_NS.pkl"
THRESHOLD          = 0.65       # confianza mínima para considerar una predicción
WINDOW             = 15         # frames para suavizar probabilidades
HOLD_FRAMES        = 8          # frames estables para confirmar seña
GUARDAR_EVIDENCIAS = True
CARPETA_EVIDENCIAS = "evidencias_NS"
# ───────────────────────────────────────────────────────────────────────────────

os.makedirs(CARPETA_EVIDENCIAS, exist_ok=True)

# ── Cargar modelo ──────────────────────────────────────────────────────────────
if not os.path.exists(MODELO_PATH):
    print(f"❌ No se encontró '{MODELO_PATH}'.")
    print("   Primero ejecuta: python entrenar_modelo.py")
    exit(1)

bundle  = joblib.load(MODELO_PATH)

# Soporta formato nuevo (dict con encoder) y formato antiguo (solo clf)
if isinstance(bundle, dict):
    modelo  = bundle["modelo"]
    encoder = bundle["encoder"]
    clases  = list(encoder.classes_)
else:
    modelo  = bundle
    encoder = None
    clases  = list(modelo.classes_) if hasattr(modelo, "classes_") else []

print(f"✅ Modelo cargado — {len(clases)} clases: {clases}")

# ── Extracción de features (debe coincidir con recolectar_datos.py) ────────────
def extraer_features(hand_landmarks) -> np.ndarray:
    """63 valores: x, y, z de los 21 landmarks."""
    datos = []
    for lm in hand_landmarks.landmark:
        datos.extend([lm.x, lm.y, lm.z])
    return np.array(datos, dtype=np.float32)

# ── Helpers visuales ───────────────────────────────────────────────────────────
def color_confianza(conf: float):
    """Verde → amarillo → rojo según confianza."""
    if conf >= 0.80:
        return (0, 210, 80)
    elif conf >= THRESHOLD:
        return (0, 190, 255)
    else:
        return (0, 80, 220)

def dibujar_barra(frame, x, y, w, h, valor, color, label=""):
    cv2.rectangle(frame, (x, y), (x + w, y + h), (60, 60, 60), -1)
    fill = int(w * max(0.0, min(1.0, valor)))
    cv2.rectangle(frame, (x, y), (x + fill, y + h), color, -1)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (150, 150, 150), 1)
    if label:
        cv2.putText(frame, label, (x + w + 8, y + h - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (200, 200, 200), 1)

def dibujar_panel_top3(frame, proba_media, clases, x, y):
    """Dibuja un mini panel con las 3 letras más probables."""
    top3_idx  = np.argsort(proba_media)[::-1][:3]
    panel_w   = 220
    panel_h   = 110
    overlay   = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + panel_w, y + panel_h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    cv2.putText(frame, "Top 3", (x + 8, y + 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)

    for rank, idx in enumerate(top3_idx):
        letra = clases[idx]
        conf  = float(proba_media[idx])
        row_y = y + 35 + rank * 26
        col   = color_confianza(conf)
        cv2.putText(frame, f"{letra}  {conf*100:4.1f}%", (x + 8, row_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.58, col, 2)
        dibujar_barra(frame, x + 105, row_y - 14, 105, 14, conf, col)

# ── MediaPipe ─────────────────────────────────────────────────────────────────
mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles  = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.72,
    min_tracking_confidence=0.65
)

# ── Estado ────────────────────────────────────────────────────────────────────
proba_buffer     = deque(maxlen=WINDOW)
clase_candidata  = None
contador_estable = 0
ultima_guardada  = None
historial        = deque(maxlen=8)   # últimas señas confirmadas

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ No se pudo abrir la cámara.")
    exit(1)

print("\n🟢 Cámara lista — muestra tu mano con una seña.")
print("   ESC para salir.\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame  = cv2.flip(frame, 1)
    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    h, w   = frame.shape[:2]

    # ── Valores por defecto ──────────────────────────────────────────────────
    etiqueta_display = "—"
    conf_display     = 0.0
    estado           = "Esperando mano..."
    color_estado     = (120, 120, 120)
    proba_media      = np.zeros(len(clases))

    # ── Procesamiento de mano ────────────────────────────────────────────────
    if result.multi_hand_landmarks:
        hand = result.multi_hand_landmarks[0]

        # Dibujar landmarks con estilo
        mp_drawing.draw_landmarks(
            frame, hand, mp_hands.HAND_CONNECTIONS,
            mp_styles.get_default_hand_landmarks_style(),
            mp_styles.get_default_hand_connections_style()
        )

        feats = extraer_features(hand).reshape(1, -1)

        # Probabilidades del modelo
        try:
            proba = modelo.predict_proba(feats)[0]
        except Exception as e:
            proba = np.zeros(len(clases))
            print(f"Error en predict_proba: {e}")

        proba_buffer.append(proba)
        proba_media = np.mean(np.stack(proba_buffer), axis=0)

        idx_top  = int(np.argmax(proba_media))
        conf     = float(proba_media[idx_top])

        # Decodificar etiqueta
        if encoder is not None:
            etiqueta = encoder.inverse_transform([idx_top])[0]
        else:
            etiqueta = clases[idx_top] if idx_top < len(clases) else str(idx_top)

        etiqueta_display = etiqueta
        conf_display     = conf

        # ── Histéresis ───────────────────────────────────────────────────────
        if conf >= THRESHOLD:
            if clase_candidata == etiqueta:
                contador_estable += 1
            else:
                clase_candidata  = etiqueta
                contador_estable = 1

            if contador_estable >= HOLD_FRAMES:
                estado       = "CONFIRMADA ✅"
                color_estado = (0, 210, 80)

                # Guardar evidencia una vez por evento
                if GUARDAR_EVIDENCIAS:
                    key_ev = (etiqueta, round(conf, 2))
                    if ultima_guardada != key_ev:
                        ts     = datetime.now().strftime("%H-%M-%S")
                        nombre = f"{etiqueta}_{int(conf*100)}_{ts}.jpg"
                        cv2.imwrite(os.path.join(CARPETA_EVIDENCIAS, nombre), frame)
                        ultima_guardada = key_ev

                        # Agregar al historial
                        historial.append(etiqueta)
                        print(f"  ✅ Seña confirmada: [{etiqueta}]  confianza: {conf*100:.1f}%")
            else:
                estado       = f"Confirmando {contador_estable}/{HOLD_FRAMES}"
                color_estado = (0, 190, 255)
        else:
            clase_candidata  = None
            contador_estable = 0
            estado           = f"Confianza baja ({conf*100:.0f}% < {int(THRESHOLD*100)}%)"
            color_estado     = (0, 80, 220)
    else:
        # Sin mano — limpiar buffer suavemente
        if proba_buffer:
            proba_buffer.clear()
        clase_candidata  = None
        contador_estable = 0

    # ── HUD principal ────────────────────────────────────────────────────────

    # Fondo semitransparente superior
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 175), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    # Letra grande
    letra_color = color_confianza(conf_display)
    cv2.putText(frame, etiqueta_display, (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 4.5, letra_color, 10)
    cv2.putText(frame, etiqueta_display, (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 4.5, (255, 255, 255), 3)

    # Confianza numérica
    cv2.putText(frame, f"{conf_display*100:.1f}%", (160, 75),
                cv2.FONT_HERSHEY_SIMPLEX, 1.4, letra_color, 3)

    # Barra de confianza principal
    dibujar_barra(frame, 160, 90, w - 180, 20,
                  conf_display, letra_color,
                  f"TH={int(THRESHOLD*100)}%")

    # Línea de umbral visual
    umbral_x = 160 + int((w - 180) * THRESHOLD)
    cv2.line(frame, (umbral_x, 90), (umbral_x, 110), (255, 255, 0), 2)

    # Estado
    cv2.putText(frame, estado, (160, 155),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, color_estado, 2)

    # ── Panel Top-3 (esquina inferior derecha) ───────────────────────────────
    if result.multi_hand_landmarks and len(clases) >= 3:
        dibujar_panel_top3(frame, proba_media, clases, w - 235, h - 125)

    # ── Historial de señas confirmadas (parte inferior) ──────────────────────
    if historial:
        overlay2 = frame.copy()
        cv2.rectangle(overlay2, (0, h - 48), (w, h), (15, 15, 15), -1)
        cv2.addWeighted(overlay2, 0.65, frame, 0.35, 0, frame)
        hist_texto = "  ".join(list(historial))
        cv2.putText(frame, f"Historial: {hist_texto}", (12, h - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    # ── Info fija ────────────────────────────────────────────────────────────
    cv2.putText(frame, "NordSign - Prueba de modelo", (12, h - 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
    cv2.putText(frame, "ESC salir", (w - 100, h - 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

    cv2.imshow("NordSign — Prueba de modelo LSC", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
hands.close()

print(f"\n📋 Sesión terminada.")
print(f"   Señas confirmadas: {list(historial)}")
if GUARDAR_EVIDENCIAS:
    print(f"   Evidencias guardadas en: '{CARPETA_EVIDENCIAS}/'")