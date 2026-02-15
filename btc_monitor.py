import requests
import statistics
import math
from datetime import datetime
import os

# -------------------------------
# 从环境变量读取 Server酱 Key
SERVER_CHAN_KEY = os.environ.get("SERVER_CHAN_KEY")
if not SERVER_CHAN_KEY:
    raise ValueError("SERVER_CHAN_KEY 未设置，请在 GitHub Secret 中添加")

# -------------------------------
# 获取比特币历史价格，返回每天收盘价列表
def get_price_history(days):
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}&interval=daily"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
    except Exception as e:
        raise ValueError(f"请求CoinGecko失败: {e}")

    if "prices" not in data:
        raise ValueError(f"API没有返回价格数据，返回内容：{data}")

    prices_daily = [p[1] for p in data["prices"]]
    return prices_daily

# -------------------------------
# 计算币龄（天）
def get_coin_age_days():
    btc_birth = datetime(2009, 1, 3)
    today = datetime.now()
    return (today - btc_birth).days

# 指数增长估值
def get_exponential_value(coin_age_days):
    return 10 ** (5.84 * math.log10(coin_age_days) - 17.01)

# AHR999评分函数
def score(ahr):
    if ahr < 0.45:
        return 5
    elif ahr < 0.7:
        return 4
    elif ahr < 1.0:
        return 3
    elif ahr < 1.3:
        return 2
    else:
        return 1

def stars(s):
    if s == 5:
        return "⭐⭐⭐⭐⭐"
    elif s == 4:
        return "⭐⭐⭐⭐"
    elif s == 3:
        return "⭐⭐⭐"
    elif s == 2:
        return "⭐⭐"
    else:
        return "⭐"

def suggestion(s):
    if s == 5:
        return "建议：无脑抄底"
    elif s == 4:
        return "建议：可加大定投比例"
    elif s == 3:
        return "建议：正常定投"
    elif s == 2:
        return "建议：小额定投"
    else:
        return "建议：暂停加仓"

# 微信推送
def send_wechat(message):
    url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
    data = {"title": "BTC每日估值报告", "desp": message}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"发送微信失败: {e}")

# -------------------------------
# 主函数
def main():
    try:
        prices_200 = get_price_history(200)
        current_price = prices_200[-1]
        ma200 = statistics.mean(prices_200)

        coin_age_days = get_coin_age_days()
        exp_value = get_exponential_value(coin_age_days)

        ahr999 = (current_price / ma200) * (current_price / exp_value)
        total_score = score(ahr999)

        # 微信推送内容，每行换行显示
        message = (
            f"📊 BTC每日估值报告（21:00推送）\n\n"
            f"当前价格：${round(current_price,2)}\n"
            f"200日均值：${round(ma200,2)}\n"
            f"AHR999：{round(ahr999,3)}\n"
            f"评级：{stars(total_score)}\n"
            f"{suggestion(total_score)}"
        )

        send_wechat(message)
        print("推送成功")
    except Exception as e:
        print(f"脚本运行出错: {e}")

if __name__ == "__main__":
    main()
