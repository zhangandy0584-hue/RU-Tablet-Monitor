import requests
import json
import time
import random
import re
from datetime import datetime

# 监控目标：品牌和价格区间（过滤配件）
BRANDS = ["TECNO", "Infinix", "Xiaomi", "Huawei", "Samsung", "Apple"]
MIN_PRICE = 8000   # 低于8000卢布通常是配件
MAX_PRICE = 180000 # 高于18w通常是异常数据

class RUMarketIntelligence:
    def __init__(self):
        self.results = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9'
        }

    def fetch_dns(self, brand):
        """抓取 DNS 渠道数据"""
        search_url = f"https://www.dns-shop.ru/search/?q=planshet+{brand.lower()}"
        try:
            # 随机延迟 5-10 秒，模拟真人操作
            time.sleep(random.uniform(5, 10))
            resp = requests.get(search_url, headers=self.headers, timeout=30)
            if resp.status_code != 200: return
            
            # 使用正则表达式精准定位型号和价格
            raw_items = re.findall(r'data-product-title="(.*?)".*?data-product-price="(\d+)"', resp.text)
            for name, price in raw_items:
                p_val = int(price)
                if MIN_PRICE < p_val < MAX_PRICE:
                    self.results.append({
                        "brand": brand,
                        "model": name.replace("Планшет ", "").strip()[:30],
                        "dns": p_val,
                        "source": "DNS"
                    })
        except Exception as e:
            print(f"DNS {brand} 抓取跳过: {e}")

    def run(self):
        for brand in BRANDS:
            print(f"正在扫描: {brand}...")
            self.fetch_dns(brand)
        
        # 保存为 data.json
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({"items": self.results, "last_update": self.timestamp}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    bot = RUMarketIntelligence()
    bot.run()
