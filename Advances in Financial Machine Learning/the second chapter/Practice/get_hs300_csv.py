import tushare as ts
import pandas as pd
import os

ts.set_token('4802ae7acc89b1e849a7c9d39078c638213502e945c5c1d886ed877d')
pro = ts.pro_api()

ts_code = "IF2309.CFX"
start_date='2023-08-25 09:00:00'
end_date='2023-08-25 19:00:00'
freq = "1min"

try:
    df = pro.ft_mins(
        ts_code=ts_code,
        freq=freq,
        start_date=start_date,
        end_date=end_date
    )
    if df.empty:
        print("数据为空")
    df['trade_time'] = pd.to_datetime(df['trade_time'])
    # 按时间升序排序（确保序列连续性）
    df = df.sort_values('trade_time').reset_index(drop=True)
        
    # 保留关键字段（时间、开高低收、成交量）
    result = df[['trade_time', 'open', 'high', 'low', 'close', 'vol','amount']]
    result = result.set_index('trade_time')
except Exception as e:
    print("failure",e)
    df = None
os.makedirs('data', exist_ok=True)
csv_path = f'data/{ts_code}_data.csv'
df.to_csv(csv_path)
print(f"数据保存至：{csv_path}")