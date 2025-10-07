import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sklearn.inspection import permutation_importance

class Visualizer:
    def __init__(self):
        """初始化可视化工具"""
        pass
        
    def plot_true_vs_predicted(self, y_test, y_pred, r2, rmse):
        """绘制真实值vs预测值散点图"""
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, label='预测值 vs 真实值')
        plt.xlabel('真实值')
        plt.ylabel('预测值')
        plt.title('True vs. Predicted Values')
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', label='理想拟合线')
        box = dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=1)
        plt.text(plt.xlim()[1], plt.ylim()[0]+0.02, f'R^2: {r2:.2f}', ha="right", va="bottom", wrap=True, bbox=box)
        plt.text(plt.xlim()[1], plt.ylim()[0]*0.85 + 0.02, f'RMSE: {rmse:.3f}', ha="right", va="bottom", wrap=True, bbox=box)
        plt.legend()
        plt.tight_layout()
        plt.show()
        
        # Plotly交互式图表
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(len(y_test))), y=y_test, mode='lines', name='真实值 (True Values)'))
        fig.add_trace(go.Scatter(x=list(range(len(y_test))), y=y_pred, mode='lines', name='预测值 (Predicted Values)'))
        fig.update_layout(title='True vs. Predicted Values', xaxis_title='Index', yaxis_title='Values')
        fig.show()
        
    def plot_feature_importance(self, model, X_test, y_test, feature_names):
        """绘制特征重要性图"""
        # 获得输入特征变量的排列重要性
        result = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42)
        importances = result.importances_mean
        
        # 根据得分（重要性）排序
        indices = importances.argsort()[::-1]
        sorted_features = [feature_names[i] for i in indices]
        sorted_importances = importances[indices]
        
        # 绘制特征变量的重要性图
        fig, ax = plt.subplots(figsize=(8, 15))
        ax.barh(sorted_features, sorted_importances)
        ax.set_yticklabels(sorted_features)
        ax.set_ylabel('特征')
        ax.set_xlabel('重要性')
        ax.set_title('特征重要性')
        plt.tight_layout()  # 自动调整布局，避免标签重叠
        plt.show()