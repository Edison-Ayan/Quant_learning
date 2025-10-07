import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor, AdaBoostRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import r2_score, mean_squared_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
import optuna

class ModelTrainer:
    def __init__(self):
        """初始化模型训练器"""
        self.models = [
            LinearRegression(),
            Ridge(random_state=42, alpha=1.0),
            ExtraTreesRegressor(random_state=42),
            GradientBoostingRegressor(random_state=42),
            KNeighborsRegressor(),
            XGBRegressor(random_state=42),
            LGBMRegressor(random_state=42),
            CatBoostRegressor(random_state=42, verbose=False),
            AdaBoostRegressor(random_state=42),
            RandomForestRegressor(random_state=42)
        ]
        
    def evaluate_all_models(self, X_train, y_train, X_test, y_test):
        """评估所有模型"""
        results = {}
        for model in self.models:
            model_name = type(model).__name__
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            rmse = mean_squared_error(y_test, y_pred)
            results[model_name] = {'model': model, 'r2': r2, 'rmse': rmse}
            print(f'{model_name}: R² = {r2:.2f}, 均方误差(Root Mean Squared Error)= {rmse:.2f}')
        return results
    
    def objective(self, trial, X_train, y_train, X_test, y_test):
        """Optuna优化目标函数"""
        params = {
            'alpha': trial.suggest_float('alpha', 0, 5, step=0.05),
            'solver': trial.suggest_categorical('solver', ['svd', 'cholesky', 'lsqr', 'sparse_cg', 'sag', 'saga']),
            'max_iter': trial.suggest_int('max_iter', 1000, 3000, step=200),
            'random_state': 42
        }
        
        tuning = Ridge(**params)
        tuning.fit(X_train, y_train)
        preds = tuning.predict(X_test)
        rmse = np.round(mean_squared_error(y_test, preds), 3)
        return rmse
    
    def train_and_optimize(self, X_train, y_train, X_test, y_test):
        """训练模型并进行超参数优化"""
        # 评估所有模型
        self.evaluate_all_models(X_train, y_train, X_test, y_test)
        
        # 使用Ridge模型进行超参数优化
        study = optuna.create_study(direction='minimize')
        study.optimize(lambda trial: self.objective(trial, X_train, y_train, X_test, y_test), 
                      n_trials=100, show_progress_bar=True)
        
        # 使用最优参数训练模型
        best_model = Ridge(**study.best_params)
        best_model.fit(X_train, y_train)
        y_pred = best_model.predict(X_test)
        
        # 计算评估指标
        r2 = r2_score(y_test, y_pred)
        rmse = mean_squared_error(y_test, y_pred)
        
        print(f"优化后的Ridge模型: R² = {r2:.2f}, RMSE = {rmse:.3f}")
        print(f"最佳参数: {study.best_params}")
        
        return best_model, y_pred, r2, rmse