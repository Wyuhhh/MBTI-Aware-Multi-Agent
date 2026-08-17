@echo off
:: ============================================================
:: MBTI Multi-Agent Benchmark 一键复现脚本 (Windows)
:: ============================================================
:: 使用方法: 双击运行或从命令行执行
:: ============================================================

echo ============================================================
echo MBTI Multi-Agent Benchmark 一键复现
echo ============================================================
echo.

:: 设置默认值
set PROVIDER=mock
set MODEL=gpt-4
set API_KEY=
set DEBATE_ROUNDS=2

:: 可以通过环境变量覆盖
:: set PROVIDER=openai
:: set API_KEY=your-api-key

echo 运行配置:
echo   Provider: %PROVIDER%
echo   Model: %MODEL%
echo   Debate Rounds: %DEBATE_ROUNDS%
echo.

:: 创建结果目录
if not exist "benchmark\results" mkdir "benchmark\results"

:: 运行评测
python -m benchmark.evaluator --provider %PROVIDER% --model %MODEL% --rounds %DEBATE_ROUNDS%

echo.
echo ============================================================
echo 评测完成!
echo 结果保存在: benchmark\results\
echo ============================================================
pause