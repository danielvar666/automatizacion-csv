import pandas as pd
import json
import os

ARCHIVO_ESTADO = "estado.json"

# 1. Cargar o inicializar el estado del acumulador
if os.path.exists(ARCHIVO_ESTADO):
    with open(ARCHIVO_ESTADO, "r") as f:
        estado = json.load(f)
else:
    # Si es el primer día, empieza en 0
    estado = {"inicio_samsung": 0, "inicio_generico": 0}

print(f"Posición inicial de hoy -> Samsung: {estado['inicio_samsung']}, Genérico: {estado['inicio_generico']}")

# 2. Preguntar la cantidad a procesar hoy
cant_samsung = int(input("¿Cuántos registros necesitas para Samsung hoy?: "))
cant_generico = int(input("¿Cuántos registros necesitas para Genérico hoy?: "))

# 3. Leer bases de datos
df = pd.read_csv("BASE VAC 2.csv", dtype=str)
base = pd.read_csv("VAC.csv", dtype=str, usecols=["MSISDN"])

# 4. Cruce de bases
resultado = base.merge(
    df[["MSISDN", "marca_dvc_act", "municipio"]],
    how="inner",
    left_on="MSISDN",
    right_on="MSISDN"
).drop_duplicates(subset="MSISDN", keep="first")

# 5. Filtrar Samsung usando la posición guardada
samsung = resultado[resultado["marca_dvc_act"] == "Samsung"]
idx_s_inicio = estado["inicio_samsung"]
idx_s_fin = idx_s_inicio + cant_samsung
samsung_out = samsung.iloc[idx_s_inicio:idx_s_fin]
samsung_out.to_csv("samsung_output.csv", index=False)

# 6. Filtrar Genérico usando la posición guardada
generico = resultado[~resultado["marca_dvc_act"].isin(["Samsung"])]
idx_g_inicio = estado["inicio_generico"]
idx_g_fin = idx_g_inicio + cant_generico
generico_out = generico.iloc[idx_g_inicio:idx_g_fin]
generico_out.to_csv("generico_output.csv", index=False)

# 7. Actualizar y guardar el nuevo estado para el día siguiente
estado["inicio_samsung"] = idx_s_fin
estado["inicio_generico"] = idx_g_fin

with open(ARCHIVO_ESTADO, "w") as f:
    json.dump(estado, f, indent=4)

print(f"\n¡Paso 1 completado con éxito!")
print(f"Nueva posición guardada para mañana -> Samsung: {idx_s_fin}, Genérico: {idx_g_fin}")