import pandas as pd
import numpy as np  

# getBins函数用于为交易事件生成分类标签，基于事件结束时的收益率
# 参数:
#   events: DataFrame, 包含交易事件信息，必须包含't1'列表示事件结束时间
#   close: Series, 价格序列（通常是收盘价）
# 返回值:
#   DataFrame, 包含每个事件的收益率('ret')和分类标签('bin')
def getBins(events, close):
    # 过滤掉没有结束时间(t1)的事件
    events_ = events.dropna(subset=['t1'])
    
    # 创建一个包含事件开始时间和结束时间的索引，并去除重复值
    # events_.index 是事件开始时间，events_['t1'].values 是事件结束时间
    px = events_.index.union(events_['t1'].values).drop_duplicates()
    
    # 使用向后填充方法(bfill)重新索引收盘价数据，确保每个时间点都有价格
    px = close.reindex(px, method='bfill')
    
    # 创建一个输出DataFrame，索引与过滤后的事件相同
    out = pd.DataFrame(index=events_.index)
    
    # 计算每个事件从开始到结束的收益率: 结束价格/开始价格
    # px.loc[events_['t1'].values] 获取所有事件结束时间点的价格
    # px.loc[events_.index] 获取所有事件开始时间点的价格
    out['ret'] = px.loc[events_['t1'].values].values / px.loc[events_.index]-1
    if 'side' in events_:out['ret']*=events_['side']
    
    # 根据收益率的符号确定交易标签：1表示正收益，-1表示负收益，0表示无变化
    out['bin'] = np.sign(out['ret'])
    if 'side' in events_:
        out.loc[out['ret']<=0,'bin']=0
    # 返回包含收益率和分类标签的结果
    return out