import pandas as pd
from getDailyVol import getDailyVol
from CUSUM_filter import getTEvents
from applyPtSlOnT1 import applyPtSlOnT1
def TripleBarrierMethod(df):
    close = df['close']  
    
    
    vol_series = getDailyVol(close, span0=30)
    # 增加阈值倍数，默认为1.5，可以根据需要调整为2.0或更高
    threshold_multiplier = 20
    h = vol_series * threshold_multiplier  # 使用每日回报的标准差的倍数作为阈值
    
    t_events = getTEvents(close, h)
    
    print(f"发现 {len(t_events)} 个事件")  
    
    # 如果没有事件，提前返回  
    if len(t_events) == 0:
        print("没有找到符合条件的事件")
        return  
    
    # 3. 直接应用止盈止损规则，不使用多进程
    print("应用止盈止损规则...")
    
    # 设置参数
    pt_sl = (1.0, 1.0)  # 止盈止损比例，元组形式(pt倍数, sl倍数)
    
    # 创建events DataFrame，包含t1、trgt和side列
    # t1: 事件的结束时间
    # trgt: 目标阈值
    # side: 交易方向
    events = pd.DataFrame(index=t_events)
    
    # 创建时间限制：每个事件最大持有20天
    # 使用更简单的方式创建t1
    t1 = []
    valid_indices = []
    
    for event_time in t_events:
        try:
            future_date = event_time + pd.Timedelta(days=20)
            # 找到大于等于future_date的第一个索引位置
            idx = close.index.searchsorted(future_date)
            
            if idx < len(close):
                t1.append(close.index[idx])
                valid_indices.append(event_time)
        except:
            continue
    
    # 过滤有效的事件
    if len(valid_indices) > 0:
        events = events.loc[valid_indices]
        events['t1'] = t1
    else:
        print("没有创建有效的时间限制，使用默认结束时间")
        # 使用数据的最后一个时间戳作为默认结束时间
        events['t1'] = close.index[-1]
    
    # 添加目标阈值和交易方向
    # 注意：我们需要确保daily_vol和events的索引匹配
    # 这里使用reindex方法来匹配索引，并填充缺失值
    events['trgt'] = vol_series.reindex(events.index, method='ffill')
    events['side'] = 1  # 默认多头
    
    # 移除trgt为空的事件
    events = events.dropna(subset=['trgt'])
    
    print(f"有效事件数量：{len(events)}")
    
    if len(events) == 0:
        print("没有找到有效的事件")
        return
    
    # 直接调用applyPtSlOnT1函数，不使用多进程
    # 使用events的索引作为molecule参数
    out = applyPtSlOnT1(close, events, pt_sl, events.index)
    
    # 合并结果
    events = pd.concat([events, out[['sl', 'pt']]], axis=1)
    
    # 4. 显示结果  
    print(f"处理后的事件数量：{len(events)}")  
    pd.set_option('display.max_rows', None)  # 显示所有行
    pd.set_option('display.max_columns', None)  # 显示所有列
    pd.set_option('display.width', None)  # 自动调整显示宽度
    print(events)  
    
    # 5. 分析触发情况
    # 统计触发止盈、止损的事件数量
    pt_triggered = events['pt'].notnull().sum()
    sl_triggered = events['sl'].notnull().sum()
    
    print(f"\n触发止盈的事件数量：{pt_triggered}")
    print(f"触发止损的事件数量：{sl_triggered}")
    
    print("\n策略应用完成！")