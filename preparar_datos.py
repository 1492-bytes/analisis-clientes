"""
Este script se corre UNA SOLA VEZ (y cada vez que actualices el Excel).
Convierte las hojas pesadas del Excel a un formato mucho más rápido de leer,
para que el dashboard cargue en segundos en vez de minutos.
"""
import pandas as pd

ARCHIVO = "BASE DE DATOS 2022 AL 2026 NOVA.xlsx"

print("Leyendo hoja de clientes (SEGMENTACION DE CLIENTES RFM)...")
clientes = pd.read_excel(ARCHIVO, sheet_name="SEGMENTACION DE CLIENTES RFM", dtype={"TEL": str})
clientes.to_parquet("clientes.parquet", index=False)
print(f"  Listo: {len(clientes)} clientes guardados en clientes.parquet")

print("Leyendo hoja de ventas (BASE DE DATOS)... esto puede tardar unos minutos, solo se hace una vez.")
cols = ["BODEGA", "FECHA", "IDCLIENTE", "ESTABLECIMIENTO", "DESCRIPCION",
        "CANTIDAD", "MARCA", "FOLIO PEDIDO", "MONTO", "TOTAL"]
ventas = pd.read_excel(ARCHIVO, sheet_name="BASE DE DATOS", usecols=cols)
ventas.to_parquet("ventas.parquet", index=False)
print(f"  Listo: {len(ventas)} filas de ventas guardadas en ventas.parquet")

print()
print("TODO LISTO. Ya puedes correr el dashboard normalmente con:")
print("  py -m streamlit run dashboard.py")