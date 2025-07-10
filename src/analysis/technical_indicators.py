"""
技术指标计算模块
提供常用的技术分析指标计算功能
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
import talib

from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self):
        """初始化技术指标计算器"""
        self.params = config.get("technical_indicators", {})
    
    def calculate_ma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        计算移动平均线
        
        Args:
            df: 价格数据DataFrame
            period: 周期
            
        Returns:
            移动平均线序列
        """
        return df['close'].rolling(window=period).mean()
    
    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        计算指数移动平均线
        
        Args:
            df: 价格数据DataFrame
            period: 周期
            
        Returns:
            指数移动平均线序列
        """
        return df['close'].ewm(span=period).mean()
    
    def calculate_macd(
        self,
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算MACD指标
        
        Args:
            df: 价格数据DataFrame
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            (MACD线, 信号线, 柱状图)
        """
        macd, signal, hist = talib.MACD(
            df['close'],
            fastperiod=fast_period,
            slowperiod=slow_period,
            signalperiod=signal_period
        )
        return macd, signal, hist
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        计算RSI指标
        
        Args:
            df: 价格数据DataFrame
            period: 周期
            
        Returns:
            RSI序列
        """
        return talib.RSI(df['close'], timeperiod=period)
    
    def calculate_bollinger_bands(
        self,
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算布林带
        
        Args:
            df: 价格数据DataFrame
            period: 周期
            std_dev: 标准差倍数
            
        Returns:
            (上轨, 中轨, 下轨)
        """
        upper, middle, lower = talib.BBANDS(
            df['close'],
            timeperiod=period,
            nbdevup=std_dev,
            nbdevdn=std_dev,
            matype=0
        )
        return upper, middle, lower
    
    def calculate_kdj(
        self,
        df: pd.DataFrame,
        fastk_period: int = 9,
        slowk_period: int = 3,
        slowd_period: int = 3
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算KDJ指标
        
        Args:
            df: 价格数据DataFrame
            fastk_period: 快速K周期
            slowk_period: 慢速K周期
            slowd_period: 慢速D周期
            
        Returns:
            (K线, D线, J线)
        """
        k, d = talib.STOCH(
            df['high'],
            df['low'],
            df['close'],
            fastk_period=fastk_period,
            slowk_period=slowk_period,
            slowk_matype=0,
            slowd_period=slowd_period,
            slowd_matype=0
        )
        
        # 计算J线
        j = 3 * k - 2 * d
        
        return k, d, j
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        计算ATR指标
        
        Args:
            df: 价格数据DataFrame
            period: 周期
            
        Returns:
            ATR序列
        """
        return talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
    
    def calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算成交量指标
        
        Args:
            df: 价格数据DataFrame
            
        Returns:
            包含成交量指标的DataFrame
        """
        result = df.copy()
        
        # 成交量移动平均
        result['volume_ma5'] = df['volume'].rolling(window=5).mean()
        result['volume_ma10'] = df['volume'].rolling(window=10).mean()
        
        # 成交量比率
        result['volume_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
        
        # OBV (On Balance Volume)
        result['obv'] = talib.OBV(df['close'], df['volume'])
        
        return result
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有技术指标
        
        Args:
            df: 价格数据DataFrame
            
        Returns:
            包含所有技术指标的DataFrame
        """
        result = df.copy()
        
        # 获取参数
        ma_params = self.params.get('ma', {})
        macd_params = self.params.get('macd', {})
        rsi_params = self.params.get('rsi', {})
        bollinger_params = self.params.get('bollinger', {})
        
        # 移动平均线
        result['ma_short'] = self.calculate_ma(df, ma_params.get('short_period', 5))
        result['ma_long'] = self.calculate_ma(df, ma_params.get('long_period', 20))
        
        # MACD
        macd, signal, hist = self.calculate_macd(
            df,
            fast_period=macd_params.get('fast_period', 12),
            slow_period=macd_params.get('slow_period', 26),
            signal_period=macd_params.get('signal_period', 9)
        )
        result['macd'] = macd
        result['macd_signal'] = signal
        result['macd_hist'] = hist
        
        # RSI
        result['rsi'] = self.calculate_rsi(df, rsi_params.get('period', 14))
        
        # 布林带
        upper, middle, lower = self.calculate_bollinger_bands(
            df,
            period=bollinger_params.get('period', 20),
            std_dev=bollinger_params.get('std_dev', 2.0)
        )
        result['bb_upper'] = upper
        result['bb_middle'] = middle
        result['bb_lower'] = lower
        
        # KDJ
        k, d, j = self.calculate_kdj(df)
        result['kdj_k'] = k
        result['kdj_d'] = d
        result['kdj_j'] = j
        
        # ATR
        result['atr'] = self.calculate_atr(df)
        
        # 成交量指标
        result = self.calculate_volume_indicators(result)
        
        return result
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        
        Args:
            df: 包含技术指标的DataFrame
            
        Returns:
            包含交易信号的DataFrame
        """
        result = df.copy()
        
        # 双均线信号
        result['ma_signal'] = np.where(
            result['ma_short'] > result['ma_long'], 1, -1
        )
        
        # MACD信号
        result['macd_signal'] = np.where(
            result['macd'] > result['macd_signal'], 1, -1
        )
        
        # RSI信号
        rsi_params = self.params.get('rsi', {})
        overbought = rsi_params.get('overbought', 70)
        oversold = rsi_params.get('oversold', 30)
        
        result['rsi_signal'] = 0
        result.loc[result['rsi'] < oversold, 'rsi_signal'] = 1  # 超卖买入
        result.loc[result['rsi'] > overbought, 'rsi_signal'] = -1  # 超买卖出
        
        # 布林带信号
        result['bb_signal'] = 0
        result.loc[result['close'] < result['bb_lower'], 'bb_signal'] = 1  # 下轨买入
        result.loc[result['close'] > result['bb_upper'], 'bb_signal'] = -1  # 上轨卖出
        
        # 综合信号
        result['combined_signal'] = (
            result['ma_signal'] + 
            result['macd_signal'] + 
            result['rsi_signal'] + 
            result['bb_signal']
        )
        
        return result


# 全局技术指标计算器实例
technical_indicators = TechnicalIndicators() 