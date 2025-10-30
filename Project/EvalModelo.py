from sklearn.model_selection import RepeatedKFold, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import ElasticNet
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np

# Núcleos paralelos por defecto
N_JOBS = -1

# XGBoost opcional
try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except Exception:
    XGBOOST_AVAILABLE = False

class Evaluador:
    def __init__(
        self,
        df: pd.DataFrame,
        target: str = "PowerConsumption_Zone2",
        num_cols = ('Temperature','Humidity','WindSpeed','GeneralDiffuseFlows','DiffuseFlows'),
        feature_range=(1,2),
        train_ratio: float = 0.80,
        random_state: int = 42
    ):
        self.df = df.copy()
        self.target = target
        self.num_cols = list(num_cols)
        self.feature_range = feature_range
        self.train_ratio = train_ratio
        self.random_state = random_state

        self.df.columns=['Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows',
       'DiffuseFlows','PowerConsumption_Zone1',
       'PowerConsumption_Zone2', 'PowerConsumption_Zone3' ,'Day',
       'Month', 'Hour', 'Minute', 'DayWeek', 'QuarterYear',
       'DayYear']

        # split temporal como en tu código
        n = len(self.df)
        i = int(n * self.train_ratio)

        self.X = self.df.drop(columns=['PowerConsumption_Zone1','PowerConsumption_Zone2','PowerConsumption_Zone3'])
        self.y = self.df[[self.target]]

        self.x_train, self.y_train = self.X.iloc[:i], self.y.iloc[:i].values.ravel()
        self.x_test,  self.y_test  = self.X.iloc[i:],  self.y.iloc[i:].values.ravel()

        # preprocesamiento
        self.num_pipeline = Pipeline(steps=[
            ('impMediana', SimpleImputer(strategy='median')),
            ('escalaNum', MinMaxScaler(feature_range=self.feature_range)),
        ])
        self.ct = ColumnTransformer(
            transformers=[('numpipe', self.num_pipeline, self.num_cols)],
            remainder='passthrough'
        )

        # modelos
        self.modelos, self.nombres = self._mis_modelos()

        # salidas
        self.cv_results_ = None
        self.best_name_ = None
        self.best_estimator_ = None          # modelo base
        self.best_pipeline_ = None           # pipeline(ct + modelo) entrenado en train
        self.test_rmse_ = None

    def _mis_modelos(self):
        modelos, nombres = [], []

        modelos.append(RandomForestRegressor(
            n_estimators=700, min_samples_split=2, min_samples_leaf=1,
            max_features=3, random_state=self.random_state, n_jobs=N_JOBS
        )); nombres.append('RandomForest')

        modelos.append(ElasticNet(
            alpha=0.1, l1_ratio=0.5, random_state=self.random_state, max_iter=5000
        )); nombres.append('ElasticNet')

        modelos.append(GradientBoostingRegressor(
            n_estimators=500, learning_rate=0.05, max_depth=5,
            min_samples_split=5, min_samples_leaf=3, random_state=self.random_state
        )); nombres.append('GradientBoosting')

        if XGBOOST_AVAILABLE:
            modelos.append(XGBRegressor(
                n_estimators=500, learning_rate=0.05, max_depth=5,
                random_state=self.random_state, n_jobs=N_JOBS
            )); nombres.append('XGBoost')

        modelos.append(SVR(kernel='rbf', C=100, epsilon=0.1, gamma='scale'))
        nombres.append('SVR')

        return modelos, nombres

    def cross_validate(self, n_splits=5, n_repeats=2, scoring='neg_mean_squared_error'):
        cv = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=8)
        filas = []
        detalles = {}

        for modelo, nombre in zip(self.modelos, self.nombres):
            pipe = Pipeline(steps=[('ct', self.ct), ('m', modelo)])
            mse_scores = cross_val_score(
                pipe, self.x_train, self.y_train,
                scoring=scoring, cv=cv, n_jobs=N_JOBS
            )
            rmse = np.sqrt(-mse_scores)
            filas.append({'model': nombre, 'rmse_mean': rmse.mean(), 'rmse_std': rmse.std()})
            detalles[nombre] = rmse

        self.cv_results_ = pd.DataFrame(filas).sort_values('rmse_mean').reset_index(drop=True)
        return self.cv_results_, detalles

    def fit_best(self):
        if self.cv_results_ is None or self.cv_results_.empty:
            self.cross_validate()

        self.best_name_ = self.cv_results_.iloc[0]['model']
        idx = self.nombres.index(self.best_name_)
        self.best_estimator_ = self.modelos[idx]

        self.best_pipeline_ = Pipeline(steps=[('ct', self.ct), ('m', self.best_estimator_)])
        self.best_pipeline_.fit(self.x_train, self.y_train)

        preds = self.best_pipeline_.predict(self.x_test)
        self.test_rmse_ = float(np.sqrt(mean_squared_error(self.y_test, preds)))
        return self.best_pipeline_, self.test_rmse_

    def get_best(self):
        if self.best_pipeline_ is None:
            raise RuntimeError("Aún no hay modelo entrenado. Llama a fit_best().")
        return {
            'name': self.best_name_,
            'pipeline': self.best_pipeline_,
            'test_rmse': self.test_rmse_,
            'cv_table': self.cv_results_.copy()
        }