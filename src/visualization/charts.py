"""
图表绘制模块
提供各种金融数据可视化功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import mplfinance as mpf
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ChartMaker:
    """图表制作器"""
    
    def __init__(self):
        """初始化图表制作器"""
        self.style = config.get("visualization.style", "seaborn-v0_8")
        self.figure_size = config.get("visualization.figure_size", [12, 8])
        self.colors = config.get("visualization.colors", {})
        
        # 设置matplotlib样式
        plt.style.use(self.style)
        
    def plot_candlestick(
        self,
        df: pd.DataFrame,
        title: str = "K线图",
        save_path: Optional[str] = None,
        show_volume: bool = True
    ):
        """
        绘制K线图
        
        Args:
            df: 包含OHLCV数据的DataFrame
            title: 图表标题
            save_path: 保存路径
            show_volume: 是否显示成交量
        """
        try:
            # 准备数据
            df_plot = df.copy()
            df_plot.index.name = 'Date'
            
            # 设置图表样式
            mc = mpf.make_marketcolors(
                up='red',
                down='green',
                edge='inherit',
                wick='inherit',
                volume='inherit'
            )
            s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', y_on_right=False)
            
            # 绘制K线图
            fig, axes = mpf.plot(
                df_plot,
                type='candle',
                title=title,
                volume=show_volume,
                style=s,
                figsize=self.figure_size,
                returnfig=True
            )
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"K线图已保存: {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"绘制K线图失败: {e}")
    
    def plot_technical_indicators(
        self,
        df: pd.DataFrame,
        indicators: List[str] = None,
        title: str = "技术指标图",
        save_path: Optional[str] = None
    ):
        """
        绘制技术指标图
        
        Args:
            df: 包含技术指标的DataFrame
            indicators: 要显示的指标列表
            title: 图表标题
            save_path: 保存路径
        """
        if indicators is None:
            indicators = ['ma_short', 'ma_long', 'rsi', 'macd']
        
        # 计算子图数量
        n_indicators = len(indicators)
        fig, axes = plt.subplots(n_indicators + 1, 1, figsize=(self.figure_size[0], self.figure_size[1] * (n_indicators + 1)))
        
        if n_indicators == 0:
            axes = [axes]
        
        # 绘制价格和移动平均线
        axes[0].plot(df.index, df['close'], label='收盘价', color='black', alpha=0.7)
        
        if 'ma_short' in df.columns and 'ma_long' in df.columns:
            axes[0].plot(df.index, df['ma_short'], label=f'MA{df["ma_short"].iloc[-1]:.0f}', alpha=0.8)
            axes[0].plot(df.index, df['ma_long'], label=f'MA{df["ma_long"].iloc[-1]:.0f}', alpha=0.8)
        
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            axes[0].fill_between(df.index, df['bb_upper'], df['bb_lower'], alpha=0.1, label='布林带')
            axes[0].plot(df.index, df['bb_upper'], '--', alpha=0.5)
            axes[0].plot(df.index, df['bb_lower'], '--', alpha=0.5)
        
        axes[0].set_title(f"{title} - 价格走势")
        axes[0].legend()
        axes[0].grid(True)
        
        # 绘制技术指标
        for i, indicator in enumerate(indicators):
            if indicator not in df.columns:
                continue
                
            ax = axes[i + 1]
            
            if indicator == 'rsi':
                ax.plot(df.index, df['rsi'], label='RSI', color='purple')
                ax.axhline(y=70, color='r', linestyle='--', alpha=0.5)
                ax.axhline(y=30, color='g', linestyle='--', alpha=0.5)
                ax.set_ylim(0, 100)
                ax.set_title('RSI指标')
                
            elif indicator == 'macd':
                ax.plot(df.index, df['macd'], label='MACD', color='blue')
                ax.plot(df.index, df['macd_signal'], label='Signal', color='red')
                ax.bar(df.index, df['macd_hist'], label='Histogram', alpha=0.3)
                ax.set_title('MACD指标')
                
            elif indicator == 'kdj_k':
                ax.plot(df.index, df['kdj_k'], label='K', color='blue')
                ax.plot(df.index, df['kdj_d'], label='D', color='red')
                ax.plot(df.index, df['kdj_j'], label='J', color='green')
                ax.set_title('KDJ指标')
                
            elif indicator == 'volume':
                ax.bar(df.index, df['volume'], alpha=0.7, color='gray')
                ax.set_title('成交量')
                
            else:
                ax.plot(df.index, df[indicator], label=indicator)
                ax.set_title(f'{indicator}指标')
            
            ax.legend()
            ax.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"技术指标图已保存: {save_path}")
        
        plt.show()
    
    def plot_portfolio_performance(
        self,
        portfolio_df: pd.DataFrame,
        benchmark_df: Optional[pd.DataFrame] = None,
        title: str = "组合表现",
        save_path: Optional[str] = None
    ):
        """
        绘制组合表现图
        
        Args:
            portfolio_df: 组合数据DataFrame
            benchmark_df: 基准数据DataFrame
            title: 图表标题
            save_path: 保存路径
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. 组合价值对比
        axes[0, 0].plot(portfolio_df.index, portfolio_df['total_value'], label='组合价值', linewidth=2)
        if benchmark_df is not None:
            axes[0, 0].plot(benchmark_df.index, benchmark_df['close'], label='基准', alpha=0.7)
        axes[0, 0].set_title('组合价值 vs 基准')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # 2. 收益率对比
        portfolio_returns = portfolio_df['total_value'].pct_change()
        cumulative_returns = (1 + portfolio_returns).cumprod()
        axes[0, 1].plot(portfolio_df.index, cumulative_returns, label='组合收益率', linewidth=2)
        
        if benchmark_df is not None:
            benchmark_returns = benchmark_df['close'].pct_change()
            benchmark_cumulative = (1 + benchmark_returns).cumprod()
            axes[0, 1].plot(benchmark_df.index, benchmark_cumulative, label='基准收益率', alpha=0.7)
        
        axes[0, 1].set_title('累计收益率对比')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # 3. 现金和持仓比例
        axes[1, 0].plot(portfolio_df.index, portfolio_df['cash'], label='现金', alpha=0.7)
        axes[1, 0].plot(portfolio_df.index, portfolio_df['position_value'], label='持仓市值', alpha=0.7)
        axes[1, 0].set_title('现金 vs 持仓')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # 4. 回撤
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        axes[1, 1].fill_between(portfolio_df.index, drawdown, 0, alpha=0.3, color='red')
        axes[1, 1].plot(portfolio_df.index, drawdown, color='red')
        axes[1, 1].set_title('回撤')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"组合表现图已保存: {save_path}")
        
        plt.show()
    
    def plot_trade_analysis(
        self,
        trades: List[Dict],
        title: str = "交易分析",
        save_path: Optional[str] = None
    ):
        """
        绘制交易分析图
        
        Args:
            trades: 交易记录列表
            title: 图表标题
            save_path: 保存路径
        """
        if not trades:
            logger.warning("没有交易记录可分析")
            return
        
        trades_df = pd.DataFrame(trades)
        trades_df['date'] = pd.to_datetime(trades_df['date'])
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. 交易金额分布
        axes[0, 0].hist(trades_df['value'], bins=20, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('交易金额分布')
        axes[0, 0].set_xlabel('交易金额')
        axes[0, 0].set_ylabel('频次')
        axes[0, 0].grid(True)
        
        # 2. 买卖交易数量
        action_counts = trades_df['action'].value_counts()
        axes[0, 1].pie(action_counts.values, labels=action_counts.index, autopct='%1.1f%%')
        axes[0, 1].set_title('买卖交易比例')
        
        # 3. 交易时间分布
        trades_df['month'] = trades_df['date'].dt.month
        monthly_trades = trades_df['month'].value_counts().sort_index()
        axes[1, 0].bar(monthly_trades.index, monthly_trades.values)
        axes[1, 0].set_title('月度交易分布')
        axes[1, 0].set_xlabel('月份')
        axes[1, 0].set_ylabel('交易次数')
        axes[1, 0].grid(True)
        
        # 4. 交易成本分析
        if 'cost' in trades_df.columns:
            axes[1, 1].plot(trades_df['date'], trades_df['cost'].cumsum(), label='累计交易成本')
            axes[1, 1].set_title('累计交易成本')
            axes[1, 1].set_xlabel('日期')
            axes[1, 1].set_ylabel('成本')
            axes[1, 1].legend()
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"交易分析图已保存: {save_path}")
        
        plt.show()
    
    def create_interactive_chart(
        self,
        df: pd.DataFrame,
        title: str = "交互式图表"
    ):
        """
        创建交互式图表
        
        Args:
            df: 数据DataFrame
            title: 图表标题
        """
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('价格', '成交量', '技术指标'),
            row_width=[0.5, 0.25, 0.25]
        )
        
        # 添加K线图
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name="K线"
            ),
            row=1, col=1
        )
        
        # 添加移动平均线
        if 'ma_short' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['ma_short'],
                    name="短期均线",
                    line=dict(color='orange')
                ),
                row=1, col=1
            )
        
        if 'ma_long' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['ma_long'],
                    name="长期均线",
                    line=dict(color='blue')
                ),
                row=1, col=1
            )
        
        # 添加成交量
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name="成交量",
                marker_color='gray'
            ),
            row=2, col=1
        )
        
        # 添加RSI
        if 'rsi' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['rsi'],
                    name="RSI",
                    line=dict(color='purple')
                ),
                row=3, col=1
            )
            
            # 添加RSI超买超卖线
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        fig.update_layout(
            title=title,
            xaxis_rangeslider_visible=False,
            height=800
        )
        
        fig.show()


# 全局图表制作器实例
chart_maker = ChartMaker() 