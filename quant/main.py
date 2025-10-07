import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from Tool.data_loader import DataLoader
from Tool.feature_selector import FeatureSelector
from Model.model_trainer import ModelTrainer
from Tool.visualizer import Visualizer
from Model.model_evaluator import ModelEvaluator

# 设置中文字体显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def main():
    # 1. 加载数据
    data_loader = DataLoader(use_local_data=True)
    stock_codes = ["600519", "002230", "000333"]
    indices_codes = ["000001", "399001", "000300"]
    
    stock_datas = data_loader.load_stock_data(stock_codes)
    index_datas = data_loader.load_index_data(indices_codes)
    
    Sz_Index = index_datas[1]  # 使用深圳成分指数
    
    # 2. 分割训练测试集
    train, test = data_loader.split_train_test(Sz_Index)
    
    # 3. 特征选择
    feature_selector = FeatureSelector()
    X_train, y_train, X_test, y_test, features = feature_selector.select_features(train, test, k=43)
    
    # 4. 模型训练
    model_trainer = ModelTrainer()
    best_model, y_pred, r2, rmse = model_trainer.train_and_optimize(X_train, y_train, X_test, y_test)
    
    # 5. 可视化
    visualizer = Visualizer()
    visualizer.plot_true_vs_predicted(y_test, y_pred, r2, rmse)
    visualizer.plot_feature_importance(best_model, X_test, y_test, features)
    
    # 6. 模型评估
    evaluator = ModelEvaluator()
    evaluator.evaluate_model(y_test, y_pred)

if __name__ == "__main__":
    main()