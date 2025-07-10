"""
策略基类
定义量化策略的基本接口和通用功能
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str, params: Dict[str, Any] = None):
        """
        初始化策略
        
        Args:
            name: 策略名称
            params: 策略参数
        """
        self.name = name
        self.params = params or {}
        self.positions = {}  # 当前持仓
        self.trades = []     # 交易记录
        self.signals = []    # 信号记录
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        
        Args:
            data: 市场数据
            
        Returns:
            包含信号的DataFrame
        """
        pass
    
    @abstractmethod
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
        pass
    
    def update_positions(self, symbol: str, quantity: float, price: float, timestamp: datetime):
        """
        更新持仓
        
        Args:
            symbol: 交易标的
            quantity: 交易数量
            price: 交易价格
            timestamp: 交易时间
        """
        if symbol not in self.positions:
            self.positions[symbol] = {
                'quantity': 0,
                'avg_price': 0,
                'last_update': timestamp
            }
        
        pos = self.positions[symbol]
        old_quantity = pos['quantity']
        old_avg_price = pos['avg_price']
        
        # 更新持仓
        new_quantity = old_quantity + quantity
        if new_quantity != 0:
            new_avg_price = (old_quantity * old_avg_price + quantity * price) / new_quantity
        else:
            new_avg_price = 0
        
        pos['quantity'] = new_quantity
        pos['avg_price'] = new_avg_price
        pos['last_update'] = timestamp
        
        # 记录交易
        self.trades.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'value': quantity * price
        })
        
        logger.info(f"持仓更新: {symbol}, 数量: {quantity}, 价格: {price}, 总持仓: {new_quantity}")
    
    def get_position_value(self, symbol: str, current_price: float) -> float:
        """
        获取持仓市值
        
        Args:
            symbol: 交易标的
            current_price: 当前价格
            
        Returns:
            持仓市值
        """
        if symbol in self.positions:
            return self.positions[symbol]['quantity'] * current_price
        return 0.0
    
    def get_total_position_value(self, prices: Dict[str, float]) -> float:
        """
        获取总持仓市值
        
        Args:
            prices: 各标的当前价格
            
        Returns:
            总持仓市值
        """
        total_value = 0.0
        for symbol, price in prices.items():
            total_value += self.get_position_value(symbol, price)
        return total_value
    
    def get_strategy_summary(self) -> Dict[str, Any]:
        """
        获取策略摘要
        
        Returns:
            策略摘要信息
        """
        return {
            'name': self.name,
            'params': self.params,
            'positions': self.positions,
            'total_trades': len(self.trades),
            'total_signals': len(self.signals)
        }
    
    def reset(self):
        """重置策略状态"""
        self.positions = {}
        self.trades = []
        self.signals = []
        logger.info(f"策略 {self.name} 已重置")


class SignalStrategy(BaseStrategy):
    """基于信号的策略基类"""
    
    def __init__(self, name: str, params: Dict[str, Any] = None):
        super().__init__(name, params)
        self.signal_threshold = params.get('signal_threshold', 0.5)
        self.position_size = params.get('position_size', 0.1)
    
    def calculate_position_size(self, signal: float, price: float, capital: float) -> float:
        """
        基于信号强度计算仓位大小
        
        Args:
            signal: 信号强度 (-1 到 1)
            price: 当前价格
            capital: 可用资金
            
        Returns:
            仓位大小
        """
        if abs(signal) < self.signal_threshold:
            return 0
        
        # 根据信号强度计算仓位比例
        position_ratio = abs(signal) * self.position_size
        
        # 计算可买入的股数
        max_shares = int(capital * position_ratio / price)
        
        return max_shares if signal > 0 else -max_shares
    
    def record_signal(self, timestamp: datetime, symbol: str, signal: float, price: float):
        """
        记录信号
        
        Args:
            timestamp: 时间戳
            symbol: 交易标的
            signal: 信号强度
            price: 当前价格
        """
        self.signals.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'signal': signal,
            'price': price
        }) 