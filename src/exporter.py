# Author: Danilo Oliveira (https://github.com/Dann-Oliv)
# Excel export module

import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd


def export_to_excel(dataframe: pd.DataFrame, sheet_name: str) -> None:
    """
    Exporta DataFrame para arquivo Excel.

    Args:
        dataframe (pd.DataFrame): DataFrame a ser exportado
        sheet_name (str): Nome da planilha/arquivo
    """
    sheet_folder = Path(f"{os.getcwd()}/out")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_path = Path(f"{sheet_folder}/{sheet_name}_{timestamp}.xlsx")

    os.makedirs(sheet_folder, exist_ok=True)

    dataframe.to_excel(
        excel_writer=full_path,
        sheet_name="Results",
        index=False,
    )
    logging.info(f"Planilha salva com sucesso em: {full_path}")
