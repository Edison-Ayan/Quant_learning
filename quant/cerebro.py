import backtrader as bt

class cerebro:
    def __init__(self,strategy,data,cash,commission):
        self.cerebro = bt.Cerebro()
        self.cerebro.addstrategy(strategy)
        self.cerebro.adddata(data)
        self.cerebro.broker.set_cash(cash)
        self.cerebro.broker.setcommission(commission)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', timeframe=bt.TimeFrame.Days, compression=1)
        self.cerebro.addanalyzer(bt.analyzers.DrawDown,_name='drawdown')
