import backtrader as bt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

class MomentumScoreStrategy(bt.Strategy):
    params = dict(
        lookback_period=20,  # 计算动量分的回溯期
        ewma_period=10,      # EWMA的周期参数
        score_threshold=0.5  # 动量分阈值，超过该值时买入
    )
    
    def __init__(self):
        # 存储价格历史数据
        self.close_history = []
        self.momentum_score = None
        
    def next(self):
        # 记录收盘价历史
        self.close_history.append(self.data.close[0])
        
        # 确保有足够的历史数据来计算动量分
        if len(self.close_history) >= self.p.lookback_period:
            # 计算动量分
            self.momentum_score = self.calculate_momentum_score()
            
            # 交易逻辑
            if not self.position and self.momentum_score > self.p.score_threshold:
                # 当没有仓位且动量分大于阈值时买入
                self.buy()
                print(f"买入: 价格={self.data.close[0]}, 动量分={self.momentum_score}")
            elif self.position and self.momentum_score < -self.p.score_threshold:
                # 当有仓位且动量分小于负阈值时卖出
                self.close()
                print(f"卖出: 价格={self.data.close[0]}, 动量分={self.momentum_score}")
    
    def calculate_momentum_score(self):
        """
        计算动量分：年化收益 × R平方 / EWMA
        该指标综合考量了资产的收益性、趋势持续性和波动性，用于捕捉市场动量
        
        返回值：
            float: 计算得到的动量分数，正值表示上涨动量，负值表示下跌动量
        """
        # 计算日度收益率序列
        returns = []
        for i in range(1, len(self.close_history)):
            # 计算相邻两日的收益率：(今日收盘价-昨日收盘价)/昨日收盘价
            returns.append((self.close_history[i] - self.close_history[i-1]) / self.close_history[i-1])
        
        # 计算回溯期内的年化收益率（假设一年252个交易日）
        recent_returns = returns[-self.p.lookback_period:]  # 获取最近lookback_period个收益率
        total_return = 1.0
        for r in recent_returns:
            # 使用复利计算总收益
            total_return *= (1 + r)
        # 将总收益转换为年化收益率
        annualized_return = (total_return ** (252 / len(recent_returns))) - 1
        
        # 计算R平方值，衡量收益率的线性趋势强度
        # 准备线性回归数据：X为时间序列(0,1,2,...)，y为收益率序列
        X = np.arange(len(recent_returns)).reshape(-1, 1)  # 重塑为二维数组以适应sklearn
        y = np.array(recent_returns)
        
        # 执行线性回归，拟合收益率的时间趋势
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)  # 获取预测的收益率值
        
        # 计算R平方：1 - (残差平方和/总平方和)
        ss_total = np.sum((y - np.mean(y)) ** 2)  # 总平方和（离均差平方和）
        ss_residual = np.sum((y - y_pred) ** 2)   # 残差平方和（预测误差平方和）
        # 避免除以零的情况，当总平方和为0时，R平方设为0
        r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
        
        # 计算EWMA（指数加权移动平均）波动率
        # 首先计算价格的对数收益率，用于波动率计算
        log_prices = np.log(self.close_history[-self.p.lookback_period:])  # 取对数价格
        log_returns = np.diff(log_prices)  # 计算对数收益率
        
        # 调用专用方法计算EWMA波动率
        ewma_volatility = self.calculate_ewma_volatility(log_returns, self.p.ewma_period)
        
        # 计算最终动量分：年化收益 × R平方 / EWMA波动率
        # 避免除以零的情况，当波动率为0时，动量分设为0
        if ewma_volatility == 0:
            momentum_score = 0
        else:
            momentum_score = annualized_return * r_squared / ewma_volatility
        
        return momentum_score
    
    def calculate_ewma_volatility(self, returns, period):
        # 计算EWMA波动率
        if len(returns) < period:
            return 0
        
        # EWMA参数
        lambda_ = 2 / (period + 1)
        
        # 初始化波动率
        volatility = 0
        weights = []
        
        # 计算加权平方收益率
        for i, ret in enumerate(reversed(returns)):
            weight = (1 - lambda_) ** i
            weights.append(weight)
            volatility += weight * (ret ** 2)
        
        # 归一化权重
        if sum(weights) > 0:
            volatility /= sum(weights)
        
        # 年化波动率
        annualized_vol = np.sqrt(volatility * 252)
        
        return annualized_vol

    def stop(self):
        if self.momentum_score is not None:
            print(f"最终动量分: {self.momentum_score}")
        print(f"最终资金: {self.broker.getvalue():.2f}")