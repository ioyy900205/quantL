"""
配置管理工具
用于读取和管理项目配置文件
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的多级键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_data_path(self, path_type: str) -> str:
        """
        获取数据路径
        
        Args:
            path_type: 路径类型 (raw_data, processed_data, cache_data)
            
        Returns:
            数据路径
        """
        base_path = self.get(f"data_source.data_paths.{path_type}")
        if base_path:
            # 确保路径存在
            Path(base_path).mkdir(parents=True, exist_ok=True)
            return base_path
        return ""
    
    def get_stock_pool(self, pool_name: str = "default") -> list:
        """
        获取股票池
        
        Args:
            pool_name: 股票池名称
            
        Returns:
            股票代码列表
        """
        return self.get(f"stock_pool.{pool_name}", [])
    
    def get_technical_params(self, indicator: str) -> Dict[str, Any]:
        """
        获取技术指标参数
        
        Args:
            indicator: 指标名称
            
        Returns:
            指标参数字典
        """
        return self.get(f"technical_indicators.{indicator}", {})
    
    def get_strategy_params(self, strategy: str) -> Dict[str, Any]:
        """
        获取策略参数
        
        Args:
            strategy: 策略名称
            
        Returns:
            策略参数字典
        """
        return self.get(f"strategy.{strategy}", {})
    
    def get_backtest_params(self) -> Dict[str, Any]:
        """获取回测参数"""
        return self.get("backtest", {})
    
    def reload(self):
        """重新加载配置文件"""
        self.config = self._load_config()


# 全局配置实例
config = ConfigManager() 