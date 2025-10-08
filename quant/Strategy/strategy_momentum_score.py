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
        # 计算收益率
        returns = []
        for i in range(1, len(self.close_history)):
            returns.append((self.close_history[i] - self.close_history[i-1]) / self.close_history[i-1])
        
        # 计算年化收益率（假设一年252个交易日）
        recent_returns = returns[-self.p.lookback_period:]
        total_return = 1.0
        for r in recent_returns:
            total_return *= (1 + r)
        annualized_return = (total_return ** (252 / len(recent_returns))) - 1
        
        # 计算R平方
        # 准备线性回归数据
        X = np.arange(len(recent_returns)).reshape(-1, 1)
        y = np.array(recent_returns)
        
        # 线性回归
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        
        # 计算R平方
        ss_total = np.sum((y - np.mean(y)) ** 2)
        ss_residual = np.sum((y - y_pred) ** 2)
        r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
        
        # 计算EWMA
        # 首先计算价格的对数收益率，用于EWMA计算
        log_prices = np.log(self.close_history[-self.p.lookback_period:])
        log_returns = np.diff(log_prices)
        
        # 计算EWMA波动率
        ewma_volatility = self.calculate_ewma_volatility(log_returns, self.p.ewma_period)
        
        # 计算动量分：年化收益 × R平方 / EWMA
        # 避免除以零的情况
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