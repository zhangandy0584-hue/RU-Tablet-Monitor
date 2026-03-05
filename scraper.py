import requests
import json
import time
import random
import re
from datetime import datetime

# ================= 核心配置：全品牌、全渠道、备选源 =================
BRANDS = ["TECNO", "Infinix", "Xiaomi", "Huawei", "Samsung", "Apple"]
CHANNELS = ["dns", "mvideo", "citilink", "ozon", "wildberries", "yandex"]
# 备选数据源：当官网 403 封锁时，从比价聚合器提取参考价
FALLBACK_SOURCES = ["https://price.ru/search/?query=", "https://www.aport.ru/search/?q="]

class RU_Intelligence_Pro:
    def __init__(self):
        self.master_data = {}
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    def get_spec(self, name):
        """精准提取配置：如 8/128, 12/256"""
        match = re.search(r'(\d+)[\s/+]?(\d+)\s?(?:GB|ГБ)', name, re.I)
        return f"{match.group(1)}/{match.group(2)}" if match else "STD"

    def fetch_fallback(self, brand, model):
        """备选方案：抓取比价网平均价"""
        search_query = f"{brand} {model}"
        try:
            time.sleep(random.uniform(5, 8))
            resp = requests.get(FALLBACK_SOURCES[0] + search_query, headers={'User-Agent': self.ua}, timeout=15)
            prices = re.findall(r'(\d+[\s\d]*)\s?₽', resp.text)
            if prices:
                vals = sorted([int(p.replace(" ", "")) for p in prices if int(p.replace(" ", "")) > 8000])
                return vals[len(vals)//2] if vals else 0
        except: return 0
        return 0

    def validate_logic(self, prices_dict, brand, model):
        """核心验证：交叉对比 6 渠道 + 剔除离群低价"""
        raw_prices = [p for p in prices_dict.values() if p > 8000]
        
        # 如果主流渠道全军覆没（被封锁），启用备选参考价
        if not raw_prices:
            ref_price = self.fetch_fallback(brand, model)
            if ref_price > 0:
                return "⚠ 官网封锁(采用比价网参考价)", ref_price, ref_price
            return "❌ 暂无有效数据", 0, 0

        # 多方验证：剔除比均价低 30% 以上的虚假低价
        avg = sum(raw_prices) / len(raw_prices)
        valid_prices = [p for p in raw_prices if p > avg * 0.7]
        
        status = "✅ 多方验证通过" if len(valid_prices) >= 2 else "🔍 单源核校"
        best = min(valid_prices) if valid_prices else min(raw_prices)
        return status, best, (0 if not raw_prices else min(raw_prices))

    def run(self):
        # 此处模拟全渠道抓取后的对齐逻辑
        # 实际部署时，脚本会循环请求 6 个渠道的搜索结果
        # 我们以核心 SKU 为 Key 进行对齐
        results = []
        
        # 模拟一条完整的 TECNO 数据作为结构示例
        sample_item = {
            "brand": "TECNO", "model": "Megapad 2", "spec": "12/256",
            "prices": {"dns": 28990, "mvideo": 29990, "citilink": 29490, "ozon": 0, "wildberries": 0, "yandex": 28500, "fallback": 0}
        }
        
        status, best, _ = self.validate_logic(sample_item['prices'], "TECNO", "Megapad 2")
        sample_item['status'] = status
        sample_item['best_price'] = best
        sample_item['update'] = self.timestamp
        results.append(sample_item)

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    RU_Intelligence_Pro().run()
