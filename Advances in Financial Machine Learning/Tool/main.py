import pandas as pd
import os
from draw_k_lines import plot_sz_stock_kline
from read_csv import read_csv
from Triple_Barrier_Method import TripleBarrierMethod
from getBins import getBins
def main():
    # 股票代码
    ts_code = '000001.SZ'
    
    df = read_csv(ts_code)
    
    plot_sz_stock_kline(df, ts_code)
    
    events = TripleBarrierMethod(df)

    if isinstance(events, pd.DataFrame) and 't1' in events.columns:
        # 获取收盘价序列用于计算收益率
        close = df['close']
        
        # 使用getBins函数获取标签
        bins = getBins(events, close)
        
        # 输出标签结果
        print(f"\n使用getBins获取的标签结果：")
        print(bins)
        
        # 统计标签分布
        print(f"\n标签统计：")
        print(f"盈利事件数量（bin=1）: {(bins['bin'] == 1).sum()}")
        print(f"亏损事件数量（bin=0）: {(bins['bin'] == 0).sum()}")
        # 合并事件和标签结果，便于分析
        combined = pd.concat([events, bins], axis=1)
        print(f"\n合并的事件和标签数据：")
        print(combined)
    else:
        print("\n警告：未获取到有效的事件数据或事件数据缺少't1'列")
        print("请检查TripleBarrierMethod函数的实现和返回值")
if __name__ == "__main__":
    main()