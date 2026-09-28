import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# NORDSIGN
# 02_entrenar_modelo.py
#
# Entrenamiento del modelo Random Forest
# para reconocimiento de señas LSC.
# ============================================================


# ============================================================
# RUTAS DEL PROYECTO
# ============================================================

# Carpeta donde está este archivo:
# interfaz-visual/codigos/
RUTA_CODIGOS = os.path.dirname(
    os.path.abspath(__file__)
)

# Carpeta principal:
# interfaz-visual/
RUTA_PROYECTO = os.path.dirname(
    RUTA_CODIGOS
)

# Dataset:
# interfaz-visual/bases de datos/dat_lsc.csv
RUTA_DATASET = os.path.join(
    RUTA_PROYECTO,
    "dat_lsc.csv"
)

# Carpeta donde guardaremos el modelo
CARPETA_MODELOS = os.path.join(
    RUTA_PROYECTO,
    "modelos de IA"
)

# Modelo final
RUTA_MODELO = os.path.join(
    CARPETA_MODELOS,
    "modelo_lsc.pkl"
)


# ============================================================
# CREAR CARPETA DE MODELOS SI NO EXISTE
# ============================================================

os.makedirs(
    CARPETA_MODELOS,
    exist_ok=True
)


# ============================================================
# INFORMACIÓN INICIAL
# ============================================================

print("\n========================================")
print("      NORDSIGN - ENTRENAMIENTO IA")
print("========================================")

print("\nDataset:")
print(RUTA_DATASET)

print("\nModelo que se generara:")
print(RUTA_MODELO)


# ============================================================
# COMPROBAR DATASET
# ============================================================

if not os.path.exists(RUTA_DATASET):

    print("\n❌ ERROR")

    print(
        "No se encontro el archivo "
        "dat_lsc.csv."
    )

    print("\nEl programa esperaba encontrarlo en:")

    print(RUTA_DATASET)

    print(
        "\nComprueba que dat_lsc.csv este dentro "
        "de la carpeta 'bases de datos'."
    )

    raise SystemExit


# ============================================================
# CARGAR DATASET
# ============================================================

print("\n📂 Cargando dataset...")

df = pd.read_csv(
    RUTA_DATASET
)


print(
    f"✅ Dataset cargado correctamente."
)

print(
    f"Total de muestras: {len(df)}"
)


# ============================================================
# COMPROBAR QUE NO ESTÉ VACÍO
# ============================================================

if df.empty:

    print(
        "\n❌ El dataset esta vacio."
    )

    raise SystemExit


# ============================================================
# COMPROBAR LABEL
# ============================================================

if "label" not in df.columns:

    print(
        "\n❌ ERROR:"
    )

    print(
        "No existe la columna 'label'."
    )

    print(
        "\nColumnas encontradas:"
    )

    print(
        list(df.columns)
    )

    raise SystemExit


# ============================================================
# ELIMINAR FILAS INCOMPLETAS
# ============================================================

cantidad_antes = len(df)

df = df.dropna()

cantidad_despues = len(df)


if cantidad_antes != cantidad_despues:

    eliminadas = (
        cantidad_antes
        -
        cantidad_despues
    )

    print(
        f"\n⚠ Se eliminaron "
        f"{eliminadas} filas incompletas."
    )


# ============================================================
# MOSTRAR LETRAS DEL DATASET
# ============================================================

print("\n========================================")
print("        MUESTRAS POR LETRA")
print("========================================")


conteo = (
    df["label"]
    .value_counts()
    .sort_index()
)


for letra, cantidad in conteo.items():

    print(
        f"{letra}: {cantidad}"
    )


# ============================================================
# SEPARAR CARACTERÍSTICAS Y ETIQUETAS
# ============================================================

# X contiene las coordenadas:
#
# x0 y0 z0
# x1 y1 z1
# ...
# x20 y20 z20

X = df.drop(
    columns=["label"]
)


# y contiene:
#
# A
# B
# O
# etc.

y = df["label"]


# ============================================================
# COMPROBAR LAS 63 CARACTERÍSTICAS
# ============================================================

print(
    f"\nCaracteristicas encontradas: "
    f"{X.shape[1]}"
)


if X.shape[1] != 63:

    print("\n❌ ERROR")

    print(
        "MediaPipe Hands debe producir "
        "63 caracteristicas."
    )

    print(
        f"Actualmente hay "
        f"{X.shape[1]}."
    )

    print(
        "\nNo entrenaremos el modelo para evitar "
        "crear un archivo incorrecto."
    )

    raise SystemExit


