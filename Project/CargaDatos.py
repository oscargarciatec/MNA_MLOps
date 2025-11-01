from dataclasses import dataclass
from pathlib import Path
import pandas as pd

@dataclass
class CargaDatasets:
    """Carga datasets crudos desde una carpeta.

    Parámetros
    ----------
    carpeta_raw: str | Path
        Ruta a la carpeta que contiene los CSVs crudos.
    nombre_modificado: str
        Nombre del CSV "modificado". power_tetouan_city_modified.csv
    """    

    carpeta_raw: Path
    nombre_modificado: str

    def __post_init__(self) -> None:
        self.carpeta_raw = Path(self.carpeta_raw)
        self.carpeta_raw.mkdir(parents=True, exist_ok=True)

    def leer(self) -> pd.DataFrame:
        na_vals = ["nan", "NAN", "NaT", ""]
        df_modificado = pd.read_csv(
            self.carpeta_raw / self.nombre_modificado,
            na_values=na_vals,
            keep_default_na=True,
        )
        return df_modificado