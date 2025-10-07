import numpy as np
import talib as ta
import pandas as pd

def feature_engineering(df):
    """
    特征工程，添加技术指标和滞后特征
    """
    # 创建DataFrame的副本以避免SettingWithCopyWarning
    df = df.copy()
    
    # 使用.loc设置新列以避免警告
    df.loc[:, 'high_low_ratio'] = df['high'] / df['low']
    df.loc[:, 'open_close_ratio'] = df['open'] / df['close']
    df.loc[:, 'candle_to_wick_ratio'] = (df['close'] - df['open']) / (df['high'] - df['low'])
    df.loc[:, 'candle_to_wick_ratio'] = df['candle_to_wick_ratio'].replace([np.inf, -np.inf], 0)

    # 添加滞后特征
    df.loc[:, 'close_lag1'] = df['close'].shift(1)
    df.loc[:, 'close_lag2'] = df['close'].shift(2)
    df.loc[:, 'close_lag3'] = df['close'].shift(3)
    df.loc[:, 'close_lag5'] = df['close'].shift(5)

    df.loc[:, 'Close_lag1_ratio'] = df['close'] / df['close_lag1']
    df.loc[:, 'Close_lag2_ratio'] = df['close'] / df['close_lag2']
    df.loc[:, 'Close_lag3_ratio'] = df['close'] / df['close_lag3']
    df.loc[:, 'Close_lag5_ratio'] = df['close'] / df['close_lag5']

    # 将数据转换为float64类型以兼容TA-Lib
    close_float = df['close'].astype(np.float64).values
    high_float = df['high'].astype(np.float64).values
    low_float = df['low'].astype(np.float64).values
    volume_float = df['volume'].astype(np.float64).values
    
    # 使用正确的TA-Lib函数计算移动平均线
    df.loc[:, 'sma10'] = ta.SMA(close_float, timeperiod=10)
    df.loc[:, 'sma20'] = ta.SMA(close_float, timeperiod=20)
    df.loc[:, 'sma80'] = ta.SMA(close_float, timeperiod=80)
    df.loc[:, 'sma100'] = ta.SMA(close_float, timeperiod=100)

    df.loc[:, 'Close_sma10_ratio'] = df['close'] / df['sma10']
    df.loc[:, 'Close_sma20_ratio'] = df['close'] / df['sma20']
    df.loc[:, 'Close_sma80_ratio'] = df['close'] / df['sma80']
    df.loc[:, 'Close_sma100_ratio'] = df['close'] / df['sma100']

    df.loc[:, 'sma10_sma20_ratio'] = df['sma10'] / df['sma20']
    df.loc[:, 'sma20_sma80_ratio'] = df['sma20'] / df['sma80']
    df.loc[:, 'sma80_sma100_ratio'] = df['sma80'] / df['sma100']
    df.loc[:, 'sma10_sma80_ratio'] = df['sma10'] / df['sma80']
    df.loc[:, 'sma20_sma100_ratio'] = df['sma20'] / df['sma100']

    # 使用正确的TA-Lib函数计算RSI
    df.loc[:, 'rsi'] = ta.RSI(close_float, timeperiod=14)
    df.loc[:, 'rsi_overbought'] = (df['rsi'] >= 70).astype(int)
    df.loc[:, 'rsi_oversold'] = (df['rsi'] <= 30).astype(int)
    
    # 使用正确的TA-Lib函数计算CCI，确保输入是double类型
    df.loc[:, 'cci'] = ta.CCI(high_float, low_float, close_float, timeperiod=20)
    
    # 手动计算OBV（On-Balance Volume）
    obv = []
    prev_obv = 0
    for i in range(len(df)):
        if i == 0:
            obv.append(0)
        else:
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                current_obv = prev_obv + df['volume'].iloc[i]
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                current_obv = prev_obv - df['volume'].iloc[i]
            else:
                current_obv = prev_obv
            obv.append(current_obv)
            prev_obv = current_obv
    df.loc[:, 'obv'] = obv
    
    df.loc[:, 'obv_divergence_10_days'] = df['obv'].diff().rolling(10).sum() - df['close'].diff().rolling(10).sum()
    df.loc[:, 'obv_divergence_20_days'] = df['obv'].diff().rolling(20).sum() - df['close'].diff().rolling(20).sum()

    # 日度收益率
    df.loc[:, 'returns_in_%'] = np.round((df['close'].pct_change()) * 100, 2)

    # 目标变量，检验训练结果
    df.loc[:, 'target'] = df['returns_in_%'].shift(-1)

    # 移除空值
    df.dropna(inplace=True)
    return df