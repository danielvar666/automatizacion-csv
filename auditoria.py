from datetime import datetime
import json
import os
import sys
from zoneinfo import ZoneInfo

from google.oauth2.service_account import Credentials
import gspread


def main():
    usuario_id = sys.argv[1]
    usuario_nombre = sys.argv[2]
    ini_sam = int(sys.argv[3])
    cant_sam = int(sys.argv[4])
    filtro_sam = sys.argv[5]
    ini_gen = int(sys.argv[6])
    cant_gen = int(sys.argv[7])
    filtro_gen = sys.argv[8]
    estado = sys.argv[9]

    with open("estado.json", "r", encoding="utf-8") as f:
        datos = json.load(f)
    fin_sam = datos.get("inicio_samsung", ini_sam)
    fin_gen = datos.get("inicio_generico", ini_gen)

    rango_sam = f"{ini_sam + 1} - {fin_sam}" if estado == "Exitoso" else "N/A"
    rango_gen = f"{ini_gen + 1} - {fin_gen}" if estado == "Exitoso" else "N/A"

    creds_raw = os.getenv("GCP_SERVICE_ACCOUNT", "")
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "").strip()

    creds_dict = json.loads(creds_raw)
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1

    ahora_col = datetime.now(ZoneInfo("America/Bogota"))
    fila = [
        ahora_col.strftime("%Y-%m-%d"),
        ahora_col.strftime("%H:%M:%S"),
        str(usuario_id),
        str(usuario_nombre),
        cant_sam,
        rango_sam,
        str(filtro_sam),
        cant_gen,
        rango_gen,
        str(filtro_gen),
        str(estado),
    ]
    sheet.append_row(fila)
    print("Bitácora actualizada correctamente en Google Sheets.")


if __name__ == "__main__":
    main()