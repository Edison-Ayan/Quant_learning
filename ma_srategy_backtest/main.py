import backtrader as bt
import pandas as pd
from strategy_ma_cross import SmaCross

df = pd.read_csv('data/000001.SZ.csv',parase_dates=['trade_date'])
df.set_index('trade_date',inplace=True)
df.rename(columns={'open':'open','high':'high','low':'low','close':'close','vol':'volume'},inplace=True)

class PandasData(bt.feeds.PandasData):
    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', -1),
    )

data = PandasData(dataname=df)

#回测引擎
cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)
cerebro.adddata(data)
cerebro.broker.set_cash(10000)
cerebro.broker.setcommission(commission=0.001)

cerebro.addanalyzer(bt.analyzers.SharpeRatio,_name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown,_name='drawdown')

print('初始资金：%.2f'%cerebro.broker.getvalue())
result = cerebro.run()
print('最终资金：%.2f'%cerebro.broker.getvalue())

sharpe = result[0].analyzers.sharpe.get_analysis()
drawdown = result[0].analyzers.drawdown.get_analysis()
print('夏普比率：%.2f'%sharpe['sharperatio'])
print('最大回撤：%.2f%%'%drawdown['max']['drawdown'])
#bt.analyzers.SharpeRatio：夏普比率分析器，核心指标之一，计算公式为 (策略收益率 - 无风险利率) / 策略收益率标准差，数值越高表示单位风险带来的收益越高（默认无风险利率为 0）
#bt.analyzers.DrawDown：最大回撤分析器，衡量策略从历史最高点到后续最低点的最大跌幅，反映策略的风险承受能力

cerebro.plot(style='candlestick')

#由于Backtrader 内置的 talib.py 模块 和 你安装的 TA-Lib 库版本不兼容
#修改了G:\Anaconda\envs\quant_env\lib\site-packages\backtrader\talib.py
