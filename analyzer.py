#!/usr/bin/env python3
"""
Stock Market Analysis Module
Generates comprehensive market analysis reports
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class StockAnalyzer:
    def __init__(self):
        self.symbols = {
            '^GSPC': 'S&P 500',
            '^IXIC': 'Nasdaq Composite',
            '^DJI': 'Dow Jones Industrial'
        }
        self.analysis_period = os.getenv('ANALYSIS_PERIOD', '1y')
        
    def fetch_stock_data(self, symbol: str, period: str = '1y') -> pd.DataFrame:
        """Fetch stock data from Yahoo Finance"""
        try:
            data = yf.download(symbol, period=period, progress=False)
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        indicators = {}
        
        # Moving Averages
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        
        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        indicators['MA20'] = df['MA20'].iloc[-1]
        indicators['MA50'] = df['MA50'].iloc[-1]
        indicators['MA200'] = df['MA200'].iloc[-1]
        indicators['RSI'] = df['RSI'].iloc[-1]
        indicators['MACD'] = df['MACD'].iloc[-1]
        indicators['Signal_Line'] = df['Signal_Line'].iloc[-1]
        indicators['BB_Upper'] = df['BB_Upper'].iloc[-1]
        indicators['BB_Lower'] = df['BB_Lower'].iloc[-1]
        
        return indicators, df
    
    def analyze_market_momentum(self) -> Dict:
        """Analyze overall market momentum"""
        analysis = {}
        
        for symbol, name in self.symbols.items():
            try:
                data = self.fetch_stock_data(symbol, period='1y')
                if data is None:
                    continue
                
                indicators, _ = self.calculate_technical_indicators(data)
                
                current_price = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2]
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                # 52-week high and low
                week52_high = data['Close'].max()
                week52_low = data['Close'].min()
                
                analysis[name] = {
                    'symbol': symbol,
                    'price': current_price,
                    'change_pct': change_pct,
                    'rsi': indicators['RSI'],
                    'ma20': indicators['MA20'],
                    'ma50': indicators['MA50'],
                    'ma200': indicators['MA200'],
                    '52w_high': week52_high,
                    '52w_low': week52_low,
                    'macd': indicators['MACD'],
                    'signal_line': indicators['Signal_Line']
                }
            except Exception as e:
                logger.error(f"Error analyzing {name}: {str(e)}")
        
        return analysis
    
    def generate_premarket_report(self) -> Dict:
        """Generate pre-market analysis report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'report_type': 'premarket',
            'market_analysis': self.analyze_market_momentum(),
            'recommendations': self.get_premarket_recommendations()
        }
        return report
    
    def generate_postmarket_report(self) -> Dict:
        """Generate post-market analysis report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'report_type': 'postmarket',
            'market_analysis': self.analyze_market_momentum(),
            'recommendations': self.get_postmarket_recommendations()
        }
        return report
    
    def get_premarket_recommendations(self) -> str:
        """Generate pre-market trading recommendations"""
        analysis = self.analyze_market_momentum()
        recommendations = "\n"
        
        for name, data in analysis.items():
            rsi = data['rsi']
            macd = data['macd']
            signal = data['signal_line']
            price = data['price']
            ma50 = data['ma50']
            
            # Generate recommendation logic
            if rsi < 30:
                signal_text = "超卖信号 - 可能反弹"
            elif rsi > 70:
                signal_text = "超买信号 - 可能回调"
            else:
                signal_text = "正常区间"
            
            trend = "上升" if price > ma50 else "下降"
            recommendations += f"\n{name}:\n"
            recommendations += f"  - RSI: {rsi:.2f} ({signal_text})\n"
            recommendations += f"  - 趋势: {trend}\n"
            recommendations += f"  - MACD信号: {'看涨' if macd > signal else '看跌'}\n"
        
        return recommendations
    
    def get_postmarket_recommendations(self) -> str:
        """Generate post-market trading recommendations"""
        analysis = self.analyze_market_momentum()
        recommendations = "\n"
        
        for name, data in analysis.items():
            change = data['change_pct']
            rsi = data['rsi']
            
            if change > 1.5:
                performance = "强势上涨"
            elif change > 0.5:
                performance = "温和上涨"
            elif change > -0.5:
                performance = "基本持平"
            elif change > -1.5:
                performance = "温和下跌"
            else:
                performance = "强势下跌"
            
            recommendations += f"\n{name}:\n"
            recommendations += f"  - 收盘涨跌幅: {change:+.2f}%\n"
            recommendations += f"  - 表现: {performance}\n"
            recommendations += f"  - RSI: {rsi:.2f}\n"
        
        return recommendations
    
    def create_chart(self, symbol: str) -> str:
        """Create and return base64 encoded chart"""
        try:
            data = self.fetch_stock_data(symbol, period='3mo')
            if data is None:
                return None
            
            indicators, df = self.calculate_technical_indicators(data)
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Price chart with moving averages
            ax1.plot(df.index, df['Close'], label='Close Price', linewidth=2)
            ax1.plot(df.index, df['MA20'], label='MA20', alpha=0.7)
            ax1.plot(df.index, df['MA50'], label='MA50', alpha=0.7)
            ax1.plot(df.index, df['MA200'], label='MA200', alpha=0.7)
            ax1.fill_between(df.index, df['BB_Upper'], df['BB_Lower'], alpha=0.1)
            ax1.set_title(f'{symbol} - Price with Moving Averages')
            ax1.set_ylabel('Price (USD)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # RSI chart
            ax2.plot(df.index, df['RSI'], label='RSI', color='orange', linewidth=2)
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought')
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold')
            ax2.set_title('Relative Strength Index (RSI)')
            ax2.set_ylabel('RSI')
            ax2.set_ylim([0, 100])
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Save to bytes
            buffer = BytesIO()
            plt.tight_layout()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return img_str
        except Exception as e:
            logger.error(f"Error creating chart for {symbol}: {str(e)}")
            return None
    
    def format_report_as_html(self, report: Dict, report_type: str = 'postmarket') -> str:
        """Format report as HTML email"""
        analysis = report['market_analysis']
        recommendations = report['recommendations']
        
        report_title = "美股盘前分析" if report_type == 'premarket' else "美股收盘分析"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    padding: 20px;
                }}
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                    border-left: 4px solid #3498db;
                    padding-left: 10px;
                }}
                .market-index {{
                    background-color: #ecf0f1;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                    border-left: 4px solid #3498db;
                }}
                .index-name {{
                    font-weight: bold;
                    font-size: 16px;
                    color: #2c3e50;
                }}
                .positive {{
                    color: #27ae60;
                    font-weight: bold;
                }}
                .negative {{
                    color: #e74c3c;
                    font-weight: bold;
                }}
                .neutral {{
                    color: #7f8c8d;
                    font-weight: bold;
                }}
                .metrics {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 10px;
                    margin-top: 10px;
                    font-size: 14px;
                }}
                .metric {{
                    background-color: white;
                    padding: 8px;
                    border-radius: 3px;
                }}
                .chart-container {{
                    margin: 20px 0;
                    text-align: center;
                }}
                .chart-container img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 5px;
                }}
                .recommendations {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    white-space: pre-wrap;
                    font-family: Courier New, monospace;
                    font-size: 13px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ecf0f1;
                    text-align: center;
                    color: #95a5a6;
                    font-size: 12px;
                }}
                .timestamp {{
                    color: #7f8c8d;
                    font-size: 12px;
                    margin-top: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{report_title}</h1>
                <p class="timestamp">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>📊 市场指数行情</h2>
        """
        
        # Add market analysis
        for index_name, data in analysis.items():
            change_class = 'positive' if data['change_pct'] > 0 else 'negative' if data['change_pct'] < 0 else 'neutral'
            html += f"""
                <div class="market-index">
                    <div class="index-name">{index_name} ({data['symbol']})</div>
                    <div class="metrics">
                        <div class="metric">
                            <strong>当前价格:</strong> ${data['price']:.2f}
                        </div>
                        <div class="metric">
                            <strong>涨跌幅:</strong> <span class="{change_class}">{data['change_pct']:+.2f}%</span>
                        </div>
                        <div class="metric">
                            <strong>52周高:</strong> ${data['52w_high']:.2f}
                        </div>
                        <div class="metric">
                            <strong>52周低:</strong> ${data['52w_low']:.2f}
                        </div>
                        <div class="metric">
                            <strong>RSI:</strong> {data['rsi']:.2f}
                        </div>
                        <div class="metric">
                            <strong>MA20:</strong> ${data['ma20']:.2f}
                        </div>
                        <div class="metric">
                            <strong>MA50:</strong> ${data['ma50']:.2f}
                        </div>
                        <div class="metric">
                            <strong>MA200:</strong> ${data['ma200']:.2f}
                        </div>
                    </div>
                </div>
            """
        
        # Add charts
        html += "<h2>📈 技术面分析</h2>"
        for symbol in self.symbols.keys():
            chart_base64 = self.create_chart(symbol)
            if chart_base64:
                html += f"""
                <div class="chart-container">
                    <img src="data:image/png;base64,{chart_base64}" alt="Chart for {symbol}">
                </div>
                """
        
        # Add recommendations
        html += f"""
                <h2>📋 交易建议</h2>
                <div class="recommendations">{recommendations}</div>
                
                <div class="footer">
                    <p>本分析仅供参考，不构成投资建议。请根据自己的风险承受能力做出投资决策。</p>
                    <p>由美股自动分析工具生成</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
