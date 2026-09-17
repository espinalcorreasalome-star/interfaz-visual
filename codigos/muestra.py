try:
    import os
    print(f"📂 Carpeta actual: {os.getcwd()}")
    print(f"📄 Archivos en esa carpeta: {os.listdir('.')}")
    
    self.modelo_lsc = joblib.load('modelo_lsc.pkl')
    self.lsc_enabled = True
    print("✅ Modelo LSC cargado correctamente")
except FileNotFoundError:
    self.modelo_lsc = None
    self.lsc_enabled = False
    print("❌ ARCHIVO NO ENCONTRADO en la carpeta mostrada arriba")
except Exception as e:
    self.modelo_lsc = None
    self.lsc_enabled = False
    print(f"❌ Error específico: {type(e).__name__}: {e}")
    