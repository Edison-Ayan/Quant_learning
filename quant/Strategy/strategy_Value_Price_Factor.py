import backtrader as bt
import numpy as np

class VolumePriceFactor(bt.Strategy):
    """
    基于价格和成交量的量化因子策略
    买入信号：
    1. 股价小于20日均线
    2. 成交量大于20日均额的两倍
    
    能被backtrader的cerebro引擎直接使用
    """
    
    params = dict(
        window=20,          # 计算均线的窗口大小
        printlog=False      # 是否打印日志
    )
    
    def __init__(self):
        """
        初始化策略
        """
        # 保存参数
        self.window = self.params.window
        
        # 保存数据引用
        self.dataclose = self.datas[0].close
        self.datavolume = self.datas[0].volume   
        
        # 计算20日均线
        self.ma20 = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, period=self.window)
        
        # 计算20日均量（使用Talib的SMA来计算）
        self.volume_ma20 = bt.indicators.SimpleMovingAverage(
            self.datavolume, period=self.window)
        
        # 记录交易状态
        self.buy_signals = []
        self.trades = []
        self.buy_price = 0
        self.buy_date = None
        self.sell_signals = []
        self.sell_price = 0
        self.sell_date = None
        
    def log(self, txt, dt=None, doprint=False):
        """
        记录策略日志
        """
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')
    
    def next(self):
        """
        每个交易日执行一次
        """
        # 检查是否有持仓
        if self.position.size == 0:
            # 没有持仓，检查买入条件
            # 条件1: 收盘价小于20日均线
            condition1 = self.dataclose[0] < self.ma20[0]
            
            # 条件2: 成交量大于20日均量的两倍
            condition2 = self.datavolume[0] > 2 * self.volume_ma20[0]
            
            # 同时满足两个条件时买入
            if condition1 and condition2:
                # 买入信号
                self.buy_signals.append(self.datas[0].datetime.date(0))
                self.log(f'买入信号: 价格={self.dataclose[0]:.2f}, 20日均线={self.ma20[0]:.2f}')
                
                # 计算买入数量（这里使用总资金的10%）
                size = int(self.broker.getvalue()  / self.dataclose[0])
                
                # 执行买入
                self.buy(size=size)
                self.buy_price = self.dataclose[0]
                self.buy_date = self.datas[0].datetime.date(0)
        else:
            # 有持仓，检查卖出条件
            # 条件1: 收盘价大于20日均线
            condition1 = self.dataclose[0] > self.ma20[0]
            
            # 条件2: 成交量大于20日均量的两倍
            condition2 = self.datavolume[0] > 2 * self.volume_ma20[0]
            
            # 如果持有超过设定的周期，则卖出
            if condition1 and condition2:
                self.sell_signals.append(self.datas[0].datetime.date(0))
                self.log(f'卖出信号: 价格={self.dataclose[0]:.2f}, 20日均线={self.ma20[0]:.2f}')
                
                # 记录交易结果
                profit = (self.dataclose[0] - self.buy_price) / self.buy_price
                self.trades.append({
                    'entry_date': self.buy_date,
                    'exit_date': self.datas[0].datetime.date(0),
                    'entry_price': self.buy_price,
                    'exit_price': self.dataclose[0],
                    'profit': profit
                })
                
                # 执行卖出
                self.sell(size=self.position.size)
                self.buy_price = 0
                self.buy_date = None
    
    def notify_order(self, order):
        """
        订单状态变化时的回调
        """
        if order.status in [order.Submitted, order.Accepted]:
            # 订单已提交或已接受，不需要操作
            return
        
        # 检查订单是否已完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入成交: 价格={order.executed.price:.2f}, 数量={order.executed.size}')
            elif order.issell():
                self.log(f'卖出成交: 价格={order.executed.price:.2f}, 数量={order.executed.size}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单 取消/保证金不足/拒绝')
    
    def notify_trade(self, trade):
        """
        交易状态变化时的回调
        """
        if not trade.isclosed:
            return
        
        self.log(f'交易利润: 毛利={trade.pnl:.2f}, 净利={trade.pnlcomm:.2f}')
    
    def stop(self):
        """
        策略结束时调用
        """
        self.log(f'最终资金: {self.broker.getvalue():.2f}', doprint=True)
        
        # 打印交易统计
        if self.trades:
            profits = [t['profit'] for t in self.trades]
            avg_profit = np.mean(profits)
            win_rate = len([p for p in profits if p > 0]) / len(profits)
            
            self.log(f'交易统计: 总交易次数={len(self.trades)}, 平均收益率={avg_profit:.2%}, 胜率={win_rate:.2%}', doprint=True)
    
    def get_buy_signals(self):
        """
        获取所有买入信号的日期
        """
        return self.buy_signals
    
    def get_trade_results(self):
        """
        获取所有交易结果
        """
        return self.trades
    
    def evaluate_performance(self):
        """
        评估策略表现
        """
        if not self.trades:
            return {
                'total_signals': len(self.buy_signals),
                'total_trades': 0,
                'average_profit': 0,
                'win_rate': 0
            }
        
        profits = [t['profit'] for t in self.trades]
        avg_profit = np.mean(profits)
        win_rate = len([p for p in profits if p > 0]) / len(profits)
        total_profit = np.sum(profits)
        
        return {
            'total_signals': len(self.buy_signals),
            'total_trades': len(self.trades),
            'average_profit': avg_profit,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'max_profit': max(profits) if profits else 0,
            'min_profit': min(profits) if profits else 0
        }

#后续需要补充天价天量做空的部分
#熊市低位放量是最佳买入时机