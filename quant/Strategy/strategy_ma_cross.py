import backtrader as bt

class SmaCross(bt.Strategy):
    params = dict(short=10, long=30)
    #定义短期均线和长期均线

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.short)
        sma2 = bt.ind.SMA(period=self.p.long)
        #计算短期与长期移动平均线

        self.crossover = bt.ind.CrossOver(sma1, sma2)
        #检测两条均线交叉情况
        #sma1上穿sm2指标为正，下穿指标为负

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.close()
        #如果sma1下穿sma2,则关闭仓位
        #如果sma1上穿sma2,则开启仓位