# 定义 objective（）函数
import optuna
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
import numpy as np
def objective(trial, X_train_kbest, y_train, X_test_kbest, y_test):
    # 定义不同的参数设置来迭代，这些参数选项怎么设置，Spyder中 Ctrl+I 快速查询 Ridge()函数说明
    params = {
        'alpha': trial.suggest_float('alpha', 0, 5, step=0.05),
        'solver': trial.suggest_categorical('solver', ['svd', 'cholesky', 'lsqr', 'sparse_cg', 'sag', 'saga']),
        'max_iter': trial.suggest_int('max_iter', 1000, 3000, step=200),
        'random_state': 42
    }

    # 拟合 & 预测
    tuning = Ridge(**params)  # 注意这里使用的是 Ridge模型，与我们上述最优模型选择相一致
    tuning.fit(X_train_kbest, y_train)
    preds = tuning.predict(X_test_kbest)

    # 计算RMSE(均方误差根- Root Mean Square Error score)
    rmse = np.round(mean_squared_error(y_test, preds), 3)
    return rmse