import backtrader as bt
import pandas as pd
from Strategy.strategy_ma_cross import SmaCross
from Tool.read_csv import read_stock_csv
from Tool.PandasData import PandasData
from cerebro import cerebro
# df = pd.read_csv('data/002415.SZ_daily.csv',parse_dates=['trade_date'])
# df.set_index('trade_date',inplace=True)
# df.rename(columns={'open':'open','high':'high','low':'low','close':'close','vol':'volume'},inplace=True)


df = read_stock_csv('data/000001.SZ_daily.csv')
data = PandasData(dataname=df)



# 修改夏普比率分析器配置，添加时间周期参数
cerebro = cerebro(SmaCross,data,1000000,0.001)
print('初始资金：%.2f'%cerebro.cerebro.broker.getvalue())
result = cerebro.cerebro.run()
print('最终资金：%.2f'%cerebro.cerebro.broker.getvalue())

sharpe = result[0].analyzers.sharpe.get_analysis()
drawdown = result[0].analyzers.drawdown.get_analysis()

# 添加错误处理，防止sharperatio为None
if 'sharperatio' in sharpe and sharpe['sharperatio'] is not None:
    print('夏普比率：%.2f'%sharpe['sharperatio'])
else:
    print('夏普比率：无法计算（数据不足或无交易）')

# 确保drawdown数据有效
if 'max' in drawdown and 'drawdown' in drawdown['max']:
    print('最大回撤：%.2f%%'%drawdown['max']['drawdown'])

cerebro.cerebro.plot(style='candlestick')