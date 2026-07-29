import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble         import RandomForestClassifier
from sklearn.model_selection  import train_test_split, cross_val_score
from sklearn.preprocessing    import LabelEncoder
from sklearn.metrics          import classification_report, accuracy_score

# ── Configuración ─────────────────────────────────────────────────────────────
ARCHIVO_CSV    = "dat_lsc.csv"
ARCHIVO_MODELO = "model_NS.pkl"
MINIMO_MUESTRAS_POR_CLASE = 20   # advierte si alguna letra tiene muy pocas
# ──────────────────────────────────────────────────────────────────────────────


def verificar_datos(df):
    """Revisa calidad del dataset y advierte problemas."""
    print("\n📊 Resumen del dataset:")
    print(f"   Total muestras : {len(df)}")
    print(f"   Letras únicas  : {sorted(df['label'].unique())}")
    print(f"   Features       : {df.shape[1] - 1}")

    conteo = df["label"].value_counts()
    print("\n   Muestras por letra:")
    for letra, n in sorted(conteo.items()):
        barra  = "█" * (n // 5)
        estado = "✅" if n >= MINIMO_MUESTRAS_POR_CLASE else "⚠️ "
        print(f"   {estado} {letra}: {n:>4}  {barra}")

    letras_bajas = conteo[conteo < MINIMO_MUESTRAS_POR_CLASE]
    if not letras_bajas.empty:
        print(f"\n⚠️  Letras con pocas muestras (< {MINIMO_MUESTRAS_POR_CLASE}): "
              f"{list(letras_bajas.index)}")
        print("   El modelo puede tener baja precisión en esas letras.")
    return True


def entrenar():
    # ── 1. Cargar datos ──────────────────────────────────────────────────────
    if not os.path.exists(ARCHIVO_CSV):
        print(f"❌ No se encontró '{ARCHIVO_CSV}'.")
        print("   Primero ejecuta: python recolectar_datos.py")
        return

    df = pd.read_csv(ARCHIVO_CSV)

    if df.empty:
        print("❌ El archivo CSV está vacío.")
        return

    verificar_datos(df)

    # ── 2. Preparar X e y ────────────────────────────────────────────────────
    feature_cols = [c for c in df.columns if c != "label"]
    X = df[feature_cols].values.astype(np.float32)
    y = df["label"].values

    # Codificar etiquetas
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    print(f"\n🔀 Dividiendo datos (80% entrenamiento / 20% prueba)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    # ── 3. Entrenar Random Forest ────────────────────────────────────────────
    print("\n🏋️  Entrenando Random Forest...")
    modelo = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1          # usa todos los núcleos disponibles
    )
    modelo.fit(X_train, y_train)

    # ── 4. Evaluar ───────────────────────────────────────────────────────────
    y_pred  = modelo.predict(X_test)
    acc     = accuracy_score(y_test, y_pred)

    print(f"\n📈 Precisión en datos de prueba: {acc * 100:.2f}%")

    if acc >= 0.95:
        print("   ✅ Excelente precisión.")
    elif acc >= 0.85:
        print("   🟡 Buena precisión. Puedes agregar más muestras para mejorar.")
    else:
        print("   🔴 Precisión baja. Agrega más muestras y asegúrate de hacer")
        print("      las señas con buena iluminación y desde distintos ángulos.")

    # Reporte por clase
    print("\n📋 Reporte por letra:")
    report = classification_report(
        y_test, y_pred,
        target_names=le.inverse_transform(sorted(set(y_test)))
    )
    print(report)

    # Validación cruzada (5-fold) — opcional pero informativo
    print("🔄 Validación cruzada (5-fold)...")
    cv_scores = cross_val_score(modelo, X, y_enc, cv=5, scoring="accuracy", n_jobs=-1)
    print(f"   Media: {cv_scores.mean() * 100:.2f}% ± {cv_scores.std() * 100:.2f}%")

    # ── 5. Guardar modelo ────────────────────────────────────────────────────
    # Guardamos el modelo junto con el LabelEncoder para decodificar predicciones
    bundle = {
        "modelo"  : modelo,
        "encoder" : le,
        "features": feature_cols,
        "clases"  : list(le.classes_)
    }
    joblib.dump(bundle, ARCHIVO_MODELO)
    print(f"\n💾 Modelo guardado en '{ARCHIVO_MODELO}'")
    print(f"   Clases: {list(le.classes_)}")
    print("\n✅ ¡Listo! Copia 'modelo_lsc.pkl' a la carpeta de NordSign y ejecuta la app.")


def probar_modelo():
    """Carga el modelo guardado y hace una predicción de prueba."""
    if not os.path.exists(ARCHIVO_MODELO):
        print(f"❌ No existe '{ARCHIVO_MODELO}' todavía.")
        return

    bundle  = joblib.load(ARCHIVO_MODELO)
    modelo  = bundle["modelo"]
    encoder = bundle["encoder"]
    clases  = bundle["clases"]

    # Predicción con vector de ceros (solo para verificar que carga bien)
    dummy   = np.zeros((1, 63))
    pred_id = modelo.predict(dummy)[0]
    pred    = encoder.inverse_transform([pred_id])[0]

    print(f"\n🧪 Test de carga del modelo: OK")
    print(f"   Clases disponibles : {clases}")
    print(f"   Predicción de prueba (vector cero): '{pred}' (normal que sea cualquier letra)")


if __name__ == "__main__":
    entrenar()
    probar_modelo()