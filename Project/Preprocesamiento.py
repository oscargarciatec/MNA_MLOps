from dataclasses import dataclass
import pandas as pd
from pathlib import Path
from Project.CargaDatos import CargaArchivos

# ==========================
# PREPROCESAMIENTO
# ==========================
@dataclass
class Preprocesamiento:
    """Transforma el dataset modificado en un dataset listo para modelar.
    Pasos realizados:
    - Elimina columna "mixed_type_col" si existe.
    - Limpia y convierte DateTime con distintos formatos.
    - Imputa DateTime faltante con vecino a ±10 min o punto medio.
    - Imputa numéricos con mediana por columna.
    - Maneja outliers mediante IQR + mediana rodante (ventana configurable).
    - Crea variables de tiempo y elimina DateTime si se solicita.
    """

    @staticmethod
    def _tranformar_numerica(df: pd.DataFrame) -> pd.DataFrame:
        cols = df.columns[1:9]
        df[cols] = (
            df[cols]
            .astype(str)
            .apply(lambda s: s.str.replace(',', '.', regex=False).str.strip())
            .apply(pd.to_numeric, errors='coerce')
        )
        df[cols].dtypes
        return df

    @staticmethod
    def _drop_col_si_existe(df: pd.DataFrame, col: str) -> pd.DataFrame:
        return df.drop(columns=[col], errors="ignore")

    @staticmethod
    def _limpiar_parsear_datetime(df: pd.DataFrame, col: str) -> pd.DataFrame:
        s = (
            df[col].astype(str)
            .str.replace(r"[\r\n\t]+", " ", regex=True)
            .str.strip()
        )
        s = s.mask(s.eq(""))
        s = s.mask(s.str.lower().eq("nan"))

        dt = pd.to_datetime(s, errors="coerce")
        miss = dt.isna()
        # Segundo intento con formato explícito mm/dd/YYYY HH:MM
        dt.loc[miss] = pd.to_datetime(
            s[miss], format="%m/%d/%Y %H:%M", errors="coerce"
        )

        # Imputación por vecinos: 10 minutos o punto medio
        prev = dt.shift(1)
        nxt = dt.shift(-1)
        mask = dt.isna() & prev.notna() & nxt.notna()

        m10 = mask & ((nxt - prev) == pd.Timedelta(minutes=20))
        dt.loc[m10] = prev.loc[m10] + pd.Timedelta(minutes=10)

        m_mid = mask & dt.isna()
        if m_mid.any():
            mid_ns = (prev[m_mid].astype("int64") + nxt[m_mid].astype("int64")) // 2
            dt.loc[m_mid] = pd.to_datetime(mid_ns)

        df[col] = dt

        valid = df['DateTime'].notna() & ~df['DateTime'].astype(str).str.strip().str.lower().eq('nan')
        df['__score__'] = df.drop(columns=['DateTime']).notna().sum(axis=1)
        keep = (df.loc[valid]
                .sort_values(['DateTime','__score__'], ascending=[True, False])
                .drop_duplicates(subset=['DateTime'], keep='first'))

        df= (pd.concat([keep, df.loc[~valid]])
                                    .drop(columns='__score__')
                                    .sort_index()
                                    .reset_index(drop=True))
        return df
    
    @staticmethod
    def _imputar_numericos_mediana(df: pd.DataFrame) -> pd.DataFrame:
        num_cols = df.select_dtypes(include="number").columns
        medianas = df[num_cols].median()
        df[num_cols] = df[num_cols].fillna(medianas)
        return df
    
    @staticmethod
    def _outliers_mediana_rodante(df: pd.DataFrame, col_fecha: str, ventana_mediana: int) -> pd.DataFrame:
        df = df.sort_values(col_fecha).copy()
        num = df.select_dtypes("number").columns

        Q1, Q3 = df[num].quantile(0.25), df[num].quantile(0.75)
        IQR = Q3 - Q1
        lo, hi = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        mask = (df[num] < lo) | (df[num] > hi)

        for c in num:
            rmed = df[c].rolling(window=ventana_mediana, center=True, min_periods=1).median()
            df.loc[mask[c], c] = rmed[mask[c]].fillna(df[c].median())
        
        df=df.dropna()
        return df
    
    @staticmethod
    def _features_tiempo(df: pd.DataFrame, col_fecha: str) -> pd.DataFrame:
        dt = df[col_fecha]
        df["Day"] = dt.dt.day
        df["Month"] = dt.dt.month
        df["Hour"] = dt.dt.hour
        df["Minute"] = dt.dt.minute
        df["Day of Week"] = dt.dt.dayofweek + 1
        # Quarter
        df["Quarter of Year"] = pd.cut(
            df["Month"],
            bins=[0, 3, 6, 9, 12],
            labels=[1, 2, 3, 4],
            include_lowest=True,
        ).astype(int)
        # Day of Year
        df["Day of Year"] = dt.dt.strftime('%j').astype(int)
        return df

    @staticmethod
    def _finalizar(df: pd.DataFrame, col_fecha: str, eliminar_datetime: bool) -> pd.DataFrame:
        df = df.dropna().copy()
        if eliminar_datetime and col_fecha in df.columns:
            df = df.drop(columns=[col_fecha])
        return df

    @staticmethod
    def ejecutar(df_modificado: pd.DataFrame, *, ventana_mediana: int, eliminar_datetime: bool) -> pd.DataFrame:
        df = df_modificado.copy()
        df = Preprocesamiento._tranformar_numerica(df)
        df = Preprocesamiento._drop_col_si_existe(df, "mixed_type_col")
        df = Preprocesamiento._limpiar_parsear_datetime(df, "DateTime")
        df = Preprocesamiento._imputar_numericos_mediana(df)
        df = Preprocesamiento._outliers_mediana_rodante(df, "DateTime", ventana_mediana)
        df = Preprocesamiento._features_tiempo(df, "DateTime")
        df = Preprocesamiento._finalizar(df, "DateTime", eliminar_datetime)
        return df


    @staticmethod
    def correr_pipeline(
        carpeta_raw: str | Path = "../data/raw",
        carpeta_processed: str | Path = "../data/processed",
        nombre_salida: str = "power_tetouan_city_processed1.csv",
        nombre_modificado: str = "power_tetouan_city_modified.csv",
        ventana_mediana: int = 25,
        eliminar_datetime: bool = True,
    ) -> Path:
        carpeta_processed = Path(carpeta_processed)
        carpeta_processed.mkdir(parents=True, exist_ok=True)

        loader = CargaArchivos(carpeta_raw, nombre_modificado)
        df_modificado = loader.leer()

        df_final = Preprocesamiento.ejecutar(df_modificado,ventana_mediana=ventana_mediana,eliminar_datetime=eliminar_datetime,)

        ruta_out = carpeta_processed / nombre_salida
        df_final.to_csv(ruta_out, index=False)
        return ruta_out
