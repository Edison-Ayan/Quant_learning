import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.dates import DateFormatter

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def plot_k_line(df, symbol):
    """
    绘制原始K线图
    
    参数:
    df (pandas.DataFrame): 包含OHLC数据的DataFrame，索引为时间
    symbol (str): 合约代码
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # 设置时间格式化器
    date_format = DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(date_format)
    
    # 绘制K线图
    for i in range(len(df)):
        date = df.index[i]
        open_price = df.loc[date, 'open']
        close_price = df.loc[date, 'close']
        high_price = df.loc[date, 'high']
        low_price = df.loc[date, 'low']
        
        # 确定K线颜色（收盘价高于开盘价为红色，否则为绿色）
        color = 'red' if close_price >= open_price else 'green'
        
        # 绘制蜡烛线
        ax.plot([date, date], [low_price, high_price], color=color, linewidth=1)
        ax.bar(date, abs(close_price - open_price), bottom=min(open_price, close_price), 
                width=0.0005, color=color)
    
    ax.set_title(f'{symbol} K线图')
    ax.set_xlabel('时间')
    ax.set_ylabel('价格')
    ax.grid(True)
    
    plt.tight_layout()
    
    # 创建保存目录（如果不存在）
    os.makedirs('data', exist_ok=True)
    
    # 保存图片
    image_path = f'data/{symbol}_k_line.png'
    plt.savefig(image_path)
    print(f"K线图已保存至：{image_path}")
    
    plt.show()


def main():
    # 合约代码（与get_hs300_csv.py中的设置保持一致）
    ts_code = "IF2309.CFX"
    
    # 数据文件路径
    csv_path = f'data/{ts_code}_data.csv'
    
    # 检查文件是否存在
    if not os.path.exists(csv_path):
        print(f"错误：数据文件 {csv_path} 不存在。请先运行get_hs300_csv.py获取数据。")
        return
    
    # 读取数据
    print(f"正在读取数据文件：{csv_path}")
    df = pd.read_csv(csv_path, parse_dates=['trade_time'], index_col='trade_time')
    
    print(f"数据形状：{df.shape}")
    print(f"数据时间范围：{df.index.min()} 至 {df.index.max()}")
    print("数据前5行：")
    print(df.head())
    
    # 绘制K线图
    print("\n正在绘制K线图...")
    plot_k_line(df, ts_code)
    
    print("\nK线图绘制完成！")


if __name__ == "__main__":
    main()