import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from typing import Dict, Any, Tuple


class PredictiveModels:
    def __init__(self):
        self.models = self._get_models()
        self.trained_models = {}

    def _get_models(self) -> Dict[str, Any]:
        return {
            "rf": RandomForestRegressor(n_estimators=100),
            "xgb": xgb.XGBRegressor(objective="reg:squarederror"),
        }

    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        metrics = {}
        for model_name, model in self.models.items():
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            metrics[model_name] = mse
            self.trained_models[model_name] = model
        return metrics

    def cross_validate(
        self, X: np.ndarray, y: np.ndarray, cv: int = 5
    ) -> Dict[str, float]:
        metrics = {}
        for model_name, model in self.models.items():
            scores = cross_val_score(
                model, X, y, scoring="neg_mean_squared_error", cv=cv
            )
            metrics[model_name] = -np.mean(scores)
        return metrics

    def predict(self, model_name: str, X: np.ndarray) -> np.ndarray:
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} has not been trained.")
        model = self.trained_models[model_name]
        return model.predict(X)

    def get_model(self, model_name: str) -> Any:
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} has not been trained.")
        return self.trained_models[model_name]

    async def train_models(self, data: pd.DataFrame) -> Dict:
        X, y = self._prepare_data(data)
        models_performance = {}

        for model_name, model in self._get_models().items():
            performance = await self._train_and_evaluate(model, X, y, model_name)
            models_performance[model_name] = performance

        return models_performance

    async def generate_predictions(
        self, data: pd.DataFrame, horizon: int = 7
    ) -> Dict[str, pd.DataFrame]:
        predictions = {}
        features = self._generate_features(data)

        for model_name, model in self.models.items():
            try:
                pred = await self._generate_model_predictions(model, features, horizon)
                predictions[model_name] = pred
            except Exception as e:
                print(f"Error generating predictions for {model_name}: {e}")

        return self._combine_predictions(predictions)

    def _prepare_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        features = self._generate_features(data)
        target = self._generate_target(data)
        return features, target

    def _generate_features(self, data: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame()

        # Technical indicators
        features["rsi"] = self._calculate_rsi(data["close"])
        features["macd"] = self._calculate_macd(data["close"])
        features["bb_upper"], features["bb_lower"] = self._calculate_bollinger_bands(
            data["close"]
        )

        # Volume metrics
        features["volume_sma"] = data["volume"].rolling(window=20).mean()
        features["volume_std"] = data["volume"].rolling(window=20).std()

        # Price metrics
        features["returns"] = data["close"].pct_change()
        features["volatility"] = features["returns"].rolling(window=20).std()

        return features.dropna()

    async def _train_and_evaluate(
        self, model: object, X: pd.DataFrame, y: pd.Series, model_name: str
    ) -> Dict:
        tscv = TimeSeriesSplit(n_splits=5)
        metrics = {"mae": [], "rmse": [], "r2": []}

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            model.fit(X_train, y_train)
            predictions = model.predict(X_test)

            metrics["mae"].append(self._calculate_mae(y_test, predictions))
            metrics["rmse"].append(self._calculate_rmse(y_test, predictions))
            metrics["r2"].append(self._calculate_r2(y_test, predictions))

        self.models[model_name] = model
        return {k: np.mean(v) for k, v in metrics.items()}

    def _calculate_mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return mean_absolute_error(y_true, y_pred)

    def _calculate_rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return np.sqrt(mean_squared_error(y_true, y_pred))

    def _calculate_r2(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return r2_score(y_true, y_pred)

    def evaluate_model(
        self, model_name: str, X: np.ndarray, y: np.ndarray
    ) -> Dict[str, float]:
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} has not been trained.")
        model = self.trained_models[model_name]
        tscv = TimeSeriesSplit(n_splits=5)
        metrics = {"mae": [], "rmse": [], "r2": []}
        for train_index, test_index in tscv.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            metrics["mae"].append(self._calculate_mae(y_test, predictions))
            metrics["rmse"].append(self._calculate_rmse(y_test, predictions))
            metrics["r2"].append(self._calculate_r2(y_test, predictions))

        self.models[model_name] = model
        return {k: np.mean(v) for k, v in metrics.items()}
