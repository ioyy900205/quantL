# -*- coding: utf-8 -*-
"""
基本面分析示例
展示如何使用下载的基本面数据进行分析
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.downloader import downloader
from src.utils.config import config
from src.utils.logger import logger


def analyze_financial_statements(fundamental_data):
    """分析财务报表数据"""
    logger.info("开始分析财务报表...")
    
    financial_analysis = {}
    
    for stock_code, stock_data in fundamental_data.items():
        if "financial_income" not in stock_data:
            continue
            
        income_df = stock_data["financial_income"]
        
        # 分析营业收入增长
        if "营业收入" in income_df.columns:
            revenue_growth = analyze_revenue_growth(income_df)
            financial_analysis[stock_code] = {
                "revenue_growth": revenue_growth,
                "latest_revenue": income_df["营业收入"].iloc[-1] if len(income_df) > 0 else None
            }
    
    return financial_analysis


def analyze_valuation_indicators(fundamental_data):
    """分析估值指标"""
    logger.info("开始分析估值指标...")
    
    valuation_analysis = {}
    
    for stock_code, stock_data in fundamental_data.items():
        if "valuation" not in stock_data:
            continue
            
        valuation_df = stock_data["valuation"]
        
        # 分析PE、PB等指标
        if not valuation_df.empty:
            latest_data = valuation_df.iloc[-1]
            valuation_analysis[stock_code] = {
                "pe_ratio": latest_data.get("pe", None),
                "pb_ratio": latest_data.get("pb", None),
                "ps_ratio": latest_data.get("ps", None),
                "market_cap": latest_data.get("market_cap", None)
            }
    
    return valuation_analysis


def analyze_industry_distribution(fundamental_data, industry_data):
    """分析行业分布"""
    logger.info("开始分析行业分布...")
    
    industry_distribution = {}
    
    for stock_code, stock_data in fundamental_data.items():
        if "industry" in stock_data:
            industry_info = stock_data["industry"]
            industry_name = industry_info.get("所属行业", "未知")
            
            if industry_name not in industry_distribution:
                industry_distribution[industry_name] = []
            industry_distribution[industry_name].append(stock_code)
    
    return industry_distribution


def analyze_revenue_growth(income_df):
    """分析营业收入增长"""
    if "营业收入" not in income_df.columns or len(income_df) < 2:
        return None
    
    revenues = income_df["营业收入"].dropna()
    if len(revenues) < 2:
        return None
    
    # 计算同比增长率
    latest_revenue = revenues.iloc[-1]
    previous_revenue = revenues.iloc[-2]
    
    if previous_revenue != 0:
        growth_rate = (latest_revenue - previous_revenue) / previous_revenue
        return growth_rate
    
    return None


def print_analysis_results(financial_analysis, valuation_analysis, industry_distribution):
    """打印分析结果"""
    print("\n" + "="*60)
    print("基本面分析结果")
    print("="*60)
    
    # 打印财务分析结果
    print("\n1. 财务分析 (营业收入增长前10名):")
    if financial_analysis:
        sorted_financial = sorted(
            financial_analysis.items(),
            key=lambda x: x[1]["revenue_growth"] if x[1]["revenue_growth"] else -999,
            reverse=True
        )
        
        for i, (stock_code, data) in enumerate(sorted_financial[:10]):
            growth = data["revenue_growth"]
            if growth is not None:
                print(f"  {i+1:2d}. {stock_code}: {growth*100:.2f}%")
    
    # 打印估值分析结果
    print("\n2. 估值分析 (PE < 20 的股票):")
    if valuation_analysis:
        low_pe_stocks = [
            (code, data) for code, data in valuation_analysis.items()
            if data["pe_ratio"] and data["pe_ratio"] < 20
        ]
        
        for i, (stock_code, data) in enumerate(low_pe_stocks[:10]):
            print(f"  {i+1:2d}. {stock_code}: PE={data['pe_ratio']:.2f}, PB={data['pb_ratio']:.2f}")
    
    # 打印行业分布
    print("\n3. 行业分布:")
    if industry_distribution:
        for industry, stocks in industry_distribution.items():
            print(f"  {industry}: {len(stocks)} 只股票")
    
    print("="*60)


def main():
    """主函数"""
    logger.info("开始基本面分析示例...")
    
    try:
        # 获取股票池（使用较小的样本进行演示）
        stock_pool = config.get_stock_pool("default")[:5]  # 只取前5只股票
        
        # 下载基本面数据
        logger.info("下载基本面数据...")
        fundamental_data = downloader.download_fundamental_batch(
            stock_codes=stock_pool,
            data_types=["financial", "valuation", "industry"]
        )
        
        # 下载行业分类数据
        industry_data = downloader.download_industry_classification()
        
        if not fundamental_data:
            logger.warning("没有下载到基本面数据")
            return
        
        # 进行分析
        financial_analysis = analyze_financial_statements(fundamental_data)
        valuation_analysis = analyze_valuation_indicators(fundamental_data)
        industry_distribution = analyze_industry_distribution(fundamental_data, industry_data)
        
        # 打印结果
        print_analysis_results(financial_analysis, valuation_analysis, industry_distribution)
        
        logger.info("基本面分析完成！")
        
    except Exception as e:
        logger.error(f"基本面分析出错: {e}")
        raise


if __name__ == "__main__":
    main() 