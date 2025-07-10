"""
基于akshare的数据下载器
提供股票、指数、基金等金融数据的下载功能
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import time
import os
from pathlib import Path

from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataDownloader:
    """数据下载器"""
    
    def __init__(self):
        """初始化数据下载器"""
        self.timeout = config.get("data_source.akshare.timeout", 30)
        self.retry_times = config.get("data_source.akshare.retry_times", 3)
        self.raw_data_path = config.get_data_path("raw_data")
        self.cache_data_path = config.get_data_path("cache_data")
        
    def download_stock_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "daily",
        adjust: str = "qfq"
    ) -> pd.DataFrame:
        """
        下载股票数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            period: 周期 (daily, weekly, monthly)
            adjust: 复权类型 (qfq: 前复权, hfq: 后复权, "")
            
        Returns:
            股票数据DataFrame
        """
        try:
            logger.info(f"开始下载股票数据: {stock_code}")
            
            # 设置默认日期范围
            if not start_date:
                start_date = "2020-01-01"
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            # 转换日期格式为YYYYMMDD
            start_date_formatted = start_date.replace("-", "")
            end_date_formatted = end_date.replace("-", "")
            
            # 下载数据
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period=period,
                start_date=start_date_formatted,
                end_date=end_date_formatted,
                adjust=adjust
            )
            
            # 检查数据是否为空
            if df.empty:
                logger.warning(f"股票 {stock_code} 在指定时间范围内没有数据")
                return pd.DataFrame()
            
            # 检查列名并重命名
            expected_columns = ['日期', '股票代码', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
            if len(df.columns) != len(expected_columns):
                logger.warning(f"股票 {stock_code} 数据列数不匹配: 期望 {len(expected_columns)}, 实际 {len(df.columns)}")
                # 如果列数不匹配，尝试使用前11列
                if len(df.columns) >= 11:
                    df = df.iloc[:, :11]
                    # 手动设置列名
                    df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'pct_change', 'pct_change_amount', 'turnover']
                else:
                    logger.error(f"股票 {stock_code} 数据列数不足")
                    return pd.DataFrame()
            else:
                # 重命名列
                column_mapping = {
                    '日期': 'date',
                    '开盘': 'open', 
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '涨跌幅': 'pct_change',
                    '涨跌额': 'pct_change_amount',
                    '换手率': 'turnover'
                }
                df = df.rename(columns=column_mapping)
            
            # 设置日期索引
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 确保数值列的数据类型
            numeric_columns = ['open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'pct_change', 'pct_change_amount', 'turnover']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 保存数据
            self._save_data(df, f"{stock_code}_{period}_{adjust}.csv", "raw")
            
            logger.info(f"股票数据下载完成: {stock_code}, 数据量: {len(df)}")
            return df
            
        except Exception as e:
            logger.error(f"下载股票数据失败: {stock_code}, 错误: {e}")
            return pd.DataFrame()
    
    def download_stock_batch(
        self,
        stock_codes: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "daily",
        adjust: str = "qfq"
    ) -> Dict[str, pd.DataFrame]:
        """
        批量下载股票数据
        
        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            period: 周期
            adjust: 复权类型
            
        Returns:
            股票数据字典
        """
        results = {}
        
        for i, stock_code in enumerate(stock_codes):
            logger.info(f"\n下载进度: {i+1}/{len(stock_codes)} - {stock_code}")
            
            df = self.download_stock_data(
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                period=period,
                adjust=adjust
            )
            
            if not df.empty:
                results[stock_code] = df
            
            # 避免请求过于频繁
            time.sleep(0.5)
        
        return results
    
    def download_index_data(
        self,
        index_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        下载指数数据
        
        Args:
            index_code: 指数代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            指数数据DataFrame
        """
        try:
            logger.info(f"开始下载指数数据: {index_code}")
            
            if not start_date:
                start_date = "2020-01-01"
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            # 转换日期格式为YYYYMMDD
            start_date_formatted = start_date.replace("-", "")
            end_date_formatted = end_date.replace("-", "")
            
            # 下载指数数据
            df = ak.stock_zh_index_hist_csindex(
                symbol=index_code,
                start_date=start_date_formatted,
                end_date=end_date_formatted
            )
            
            # 检查数据是否为空
            if df.empty:
                logger.warning(f"指数 {index_code} 在指定时间范围内没有数据")
                return pd.DataFrame()
            
            # 重命名列
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '涨跌': 'change',
                '涨跌幅': 'pct_change',
                '成交量': 'volume',
                '成交金额': 'amount'
            }
            df = df.rename(columns=column_mapping)
            
            # 过滤需要的列
            needed_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_change']
            available_columns = [col for col in needed_columns if col in df.columns]
            df = df[available_columns]
            
            # 设置日期索引
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 确保数值列的数据类型
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount', 'pct_change']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 保存数据
            self._save_data(df, f"{index_code}_index.csv", "raw")
            
            logger.info(f"指数数据下载完成: {index_code}, 数据量: {len(df)}")
            return df
            
        except Exception as e:
            logger.error(f"下载指数数据失败: {index_code}, 错误: {e}")
            return pd.DataFrame()
    
    def download_fund_data(
        self,
        fund_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        下载基金数据
        
        Args:
            fund_code: 基金代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            基金数据DataFrame
        """
        try:
            logger.info(f"开始下载基金数据: {fund_code}")
            
            if not start_date:
                start_date = "2020-01-01"
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            # 下载基金数据
            df = ak.fund_open_fund_info_em(fund=fund_code, indicator="净值")
            
            # 过滤日期范围
            df['净值日期'] = pd.to_datetime(df['净值日期'])
            df = df[(df['净值日期'] >= start_date) & (df['净值日期'] <= end_date)]
            
            # 重命名列
            df.columns = ['date', 'nav', 'accumulated_nav', 'daily_return', 'subscription_status', 'redemption_status', 'dividend']
            
            # 设置日期索引
            df.set_index('date', inplace=True)
            
            # 保存数据
            self._save_data(df, f"{fund_code}_fund.csv", "raw")
            
            logger.info(f"基金数据下载完成: {fund_code}, 数据量: {len(df)}")
            return df
            
        except Exception as e:
            logger.error(f"下载基金数据失败: {fund_code}, 错误: {e}")
            return pd.DataFrame()
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取股票列表
        
        Returns:
            股票列表DataFrame
        """
        try:
            logger.info("开始获取股票列表")
            
            # 获取A股股票列表
            df = ak.stock_zh_a_spot_em()
            
            # 保存数据
            self._save_data(df, "stock_list.csv", "cache")
            
            logger.info(f"股票列表获取完成, 数量: {len(df)}")
            return df
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def _save_data(self, df: pd.DataFrame, filename: str, data_type: str = "raw"):
        """
        保存数据到文件
        
        Args:
            df: 数据DataFrame
            filename: 文件名
            data_type: 数据类型 (raw, cache)
        """
        if data_type == "raw":
            save_path = os.path.join(self.raw_data_path, filename)
        else:
            save_path = os.path.join(self.cache_data_path, filename)
        
        try:
            df.to_csv(save_path, encoding='utf-8')
            logger.debug(f"数据已保存: {save_path}")
        except Exception as e:
            logger.error(f"保存数据失败: {save_path}, 错误: {e}")


# 全局数据下载器实例
downloader = DataDownloader() 