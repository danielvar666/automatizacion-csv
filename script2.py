import pandas as pd
import os

print("--- CONFIGURACIÓN DE FORMATO (SCRIPT 2) ---")

# 1. Preguntar al usuario los nombres de grupo deseados para el día de hoy
grupo_samsung = input("¿Qué nombre de grupo quieres para Samsung? (ej. ventaft_samsung): ")
grupo_generico = input("¿Qué nombre de grupo quieres para Genérico? (ej. ventaft_generico): ")

def process_mobile_data(input_file, output_file, grupo_nombre):
    # Verificar que el archivo generado por el script 1 exista
    if not os.path.exists(input_file):
        print(f"Error: No se encontró el archivo {input_file}")
        return

    # Leer el archivo CSV generado por script1.py
    df = pd.read_csv(input_file, dtype=str)
    
    # Crear el nuevo DataFrame con la estructura requerida
    df_output = pd.DataFrame({
        "event_header.country": "co",
        "event_header.customer_type": "prepaid_mobile",
        "event_header.customer_action": "purchase",
        "event_header.event_source": "co_migration",
        "event_header.event_name": "co_mobile_migra_pre2pos_121_018000",
        "customer_profile.anonymous_id": df["MSISDN"],
        "customer_profile.phone_number_main_contact": df["MSISDN"],
        "event_data.grupo": grupo_nombre,
        "event_data.mes": "octubre"
    })
    
    # Guardar el resultado formateado
    df_output.to_csv(output_file, index=False)
    print(f"Archivo procesado y guardado en: {output_file}")

# 2. Procesar ambos segmentos
print("\nAplicando formato...")
process_mobile_data("samsung_output.csv", "co_mobile_ft_vac_samsung_final.csv", grupo_samsung)
process_mobile_data("generico_output.csv", "co_mobile_ft_vac_generico_final.csv", grupo_generico)

print("\n¡Script 2 completado exitosamente!")