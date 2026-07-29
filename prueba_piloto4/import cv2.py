import cv2
import mediapipe as mp
import csv
import os
import threading
# ===== CONFIGURACIÓN =====
MUESTRAS_POR_PALABRA = 50
ARCHIVO = "dataset.csv"

# ===== UTILIDADES: LEER CLASES EXISTENTES =====
def leer_clases_existentes(path_csv: str):
    """
    Devuelve:
      - lista_ordenada_clases (str)
      - conteo_por_clase (dict palabra -> int)
    """
    if not os.path.exists(path_csv):
        return [], {}

    conteo = {}
    with open(path_csv, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # salta encabezado

        # última columna es la etiqueta
        for row in reader:
            if not row:
                continue
            palabra = row[-1].strip()
            if palabra == "":
                continue
            conteo[palabra] = conteo.get(palabra, 0) + 1

    clases = sorted(conteo.keys(), key=lambda x: x.lower())
    return clases, conteo

def imprimir_clases(clases, conteo):
    if not clases:
        print("📭 Aún no hay clases guardadas (dataset vacío).")
        return
    print("\n📚 Clases ya creadas (en el CSV):")
    for i, c in enumerate(clases, 1):
        print(f"  {i}. {c}  ->  {conteo[c]} muestras")
    print("")

# ===== CREA CSV SI NO EXISTE =====
if not os.path.exists(ARCHIVO):
    with open(ARCHIVO, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = []
        for i in range(21):
            header += [f"x{i}", f"y{i}", f"z{i}"]
        header.append("palabra")
        writer.writerow(header)

# ===== MOSTRAR CLASES EXISTENTES AL INICIO =====
clases_existentes, conteo_existentes = leer_clases_existentes(ARCHIVO)
imprimir_clases(clases_existentes, conteo_existentes)

# ===== MEDIAPIPE =====
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7
)
cap = cv2.VideoCapture(0)

# ===== VARIABLES COMPARTIDAS =====
lock = threading.Lock()
palabra_actual = None
contador = 0
salir = False

def hilo_consola():
    """
    Escribe una palabra y presiona Enter para empezar captura.
    Comandos:
      - listar : muestra clases existentes
      - salir  : cierra el programa
    """
    global palabra_actual, contador, salir

    print("✅ Escribe una palabra y Enter para capturar.")
    print("🧾 Comandos: 'listar' (ver clases), 'salir' (cerrar)\n")

    while True:
        try:
            texto = input("Palabra> ").strip()
        except EOFError:
            texto = "salir"

        if texto == "":
            continue

        if texto.lower() == "salir":
            with lock:
                salir = True
            break

        if texto.lower() == "listar":
            clases, conteo = leer_clases_existentes(ARCHIVO)
            imprimir_clases(clases, conteo)
            continue

        with lock:
            palabra_actual = texto
            contador = 0
        print(f"📥 Capturando '{texto}' ({contador}/{MUESTRAS_POR_PALABRA})")

t = threading.Thread(target=hilo_consola, daemon=True)
t.start()

# ===== LOOP PRINCIPAL =====
while True:
    with lock:
        if salir:
            break
        palabra = palabra_actual
        c = contador

    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(frame_rgb)

    if resultado.multi_hand_landmarks:
        hand = resultado.multi_hand_landmarks[0]
        mp.solutions.drawing_utils.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        if palabra is not None and c < MUESTRAS_POR_PALABRA:
            fila = []
            for lm in hand.landmark:
                fila.extend([lm.x, lm.y, lm.z])
            fila.append(palabra)

            with open(ARCHIVO, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(fila)

            with lock:
                contador += 1
                c2 = contador

            print(f"✅ '{palabra}': {c2}/{MUESTRAS_POR_PALABRA}")

            if c2 >= MUESTRAS_POR_PALABRA:
                with lock:
                    palabra_actual = None
                    contador = 0
                print(f"✔ Clase completada: '{palabra}'")

    # overlay
    estado = f"Capturando: {palabra} ({c}/{MUESTRAS_POR_PALABRA})" if palabra else "Esperando palabra (consola)"
    cv2.putText(frame, estado, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Captura de datos", frame)
    if (cv2.waitKey(1) & 0xFF) == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
print("👋 Cerrado.")
