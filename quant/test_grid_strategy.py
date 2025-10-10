import backtrader as bt
import pandas as pd
import numpy as np
from Tool.PandasData import PandasData
from Strategy.strategy_grid_trading import GridTradingStrategy

# 加载数据
def load_data(file_path):
    df = pd.read_csv(file_path, index_col='date', parse_dates=True)
    data_feed = PandasData(dataname=df)
    return data_feed

# 运行回测
def run_backtest(data_feed):
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    
    # 添加网格交易策略，可以根据需要调整参数
    cerebro.addstrategy(GridTradingStrategy,
                        grid_spacing=0.02,     # 网格间距为2%
                        grid_levels=10,        # 10层网格
                        initial_cash_ratio=0.5, # 初始资金50%用于建仓
                        use_atr=False)         # 不使用ATR自动调整网格
    
    # 设置初始资金
    cerebro.broker.setcash(1000000.0)
    
    # 设置佣金
    cerebro.broker.setcommission(commission=0.0001)
    
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