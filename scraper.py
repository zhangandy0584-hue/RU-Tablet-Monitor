import requests
import json
import time
import re  # 修复：增加了缺失的正则模块

# 待监控的清单
MONITOR_LIST = [
    {
        "brand": "TECNO",
        "model": "Megapad 2",
        "spec": "12/256",
        "urls": {
            "dns": "https://www.dns-shop.ru/product/2aab3723b463d21a/",
            "yandex": "https://market.yandex.ru/" 
        }
    }
]

def get_price_dns(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=15)
        # 修复：更鲁棒的价格提取逻辑
        price_match = re.search(r'"price":(\d+)', resp.text)
        if price_match:
            return int(price_match.group(1))
        return None
    except Exception as e:
        print(f"DNS抓取失败: {e}")
        return None

def calibrate_data(raw_data):
    prices = [v for k, v in raw_data.items() if v]
    if not prices: return {k: {"price": v, "status": "No Data"} for k, v in raw_data.items()}
    
    avg = sum(prices) / len(prices)
    calibrated = {}
    for channel, price in raw_data.items():
        if price and (price < avg * 0.7 or price > avg * 1.3):
            calibrated[channel] = {"price": price, "status": "Suspect"}
        else:
            calibrated[channel] = {"price": price, "status": "Valid"}
    return calibrated

# 运行逻辑
if __name__ == "__main__":
    final_output = []
    for item in MONITOR_LIST:
        raw_prices = {
            "dns": get_price_dns(item["urls"]["dns"]),
            "yandex": None # 占位
        }
        item["calibrated"] = calibrate_data(raw_prices)
        item["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        final_output.append(item)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    print("数据生成成功: data.json")
