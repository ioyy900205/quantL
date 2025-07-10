# -*- coding: utf-8 -*-
"""
量化分析项目主程序
提供完整的量化分析流程
"""

import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.downloader import downloader
from src.analysis.technical_indicators import technical_indicators
from src.strategy.dual_ma_strategy import DualMAStrategy
from src.backtest.backtest_engine import backtest_engine
from src.visualization.charts import chart_maker
from src.utils.config import config
from src.utils.logger import logger


def download_data():
    """下载数据"""
    logger.info("开始下载数据...")
    
    # 获取股票池
    stock_pool = config.get_stock_pool("default")
    
    # 下载股票数据
    stock_data = downloader.download_stock_batch(
        stock_codes=stock_pool,
        start_date="2020-01-01",
        end_date="2023-12-31"
    )
    
    # 下载指数数据作为基准
    benchmark_data = downloader.download_index_data("000300")  # 沪深300
    
    logger.info(f"数据下载完成: {len(stock_data)} 只股票")
    
    return stock_data, benchmark_data


def analyze_data(stock_data):
    """分析数据"""
    logger.info("开始技术分析...")
    
    analyzed_data = {}
    
    for symbol, df in stock_data.items():
        if df.empty:
            continue
            
        # 计算技术指标
        df_with_indicators = technical_indicators.calculate_all_indicators(df)
        
        # 生成信号
        df_with_signals = technical_indicators.generate_signals(df_with_indicators)
        
        analyzed_data[symbol] = df_with_signals
        
        logger.info(f"技术分析完成: {symbol}")
    
    return analyzed_data


def run_strategy(analyzed_data):
    """运行策略"""
    logger.info("开始运行策略...")
    
    # 创建策略
    strategy_params = config.get_strategy_params("dual_ma")
    strategy = DualMAStrategy(strategy_params)
    
    # 生成策略信号
    strategy_data = {}
    
    for symbol, df in analyzed_data.items():
        if df.empty:
            continue
            
        # 使用策略生成信号
        df_with_strategy = strategy.generate_signals(df)
        strategy_data[symbol] = df_with_strategy
        
        logger.info(f"策略信号生成完成: {symbol}")
    
    return strategy, strategy_data


def run_backtest(strategy, strategy_data, benchmark_data):
    """运行回测"""
    logger.info("开始回测...")
    
    # 运行回测
    results = backtest_engine.run_backtest(
        strategy=strategy,
        data=strategy_data,
        start_date="2020-01-01",
        end_date="2023-12-31"
    )
    
    # 打印回测结果
    print("\n" + "="*50)
    print("回测结果")
    print("="*50)
    print(f"策略名称: {results.get('strategy_name', 'N/A')}")
    print(f"初始资金: {results.get('initial_capital', 0):,.2f}")
    print(f"最终资金: {results.get('final_capital', 0):,.2f}")
    print(f"总收益率: {results.get('total_return', 0)*100:.2f}%")
    print(f"年化收益率: {results.get('annual_return', 0)*100:.2f}%")
    print(f"夏普比率: {results.get('sharpe_ratio', 0):.2f}")
    print(f"最大回撤: {results.get('max_drawdown', 0)*100:.2f}%")
    print(f"总交易次数: {results.get('total_trades', 0)}")
    print(f"胜率: {results.get('win_rate', 0)*100:.2f}%")
    print("="*50)
    
    return results


def visualize_results(results, strategy_data, benchmark_data):
    """可视化结果"""
    logger.info("开始生成图表...")
    
    # 创建输出目录
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # 绘制回测结果
    if results and 'portfolio_history' in results:
        backtest_engine.plot_results(
            results,
            save_path=f"{output_dir}/backtest_results.png"
        )
    
    # 绘制技术指标图（以第一只股票为例）
    if strategy_data:
        first_symbol = list(strategy_data.keys())[0]
        first_data = strategy_data[first_symbol]
        
        chart_maker.plot_technical_indicators(
            first_data,
            save_path=f"{output_dir}/technical_indicators.png"
        )
        
        chart_maker.plot_candlestick(
            first_data,
            title=f"{first_symbol} K线图",
            save_path=f"{output_dir}/candlestick.png"
        )
    
    # 绘制交易分析
    if results and 'trades' in results:
        chart_maker.plot_trade_analysis(
            results['trades'],
            save_path=f"{output_dir}/trade_analysis.png"
        )
    
    logger.info(f"图表已保存到 {output_dir} 目录")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="量化分析项目")
    parser.add_argument("--download", action="store_true", help="下载数据")
    parser.add_argument("--analyze", action="store_true", help="技术分析")
    parser.add_argument("--strategy", action="store_true", help="运行策略")
    parser.add_argument("--backtest", action="store_true", help="运行回测")
    parser.add_argument("--visualize", action="store_true", help="生成图表")
    parser.add_argument("--all", action="store_true", help="运行完整流程")
    
    args = parser.parse_args()
    
    try:
        if args.all or args.download:
            # 下载数据
            stock_data, benchmark_data = download_data()
        else:
            stock_data, benchmark_data = {}, {}
        
        if args.all or args.analyze:
            # 分析数据
            analyzed_data = analyze_data(stock_data)
        else:
            analyzed_data = {}
        
        if args.all or args.strategy:
            # 运行策略
            strategy, strategy_data = run_strategy(analyzed_data)
        else:
            strategy, strategy_data = None, {}
        
        if args.all or args.backtest:
            # 运行回测
            if strategy and strategy_data:
                results = run_backtest(strategy, strategy_data, benchmark_data)
            else:
                logger.warning("没有策略数据，跳过回测")
                results = {}
        else:
            results = {}
        
        if args.all or args.visualize:
            # 可视化结果
            visualize_results(results, strategy_data, benchmark_data)
        
        if not any([args.download, args.analyze, args.strategy, args.backtest, args.visualize, args.all]):
            # 默认运行完整流程
            logger.info("运行完整量化分析流程...")
            
            # 下载数据
            stock_data, benchmark_data = download_data()
            
            # 分析数据
            analyzed_data = analyze_data(stock_data)
            
            # 运行策略
            strategy, strategy_data = run_strategy(analyzed_data)
            
            # 运行回测
            results = run_backtest(strategy, strategy_data, benchmark_data)
            
            # 可视化结果
            visualize_results(results, strategy_data, benchmark_data)
        
        logger.info("量化分析完成！")
        
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        raise


if __name__ == "__main__":
    main() 