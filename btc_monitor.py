import requests
import statistics

SERVER_CHAN_KEY = "SCT314813TceWtnRBKA30YQs6XaQi9PAwh"

def get_price_history(days):
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
    r = requests.get(url)
    data = r.json()
    prices = [p[1] for p in data["prices"]]
    return prices

def score(ahr, long_ratio):
    s = 0

    if ahr < 0.5:
        s += 3
    elif ahr < 1.0:
        s += 2
    elif ahr < 1.3:
        s += 1
    else:
        s -= 2

    if long_ratio < 0.6:
        s += 3
    elif long_ratio < 1.0:
        s += 2
    elif long_ratio < 1.5:
        s += 1
    else:
        s -= 2

    return s

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

def suggestion(s):
    if s >= 5:
        return "建议：可加大定投比例"
    elif s >= 3:
        return "建议：正常定投"
    elif s >= 1:
        return "建议：小额定投"
    else:
        return "建议：暂停加仓"

def send_wechat(message):
    url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
    data = {
        "title": "BTC每日估值报告",
        "desp": message
    }
    requests.post(url, data=data)

def main():
    prices_200 = get_price_history(200)
    prices_730 = get_price_history(730)

    current_price = prices_200[-1]
    ma200 = statistics.mean(prices_200)
    ma2y = statistics.mean(prices_730)

    ahr = current_price / ma200
    long_ratio = current_price / ma2y

    total = score(ahr, long_ratio)

    message = f"""
📊 BTC每日估值报告

当前价格：${round(current_price,2)}

AHR趋势值：{round(ahr,2)}
长期估值比：{round(long_ratio,2)}

综合评分：{total}
评级：{stars(total)}

{suggestion(total)}
"""

    send_wechat(message)

if __name__ == "__main__":
    main()
