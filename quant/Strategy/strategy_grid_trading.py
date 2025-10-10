import backtrader as bt
import numpy as np

class GridTradingStrategy(bt.Strategy):
    params = dict(
        grid_spacing=0.02,    # 网格间距（百分比）
        grid_levels=10,       # 网格层数
        initial_cash_ratio=0.2,  # 初始资金用于建仓的比例
        use_atr=True,         # 启用ATR自动调整网格间距
        atr_period=14,        # ATR计算周期
        atr_multiplier=2.0,   # ATR倍数，用于计算网格间距
        rebalance_days=20,    # 重新计算网格的周期（天）
        move_threshold=0.3    # 价格偏离基准价格的阈值，超过后移动网格
    )
    
    def __init__(self):
        """
        初始化网格交易策略
        """
        # 记录交易订单
        self.orders = []
        
        # 记录网格线
        self.buy_grid_lines = []
        self.sell_grid_lines = []
        
        # 记录当前持仓数量
        self.position_count = 0
        
        # 初始化ATR指标（如果启用）
        if self.p.use_atr:
            self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)
        
        # 记录策略初始化时的价格作为基准价格
        self.base_price = None
        self.trade_count = 0
        self.days_since_rebalance = 0
        
    def start(self):
        """
        策略启动时执行
        """
        # 设置基准价格（使用第一个可用的收盘价）
        if self.data.close[0] > 0:
            self.base_price = self.data.close[0]
            self._initialize_grid()
    
    def _initialize_grid(self):
        """
        初始化网格线
        """
        if self.base_price is None:
            return
        
        # 计算网格间距
        if self.p.use_atr and self.atr[0] > 0:
            grid_spacing = self.atr[0] * self.p.atr_multiplier
        else:
            grid_spacing = self.base_price * self.p.grid_spacing
        
        # 清空之前的网格线
        self.buy_grid_lines = []
        self.sell_grid_lines = []
        
        # 创建买入和卖出网格线
        for i in range(1, self.p.grid_levels + 1):
            # 买入网格线（低于基准价格）
            buy_price = self.base_price - i * grid_spacing
            self.buy_grid_lines.append(buy_price)
            
            # 卖出网格线（高于基准价格）
            sell_price = self.base_price + i * grid_spacing
            self.sell_grid_lines.append(sell_price)
        
        # 按价格排序
        self.buy_grid_lines.sort(reverse=True)  # 从高到低排序
        self.sell_grid_lines.sort()             # 从低到高排序
        
        # 计算每格的交易数量
        self.cash_per_grid = self.broker.getvalue() * self.p.initial_cash_ratio / self.p.grid_levels
    
    def next(self):
        """
        每个交易日执行一次
        """
        # 如果基准价格未设置，尝试设置它
        if self.base_price is None and self.data.close[0] > 0:
            self.base_price = self.data.close[0]
            self._initialize_grid()
            return
        
        # 如果网格线未初始化，返回
        if not self.buy_grid_lines or not self.sell_grid_lines:
            return
        
        # 取消所有未执行的订单
        self._cancel_open_orders()
        
        # 获取当前价格
        current_price = self.data.close[0]
        
        # 检查买入条件
        self._check_buy_conditions(current_price)
        
        # 检查卖出条件
        self._check_sell_conditions(current_price)
        # 定期重新计算网格或当价格大幅偏离时移动网格
        self.days_since_rebalance += 1
        
        # 检查是否需要重新平衡网格
        if (self.days_since_rebalance >= self.p.rebalance_days or 
            abs(current_price - self.base_price) / self.base_price >= self.p.move_threshold):
            self.base_price = current_price  # 更新基准价格为当前价格
            self._initialize_grid()          # 重新初始化网格
            self.days_since_rebalance = 0    # 重置计数器
    
    def _cancel_open_orders(self):
        """
        取消所有未执行的订单
        """
        for order in self.orders[:]:
            if order.status in [order.Submitted, order.Accepted]:
                self.cancel(order)
                self.orders.remove(order)
    
    def _check_buy_conditions(self, current_price):
        """
        检查买入条件
        """
        # 获取可用资金
        available_cash = self.broker.getcash()
        
        # 检查是否触发买入网格线
        for buy_price in self.buy_grid_lines:
            if current_price <= buy_price and available_cash >= self.cash_per_grid:
                # 计算购买数量
                size = int(self.cash_per_grid / current_price)
                if size > 0:
                    # 下买单
                    buy_order = self.buy(size=size)
                    self.orders.append(buy_order)
                    self.position_count += 1
                    print(f"买入: 价格={current_price:.2f}, 数量={size}, 网格价格={buy_price:.2f}")
                    # 避免重复买入
                    break
    
    def _check_sell_conditions(self, current_price):
        """
        检查卖出条件
        """
        # 当前持仓数量
        current_position = self.position.size
        
        # 检查是否触发卖出网格线
        if current_position > 0:
            for sell_price in self.sell_grid_lines:
                if current_price >= sell_price:
                    # 计算卖出数量（可以选择全部卖出或部分卖出）
                    size = int(current_position / self.p.grid_levels) if self.position_count > 0 else current_position
                    size = max(1, size)  # 至少卖出1股
                    
                    # 下卖单
                    sell_order = self.sell(size=size)
                    self.orders.append(sell_order)
                    self.position_count = max(0, self.position_count - 1)
                    print(f"卖出: 价格={current_price:.2f}, 数量={size}, 网格价格={sell_price:.2f}")
                    # 避免重复卖出
                    break
    
    def notify_order(self, order):
        """
        订单状态变化时的回调函数
        """
        # 从订单列表中移除已完成的订单
        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            if order in self.orders:
                self.orders.remove(order)
    
    def stop(self):
        """
        策略结束时执行
        """
        print(f"最终资金: {self.broker.getvalue():.2f}")
        print(f"最终持仓: {self.position.size}")