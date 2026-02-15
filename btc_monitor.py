import requests
import statistics

# 填入你的 Server酱 SendKey
SERVER_CHAN_KEY = "SCT314813TceWtnRBKA30YQs6XaQi9PAwh"

# 获取比特币历史价格，返回每天收盘价列表
def get_price_history(days):
    if days > 365:
        days = 365  # 最大365天
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
    except Exception as e:
        raise ValueError(f"请求CoinGecko失败: {e}")

    if "prices" not in data:
        raise ValueError(f"API没有返回价格数据，返回内容：{data}")

    prices_hourly = [p[1] for p in data["prices"]]

    # 取每天收盘价（每24小时取最后一个）
    prices_daily = [prices_hourly[i] for i in range(23, len(prices_hourly), 24)]
    return prices_daily

# 评分函数
def score(ahr, long_ratio):
    s = 0
    # AHR评分
    if ahr < 0.5:
        s += 3
    elif ahr < 1.0:
        s += 2
    elif ahr < 1.3:
        s += 1
    else:
        s -= 2

    # 长期估值评分
    if long_ratio < 0.6:
        s += 3
    elif long_ratio < 1.0:
        s += 2
    elif long_ratio < 1.5:
        s += 1
    else:
        s -= 2

    return s

# 星级评价
def stars(s):
    if s >= 5:
        return "⭐⭐⭐⭐⭐ 强烈低估"
    elif s >= 3:
        return "⭐⭐⭐⭐ 偏低估"
    elif s >= 1:
        return "⭐⭐⭐ 正常区间"
    elif s == 0:
        return "⭐⭐ 偏高"
    else:
        return "⭐ 高风险区"

# 投资建议
def suggestion(s):
    if s >= 5:
        return "建议：可加大定投比例"
    elif s >= 3:
        return "建议：正常定投"
    elif s >= 1:
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

# 主函数
def main():
    try:
        # 获取200日和365日每日收盘价
        prices_200 = get_price_history(200)
        prices_365 = get_price_history(365)

        current_price = prices_200[-1]
        ma200 = statistics.mean(prices_200)
        ma1y = statistics.mean(prices_365)

        ahr = current_price / ma200
        long_ratio = current_price / ma1y

        total = score(ahr, long_ratio)

        message = f"""
📊 BTC每日估值报告

当前价格：${round(current_price,2)}

AHR趋势值：{round(ahr,3)}
长期估值比：{round(long_ratio,3)}

综合评分：{total}
评级：{stars(total)}

{suggestion(total)}
"""

        send_wechat(message)
        print("推送成功")
    except Exception as e:
        print(f"脚本运行出错: {e}")

if __name__ == "__main__":
    main()
