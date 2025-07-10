"""
双均线策略
基于短期和长期移动平均线的交叉信号进行交易
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

from .base_strategy import SignalStrategy
from ..analysis.technical_indicators import technical_indicators
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DualMAStrategy(SignalStrategy):
    """双均线策略"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化双均线策略
        
        Args:
            params: 策略参数，包含:
                - short_ma: 短期均线周期
                - long_ma: 长期均线周期
                - position_size: 仓位大小
        """
        super().__init__("DualMA", params)
        
        # 获取参数
        self.short_ma = params.get('short_ma', 5)
        self.long_ma = params.get('long_ma', 20)
        self.position_size = params.get('position_size', 0.1)
        
        logger.info(f"双均线策略初始化: 短期均线={self.short_ma}, 长期均线={self.long_ma}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成双均线交易信号
        
        Args:
            data: 包含OHLCV数据的DataFrame
            
        Returns:
            包含信号的DataFrame
        """
        result = data.copy()
        
        # 计算移动平均线
        result['ma_short'] = technical_indicators.calculate_ma(data, self.short_ma)
        result['ma_long'] = technical_indicators.calculate_ma(data, self.long_ma)
        
        # 生成信号
        # 短期均线上穿长期均线，买入信号
        result['signal'] = np.where(
            (result['ma_short'] > result['ma_long']) & 
            (result['ma_short'].shift(1) <= result['ma_long'].shift(1)),
            1,  # 买入信号
            np.where(
                (result['ma_short'] < result['ma_long']) & 
                (result['ma_short'].shift(1) >= result['ma_long'].shift(1)),
                -1,  # 卖出信号
                0   # 无信号
            )
        )
        
        # 计算信号强度（基于均线距离）
        ma_diff = (result['ma_short'] - result['ma_long']) / result['ma_long']
        result['signal_strength'] = np.clip(ma_diff * 10, -1, 1)  # 限制在[-1, 1]范围内
        
        # 添加持仓状态
        result['position'] = result['signal'].cumsum()
        
        logger.info(f"双均线信号生成完成，信号数量: {(result['signal'] != 0).sum()}")
        
        return result
    
    def calculate_position_size(self, signal: float, price: float, capital: float) -> float:
        """
        计算仓位大小
        
        Args:
            signal: 信号强度
            price: 当前价格
            capital: 可用资金
            
        Returns:
            仓位大小
        """
        if signal == 0:
            return 0
        
        # 根据信号强度计算仓位比例
        position_ratio = abs(signal) * self.position_size
        
        # 计算可买入的股数
        max_shares = int(capital * position_ratio / price)
        
        return max_shares if signal > 0 else -max_shares
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        获取策略信息
        
        Returns:
            策略信息字典
        """
        return {
            'name': self.name,
            'short_ma': self.short_ma,
            'long_ma': self.long_ma,
            'position_size': self.position_size,
            'description': '基于短期和长期移动平均线交叉的双均线策略'
        } 