print(
    "✅ Las 63 caracteristicas son correctas."
)


# ============================================================
# COMPROBAR CLASES
# ============================================================

clases = sorted(
    y.unique()
)


print(
    f"\nClases encontradas: "
    f"{clases}"
)


print(
    f"Cantidad de clases: "
    f"{len(clases)}"
)


if len(clases) < 2:

    print(
        "\n❌ Se necesitan por lo menos "
        "2 letras diferentes."
    )

    raise SystemExit


# ============================================================
# DIVIDIR DATASET
# ============================================================

print("\n========================================")
print("       DIVISION DEL DATASET")
print("========================================")


X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,

        # 80% entrenamiento
        # 20% prueba
        test_size=0.20,

        # Permite repetir el experimento
        random_state=42,

        # Mantiene proporciones de A/B/O
        stratify=y
    )
)


print(
    f"\nEntrenamiento: "
    f"{len(X_train)} muestras"
)


print(
    f"Prueba: "
    f"{len(X_test)} muestras"
)


# ============================================================
# CREAR RANDOM FOREST
# ============================================================

print("\n========================================")
print("         RANDOM FOREST")
print("========================================")


modelo = RandomForestClassifier(

    # Número de árboles
    n_estimators=300,

    # Usa todos los núcleos disponibles
    n_jobs=-1,

    # Reproducibilidad
    random_state=42,

    # Compensa diferencias en cantidad
    # de muestras entre letras.
    class_weight="balanced"
)


print(
    "\n🌲 Random Forest creado."
)


# ============================================================
# ENTRENAMIENTO
# ============================================================

print(
    "🧠 Entrenando..."
)


modelo.fit(
    X_train,
    y_train
)


print(
    "✅ Entrenamiento terminado."
)


# ============================================================
# EVALUACIÓN
# ============================================================

print("\n========================================")
print("           EVALUACION")
print("========================================")


y_pred = modelo.predict(
    X_test
)


precision = accuracy_score(
    y_test,
    y_pred
)


print(
    f"\nPrecision general: "
    f"{precision * 100:.2f}%"
)


# ============================================================
# REPORTE POR LETRA
# ============================================================

print("\nReporte por letra:\n")


print(
    classification_report(
        y_test,
        y_pred,
        labels=modelo.classes_,
        zero_division=0
    )
)


# ============================================================
# MATRIZ DE CONFUSIÓN
# ============================================================

print(
    "Matriz de confusion:"
)


matriz = confusion_matrix(
    y_test,
    y_pred,
    labels=modelo.classes_
)


print(
    matriz
)


print(
    "\nOrden de las letras:"
)


print(
    modelo.classes_
)


# ============================================================
# INFORMACIÓN DEL MODELO
# ============================================================

print("\n========================================")
print("       INFORMACION DEL MODELO")
print("========================================")


print(
    f"\nNumero de arboles: "
    f"{modelo.n_estimators}"
)


print(
    f"Numero de caracteristicas: "
    f"{modelo.n_features_in_}"
)


print(
    "Clases aprendidas:"
)


print(
    modelo.classes_
)


# ============================================================
# IMPORTANTE:
# NOMBRES DE LAS CARACTERÍSTICAS
# ============================================================

if hasattr(
    modelo,
    "feature_names_in_"
):

    print(
        "\nPrimeras caracteristicas:"
    )

    print(
        modelo.feature_names_in_[:9]
    )


# ============================================================
# GUARDAR MODELO
# ============================================================

print("\n========================================")
print("          GUARDANDO MODELO")
print("========================================")


joblib.dump(
    modelo,
    RUTA_MODELO
)


# ============================================================
# COMPROBAR QUE SE CREÓ
# ============================================================

if os.path.exists(
    RUTA_MODELO
):

    tamaño = os.path.getsize(
        RUTA_MODELO
    )

    tamaño_mb = (
        tamaño
        /
        (1024 * 1024)
    )


    print(
        "\n✅ MODELO CREADO CORRECTAMENTE"
    )


    print(
        f"\nArchivo:"
    )

    print(
        RUTA_MODELO
    )


    print(
        f"\nTamaño: "
        f"{tamaño_mb:.2f} MB"
    )


else:

    print(
        "\n❌ Hubo un problema "
        "guardando el modelo."
    )


# ============================================================
# FINAL
# ============================================================

print("\n========================================")
print("       ENTRENAMIENTO FINALIZADO")
print("========================================")

print(
    "\nSiguiente paso:"
)

print(
    "python .\\codigos\\03_reconocimiento.py"
)