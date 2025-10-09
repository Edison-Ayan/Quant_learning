import backtrader as bt
import pandas as pd
import numpy as np
from Tool.PandasData import PandasData
from Strategy.strategy_momentum_score import MomentumScoreStrategy

# 加载数据
def load_data(file_path):
    df = pd.read_csv(file_path, index_col='date', parse_dates=True)
    data_feed = PandasData(dataname=df)
    return data_feed

# 运行回测
def run_backtest(data_feed):
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(MomentumScoreStrategy)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    
    print('初始资金: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    print('最终资金: %.2f' % cerebro.broker.getvalue())
    
    # 获取分析结果
    strat = results[0]
    print('夏普比率:', strat.analyzers.sharpe.get_analysis())
    print('最大回撤:', strat.analyzers.drawdown.get_analysis())
    print('收益率:', strat.analyzers.returns.get_analysis())
    
    # 绘制结果
    cerebro.plot(style='candlestick')

if __name__ == '__main__':
    # 替换为您的数据文件路径
    data_file = 'data/600519_stock_20080101_20250630.csv'
    data_feed = load_data(data_file)
    run_backtest(data_feed) 