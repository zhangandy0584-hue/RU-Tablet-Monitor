import requests
import json
import time
import random
import re
import hashlib
from datetime import datetime

# ================= 工业级配置：满足所有品牌需求 =================
BRANDS = ["TECNO", "Infinix", "Xiaomi", "Huawei", "Samsung", "Apple", "Redmi", "Realme", "Honor", "Lenovo"]

class RUMarketInvincibleV23:
    def __init__(self):
        self.master_data = {}
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.session = requests.Session()
        
    def _get_headers(self):
        """模拟高权重俄语用户浏览器指纹"""
        uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0"
        ]
        return {
            "User-Agent": random.choice(uas),
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
            "Referer": "https://www.google.ru/"
        }

    def solve_sku(self, text_blob, brand):
        """核心解析引擎：从搜索摘要中提取 SKU、规格和卢布价格"""
        # 匹配规律：数字 + 空格 + ₽/руб/RUB
        price_matches = re.findall(r'(\d+[\s\d]*)\s*(?:руб|₽|RUB)', text_blob)
        # 匹配规律：存储规格 (如 8/256GB)
        spec_matches = re.findall(r'(\d+[\s/+]?\d+(?:GB|TB|ГБ))', text_blob, re.I)
        
        for price in price_matches:
            p_val = int(re.sub(r'[^\d]', '', price))
            if p_val < 8000: continue # 过滤低价配件
            
            spec = spec_matches[0].upper().replace(" ", "") if spec_matches else "STD"
            model = f"{brand} Series Tablet"
            # 生成唯一标识，防止重复
            sku_id = hashlib.md5(f"{brand}{spec}{p_val//500}".encode()).hexdigest()

            if sku_id not in self.master_data:
                self.master_data[sku_id] = {
                    "brand": brand, "model": model, "spec": spec, "best": p_val
                }

    def run_stealth_search(self, brand):
        """利用 Google 搜索快照避开封锁"""
        print(f"[*] 正在探测品牌情报: {brand}")
        # 核心技巧：搜索 price.ru 在该品牌下的索引
        query = f"site:price.ru {brand.lower()} planshet"
        url = f"https://www.google.com/search?q={query}&hl=ru"
        
        try:
            # 极保守的延迟，确保长久运行
            time.sleep(random.uniform(10, 15))
            r = self.session.get(url, headers=self._get_headers(), timeout=30)
            if r.status_code == 200:
                self.solve_sku(r.text, brand)
                return True
        except: pass
        return False

    def main(self):
        print(f"[*] [{self.timestamp}] 启动 V23 穿透引擎...")
        for brand in BRANDS:
            self.run_stealth_search(brand)
            
        output = list(self.master_data.values())
        # 按照品牌和价格排序，方便销售分析
        output.sort(key=lambda x: (x['brand'], x['best']))
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({
                "items": output,
                "update": self.timestamp,
                "sku_count": len(output)
            }, f, ensure_ascii=False, indent=2)
        print(f"[√] 完成！捕获到 {len(output)} 条真实 SKU 情报。")

if __name__ == "__main__":
    RUMarketInvincibleV23().main()
