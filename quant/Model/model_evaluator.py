import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

class ModelEvaluator:
    def __init__(self):
        """初始化模型评估器"""
        pass
        
    def evaluate_model(self, y_test, y_pred):
        """评估模型性能，生成混淆矩阵"""
        # 将模型预测收益率转换成为0/1信号
        y_pred_class = np.where(y_pred > 0, 1, 0)
        
        # 对真实值预测收益转化为0/1信号
        y_test_class = np.where(y_test > 0, 1, 0)
        
        # 创建混淆矩阵
        conf_matrix = confusion_matrix(y_test_class, y_pred_class)
        
        # 将结果转换成百分数% -- 便于可视化
        conf_matrix = conf_matrix / np.sum(conf_matrix) * 100
        
        # 绘制配置矩阵
        plt.figure(figsize=(8, 6))
        sns.heatmap(conf_matrix, annot=True, cmap='Blues', fmt='.2f')
        plt.title('混淆矩阵')
        plt.xlabel('预测值')
        plt.ylabel('真实值')
        plt.tight_layout()
        plt.show()