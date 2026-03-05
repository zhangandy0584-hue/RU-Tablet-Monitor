import requests
from bs4 import BeautifulSoup
import json
import time

# 待监控的清单（你可以根据格式自行增加链接）
MONITOR_LIST = [
    {
        "brand": "TECNO",
        "model": "Megapad 2",
        "spec": "12/256",
        "urls": {
            "dns": "https://www.dns-shop.ru/product/2aab3723b463d21a/",
            "mvideo": "https://www.mvideo.ru/products/40030000", # 示例ID
            "yandex": "https://market.yandex.ru/product--planshet-tecno-megapad-2/123" # 示例ID
        }
    }
]

def get_price_dns(url):
    try:
        # DNS 反爬很严，这里模拟浏览器头
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        # 简单逻辑：在网页源码中寻找价格数字（实际生产中需配合正则或Json解析）
        price = re.search(r'"price":(\d+)', resp.text).group(1)
        return int(price)
    except:
        return None

def calibrate_data(raw_data):
    """
    多方校准逻辑：
    1. 计算所有渠道的平均值
    2. 如果某个渠道价格偏离均值 30% 以上，标记为 'Suspect' (疑似虚假)
    """
    prices = [v for k, v in raw_data.items() if v]
    if not prices: return raw_data
    
    avg = sum(prices) / len(prices)
    calibrated = {}
    for channel, price in raw_data.items():
        if price and (price < avg * 0.7 or price > avg * 1.3):
            calibrated[channel] = {"price": price, "status": "Suspect"}
        else:
            calibrated[channel] = {"price": price, "status": "Valid"}
    return calibrated

# 运行并生成数据
final_output = []
for item in MONITOR_LIST:
    results = {
        "dns": get_price_dns(item["urls"]["dns"]),
        # 这里后续可以扩展 mvideo, citylink 等抓取函数
    }
    item["calibrated"] = calibrate_data(results)
    item["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
    final_output.append(item)

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)
