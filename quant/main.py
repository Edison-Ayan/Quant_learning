import backtrader as bt
import pandas as pd
from quant.Strategy.strategy_ma_cross import SmaCross
from Tool.read_csv import read_stock_csv
from Tool.PandasData import PandasData

# df = pd.read_csv('data/002415.SZ_daily.csv',parse_dates=['trade_date'])
# df.set_index('trade_date',inplace=True)
# df.rename(columns={'open':'open','high':'high','low':'low','close':'close','vol':'volume'},inplace=True)


df = read_stock_csv('data/002415.SZ_daily.csv')
data = PandasData(dataname=df)

#回测引擎
cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)
cerebro.adddata(data)
cerebro.broker.set_cash(1000000)
cerebro.broker.setcommission(commission=0.001)

# 修改夏普比率分析器配置，添加时间周期参数
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days, compression=1)
cerebro.addanalyzer(bt.analyzers.DrawDown,_name='drawdown')

print('初始资金：%.2f'%cerebro.broker.getvalue())
result = cerebro.run()
print('最终资金：%.2f'%cerebro.broker.getvalue())

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

cerebro.plot(style='candlestick')