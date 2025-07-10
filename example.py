#!/usr/bin/env python3
"""
量化分析项目示例脚本
演示如何使用项目的各个模块
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.downloader import downloader
from src.analysis.technical_indicators import technical_indicators
from src.strategy.dual_ma_strategy import DualMAStrategy
from src.backtest.backtest_engine import backtest_engine
from src.visualization.charts import chart_maker
from src.utils.config import config
from src.utils.logger import logger


def main():
    """主函数"""
    logger.info("开始运行量化分析示例...")
    
    try:
        # 1. 下载数据
        logger.info("步骤1: 下载数据")
        stock_code = "000001"  # 平安银行
        
        df = downloader.download_stock_data(
            stock_code=stock_code,
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        
        if df.empty:
            logger.error("数据下载失败")
            return
        
        logger.info(f"成功下载 {stock_code} 的数据，共 {len(df)} 条记录")
        
        # 2. 技术分析
        logger.info("步骤2: 技术分析")
        df_with_indicators = technical_indicators.calculate_all_indicators(df)
        df_with_signals = technical_indicators.generate_signals(df_with_indicators)
        
        logger.info("技术指标计算完成")
        
        # 3. 策略分析
        logger.info("步骤3: 策略分析")
        strategy_params = config.get_strategy_params("dual_ma")
        strategy = DualMAStrategy(strategy_params)
        
        strategy_data = strategy.generate_signals(df_with_signals)
        
        logger.info("策略信号生成完成")
        
        # 4. 回测
        logger.info("步骤4: 回测")
        # 准备回测数据
        backtest_data = {stock_code: strategy_data}
        
        results = backtest_engine.run_backtest(
            strategy=strategy,
            data=backtest_data,
            start_date="2023-01-01",
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
        print("="*50)
        
        # 5. 可视化
        logger.info("步骤5: 生成图表")
        
        # 创建输出目录
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        # 绘制K线图
        chart_maker.plot_candlestick(
            df,
            title=f"{stock_code} K线图",
            save_path=f"{output_dir}/candlestick_example.png"
        )
        
        # 绘制技术指标图
        chart_maker.plot_technical_indicators(
            df_with_indicators,
            save_path=f"{output_dir}/technical_indicators_example.png"
        )
        
        # 绘制回测结果
        if results and 'portfolio_history' in results:
            backtest_engine.plot_results(
                results,
                save_path=f"{output_dir}/backtest_results_example.png"
            )
        
        logger.info(f"图表已保存到 {output_dir} 目录")
        
        # 6. 显示数据摘要
        print("\n" + "="*50)
        print("数据摘要")
        print("="*50)
        print(f"数据时间范围: {df.index.min()} 到 {df.index.max()}")
        print(f"数据条数: {len(df)}")
        print(f"最新收盘价: {df['close'].iloc[-1]:.2f}")
        print(f"最高价: {df['high'].max():.2f}")
        print(f"最低价: {df['low'].min():.2f}")
        print(f"平均成交量: {df['volume'].mean():,.0f}")
        print("="*50)
        
        logger.info("量化分析示例运行完成！")
        
    except Exception as e:
        logger.error(f"示例运行出错: {e}")
        raise


if __name__ == "__main__":
    main() 