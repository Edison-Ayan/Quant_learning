import pandas as pd
import os
from draw_k_lines import plot_sz_stock_kline
from read_csv import read_csv
from Triple_Barrier_Method import TripleBarrierMethod
def main():
    # 股票代码
    ts_code = '000001.SZ'
    
    df = read_csv(ts_code)
    
    # 绘制K线图
    plot_sz_stock_kline(df, ts_code)
    
    # -------------------------  
    # 应用止盈止损规则  
    # -------------------------  
    # 假设我们使用close价格列  
    TripleBarrierMethod(df)

if __name__ == "__main__":
    main()