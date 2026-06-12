# US Stock Market Analyzer

自动化美股市场分析工具，每个交易日北京时间晚上9点提供盘前分析，早上5:30提供收盘分析。

## 功能特性

✅ **自动定时分析** - 每个交易日自动运行分析
- 📅 北京时间 21:00 (9 PM) - 盘前分析
- 📅 北京时间 05:30 (5:30 AM) - 收盘分析

✅ **全面的市场分析**
- 三大指数实时数据（S&P 500、Nasdaq、Dow Jones）
- 技术面分析（RSI、MACD、布林带、移动平均线）
- 价格走势图表
- 交易建议和信号

✅ **美观的邮件报告**
- HTML格式报告
- 实时数据可视化
- 响应式设计

## 环境要求

- Python 3.8+
- Gmail账户（用于发送邮件）
- Internet连接

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone https://github.com/louiseliu0137/us-stock-analyzer.git
cd us-stock-analyzer
```

### 2. 创建Python虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 到 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件并填入你的信息：

```
GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=liuchujun137@icloud.com
STOCK_SYMBOLS=^GSPC,^IXIC,^DJI
ANALYSIS_PERIOD=1y
TIME_ZONE=Asia/Shanghai
```

### 5. Gmail配置

本工具使用Gmail发送邮件，需要进行以下配置：

#### 步骤A：启用两步验证
1. 访问 https://myaccount.google.com/security
2. 找到"两步验证"，点击启用
3. 按照指示完成设置

#### 步骤B：生成应用专用密码
1. 访问 https://myaccount.google.com/apppasswords
2. 选择"邮件"和"Windows电脑"（或你使用的设备）
3. 点击"生成"
4. 复制生成的密码（16位，格式：xxxx xxxx xxxx xxxx）
5. 将密码粘贴到 `.env` 文件的 `GMAIL_PASSWORD` 字段

**⚠️ 注意：不要使用Gmail正式密码，必须使用应用专用密码**

## 使用方法

### 方式1：测试邮件发送

首先测试邮件发送是否正常工作：

```bash
python run_once.py
```

预期输出：
```
2026-06-12 21:30:45 - INFO - Initializing analyzer and email sender...
2026-06-12 21:30:45 - INFO - Testing email connection...
2026-06-12 21:30:48 - INFO - Email connection successful!
2026-06-12 21:30:48 - INFO - Generating post-market analysis report...
2026-06-12 21:31:15 - INFO - Sending email...
2026-06-12 21:31:18 - INFO - ✅ Test email sent successfully!
```

检查 `liuchujun137@icloud.com` 邮箱是否收到测试邮件。

### 方式2：运行定时任务

启动自动化分析器（将在后台持续运行）：

```bash
python main.py
```

程序将在以下时间自动发送分析报告：
- 每个美股交易日（周一至周五）北京时间 21:00
- 每个美股交易日（周一至周五）北京时间 05:30

## 在Google Cloud上部署

### 使用Cloud Functions + Cloud Scheduler

**优点：** 无需保持电脑开机，成本低廉
**成本：** 免费额度内（每月200万次调用）

#### 步骤1：准备Cloud Functions
1. 访问 https://console.cloud.google.com/functions
2. 创建新函数
3. 运行时：Python 3.11
4. 内存：512 MB
5. 超时：300秒

#### 步骤2：上传代码
将项目文件上传到Cloud Functions

#### 步骤3：创建Cloud Scheduler
1. 访问 https://console.cloud.google.com/cloudscheduler
2. 创建两个定时任务：

**任务1 - 盘前分析：**
- 频率：`0 21 * * 1-5` (北京时间每晚9:00，周一-周五)
- HTTP方法：GET
- 目标URL：你的Cloud Functions URL

**任务2 - 收盘分析：**
- 频率：`30 5 * * 1-5` (北京时间每早5:30，周一-周五)
- HTTP方法：GET
- 目标URL：你的Cloud Functions URL

### 在个人电脑上运行

#### Windows

创建批处理文件 `start_analyzer.bat`：

```batch
@echo off
cd /d "%~dp0"
venv\Scripts\activate
python main.py
pause
```

使用Windows Task Scheduler创建定时任务

#### macOS/Linux

创建Shell脚本 `start_analyzer.sh`：

```bash
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
```

使用cron或systemd服务

## 项目结构

```
us-stock-analyzer/
├── main.py              # 主程序，包含定时调度器
├── analyzer.py          # 市场分析模块
├── email_sender.py      # 邮件发送模块
├── run_once.py          # 一次性运行脚本（用于测试）
├── requirements.txt     # Python依赖
├── .env.example         # 环境变量示例
├── .gitignore           # Git忽略文件
└── README.md            # 本文件
```

## 技术指标说明

- **RSI (Relative Strength Index)**: 相对强弱指数
  - 0-30: 超卖区间
  - 70-100: 超买区间
  - 30-70: 正常区间

- **MACD**: 指数平滑移动平均线
  - 用于确认趋势方向
  - MACD > Signal Line: 看涨
  - MACD < Signal Line: 看跌

- **布林带**: 价格波动范围指标
  - 显示价格的波动范围
  - 价格触及上轨可能过热
  - 价格触及下轨可能超卖

- **移动平均线**:
  - MA20: 20天平均价格
  - MA50: 50天平均价格
  - MA200: 200天平均价格
  - 价格在MA上方: 上升趋势
  - 价格在MA下方: 下降趋势

## 常见问题

### Q: 收不到邮件？

**A:** 检查以下几点：
1. 确认 `.env` 文件中的邮箱和密码正确
2. 确保使用的是"应用专用密码"，而不是Gmail正式密码
3. 确认两步验证已启用
4. 检查垃圾邮件文件夹
5. 运行 `python run_once.py` 进行测试

### Q: 图表不显示？

**A:** 
1. 确保已安装 `matplotlib` 和 `seaborn`
2. 检查网络连接
3. 查看日志文件中是否有错误信息

### Q: 如何修改分析时间？

**A:** 编辑 `main.py` 中的 `schedule_tasks()` 方法：

```python
# 修改这两行的时间
schedule.every().monday.at("21:00").do(self.run_premarket_analysis)  # 盘前
schedule.every().monday.at("05:30").do(self.run_postmarket_analysis)  # 收盘
```

### Q: 如何添加更多股票符号？

**A:** 编辑 `analyzer.py` 中的 `symbols` 字典：

```python
self.symbols = {
    '^GSPC': 'S&P 500',
    '^IXIC': 'Nasdaq Composite',
    '^DJI': 'Dow Jones Industrial',
    'AAPL': 'Apple',  # 添加新股票
    'MSFT': 'Microsoft',  # 添加新股票
}
```

## 免责声明

本工具仅提供市场分析信息，不构成投资建议。请根据自己的风险承受能力和投资目标做出投资决策。过去的表现不代表未来的结果。

## 许可证

MIT License

## 支持

如有问题或建议，请提交Issue或Pull Request。
