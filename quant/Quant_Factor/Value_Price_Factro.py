import pandas as pd
import numpy as np

class VolumePriceFactor:
    """
    基于价格和成交量的量化因子
    买入信号：
    1. 股价小于20日均线
    2. 成交额大于20日均额的两倍
    """
    
    def __init__(self, window=20):
        """
        初始化因子
        
        参数:
            window: 计算均线的窗口大小，默认20
        """
        self.window = window
        self.signals = None
        
    def calculate_factor(self, data):
        """
        计算量化因子和买入信号
        
        参数:
            data: 包含'close'(收盘价)和'amount'(成交额)列的DataFrame
        
        返回:
            包含原始数据和因子值的DataFrame
        """
        # 创建数据副本以避免修改原始数据
        df = data.copy()
        
        # 计算20日均线
        df['ma20'] = df['close'].rolling(window=self.window).mean()
        
        # 计算20日均额
        df['amount_ma20'] = df['amount'].rolling(window=self.window).mean()
        
        # 生成买入信号
        # 条件1: 收盘价小于20日均线
        condition1 = df['close'] < df['ma20']
        
        # 条件2: 成交额大于20日均额的两倍
        condition2 = df['amount'] > 2 * df['amount_ma20']
        
        # 合并两个条件，同时满足时产生买入信号(1)
        df['buy_signal'] = np.where(condition1 & condition2, 1, 0)
        
        # 记录买入信号出现的日期
        self.signals = df[df['buy_signal'] == 1].index
        
        return df
        
    def get_signals(self):
        """
        获取所有买入信号的日期
        
        返回:
            买入信号日期的索引
        """
        return self.signals
        
    def evaluate_performance(self, data):
        """
        评估因子的表现
        
        参数:
            data: 包含价格数据的DataFrame
        
        返回:
            包含表现评估指标的字典
        """
        # 计算因子值
        df = self.calculate_factor(data)
        
        # 计算买入信号数量
        total_signals = len(self.signals)
        
        # 计算成功率（简单版本：假设在信号出现后持有n天）
        if total_signals > 0:
            # 回测持有期（可以根据需要调整）
            holding_period = 5
            
            # 计算每个信号后的收益
            profits = []
            for signal_date in self.signals:
                try:
                    # 找到信号日期在DataFrame中的位置
                    signal_idx = df.index.get_loc(signal_date)
                    
                    # 确保不会超出数据范围
                    if signal_idx + holding_period < len(df):
                        # 信号日收盘价
                        entry_price = df.iloc[signal_idx]['close']
                        # 持有期结束后的收盘价
                        exit_price = df.iloc[signal_idx + holding_period]['close']
                        # 计算收益率
                        profit = (exit_price - entry_price) / entry_price
                        profits.append(profit)
                except:
                    # 处理可能的异常
                    continue
            
            # 计算平均收益率和成功率
            if profits:
                avg_profit = np.mean(profits)
                win_rate = len([p for p in profits if p > 0]) / len(profits)
            else:
                avg_profit = 0
                win_rate = 0
        else:
            avg_profit = 0
            win_rate = 0
            total_signals = 0
        
        # 返回评估结果
        performance = {
            'total_signals': total_signals,
            'average_profit': avg_profit,
            'win_rate': win_rate
        }
        
        return performance

# 示例用法
if __name__ == "__main__":
    # 这里是示例用法，实际使用时需要导入数据
    try:
        # 假设我们有一个数据加载函数
        from Tool.data_loader import DataLoader
        
        # 加载数据
        data_loader = DataLoader(use_local_data=True)
        stock_data = data_loader.load_stock_data(["600519"])  # 加载贵州茅台数据作为示例
        
        if stock_data:
            # 使用第一只股票的数据
            df = stock_data[0]
            
            # 创建并使用因子
            factor = VolumePriceFactor(window=20)
            result = factor.calculate_factor(df)
            
            # 输出买入信号
            signals = factor.get_signals()
            print(f"找到{len(signals)}个买入信号")
            if len(signals) > 0:
                print(f"最近的5个买入信号日期: {signals[-5:]}")
            
            # 评估因子表现
            performance = factor.evaluate_performance(df)
            print(f"因子表现评估:")
            print(f"总信号数: {performance['total_signals']}")
            print(f"平均收益率: {performance['average_profit']:.2%}")
            print(f"胜率: {performance['win_rate']:.2%}")
    except Exception as e:
        print(f"示例运行出错: {e}")
        print("请确保您已正确导入数据并安装所需依赖")