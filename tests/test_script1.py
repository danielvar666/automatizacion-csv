import pytest
import pandas as pd

# Función lógica de rebanado basada en script1.py
def procesar_lote(df, inicio, cantidad):
    if df.empty:
        raise ValueError("El DataFrame de entrada está vacío")
    
    fin = inicio + cantidad
    lote = df.iloc[inicio:fin]
    nuevo_inicio = fin if fin < len(df) else len(df)
    return lote, nuevo_inicio

# --- PRUEBAS UNITARIAS ---

def test_procesar_lote_exito():
    """Verifica que el rebanado extraiga la cantidad exacta y actualice el índice."""
    datos_prueba = pd.DataFrame({"MSISDN": [f"300000000{i}" for i in range(50)]})
    lote, nuevo_inicio = procesar_lote(datos_prueba, inicio=0, cantidad=10)
    
    assert len(lote) == 10
    assert nuevo_inicio == 10

def test_procesar_lote_limite():
    """Verifica el comportamiento cuando se piden más registros de los disponibles."""
    datos_prueba = pd.DataFrame({"MSISDN": [f"300000000{i}" for i in range(5)]})
    lote, nuevo_inicio = procesar_lote(datos_prueba, inicio=2, cantidad=10)
    
    assert len(lote) == 3
    assert nuevo_inicio == 5

def test_dataframe_vacio_lanza_error():
    """Verifica que detecte si el CSV está vacío."""
    df_vacio = pd.DataFrame()
    with pytest.raises(ValueError, match="El DataFrame de entrada está vacío"):
        procesar_lote(df_vacio, inicio=0, cantidad=5)