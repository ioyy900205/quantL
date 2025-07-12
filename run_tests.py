# -*- coding: utf-8 -*-
"""
测试运行脚本
提供便捷的测试运行方式
"""

import sys
import os
import subprocess
import argparse

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import logger


def run_unit_tests():
    """运行单元测试"""
    logger.info("开始运行单元测试...")
    
    try:
        # 运行数据下载器测试
        result = subprocess.run([
            sys.executable, "tests/test_downloader.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ 单元测试通过")
            print(result.stdout)
        else:
            logger.error("✗ 单元测试失败")
            print(result.stderr)
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"运行单元测试时出错: {e}")
        return False


def run_fundamental_test():
    """运行基本面数据测试"""
    logger.info("开始运行基本面数据测试...")
    
    try:
        # 导入并运行基本面测试
        from tests.test_downloader import TestDataDownloader
        import unittest
        
        # 创建测试套件
        suite = unittest.TestSuite()
        fundamental_tests = [
            'test_download_financial_statement',
            'test_download_valuation_indicators', 
            'test_download_industry_classification',
            'test_download_stock_industry_info',
            'test_download_fundamental_batch'
        ]
        
        for test_name in fundamental_tests:
            suite.addTest(TestDataDownloader(test_name))
        
        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            logger.info("✓ 基本面数据测试通过")
            return True
        else:
            logger.error("✗ 基本面数据测试失败")
            return False
            
    except Exception as e:
        logger.error(f"运行基本面数据测试时出错: {e}")
        return False


def run_example():
    """运行示例程序"""
    logger.info("开始运行基本面分析示例...")
    
    try:
        result = subprocess.run([
            sys.executable, "examples/fundamental_analysis.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ 示例程序运行成功")
            print(result.stdout)
            return True
        else:
            logger.error("✗ 示例程序运行失败")
            print(result.stderr)
            return False
            
    except Exception as e:
        logger.error(f"运行示例程序时出错: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试运行脚本")
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--fundamental", action="store_true", help="运行基本面数据测试")
    parser.add_argument("--example", action="store_true", help="运行示例程序")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    
    args = parser.parse_args()
    
    success = True
    
    try:
        if args.all or args.unit:
            success &= run_unit_tests()
        
        if args.all or args.fundamental:
            success &= run_fundamental_test()
        
        if args.all or args.example:
            success &= run_example()
        
        if not any([args.unit, args.fundamental, args.example, args.all]):
            # 默认运行所有测试
            logger.info("运行所有测试...")
            success &= run_unit_tests()
            success &= run_fundamental_test()
            success &= run_example()
        
        if success:
            logger.info("所有测试完成！")
        else:
            logger.error("部分测试失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 