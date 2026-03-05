import requests
import json
import time
import random
import re
import hashlib
from datetime import datetime

# 配置：10大核心品牌 + 深度探测逻辑
BRANDS = ["TECNO", "Infinix", "Xiaomi", "Huawei", "Samsung", "Apple", "Redmi", "Realme", "Honor", "Lenovo"]

class RUMarketDragonV20:
    def __init__(self):
        self.master_data = {}
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.session = requests.Session()
        
    def _get_headers(self):
        uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0"
        ]
        return {"User-Agent": random.choice(uas), "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8"}

    def solve_sku(self, name, price, brand):
        try:
            p_val = int(re.sub(r'[^\d]', '', str(price)))
            if p_val < 8000: return 
            spec_m = re.search(r'(\d+[\s/+]?(\d+GB|\d+TB|\d+ГБ))', name, re.I)
            spec = spec_m.group(0).upper().replace(" ", "") if spec_m else "STD"
            model = name.upper().replace("ПЛАНШЕТ", "").replace(brand.upper(), "").split('(')[0].strip()[:35]
            sku_id = hashlib.md5(f"{brand}{model}{spec}".encode()).hexdigest()

            if sku_id not in self.master_data:
                self.master_data[sku_id] = {
                    "brand": brand, "model": model, "spec": spec, "best": p_val
                }
        except: pass

    def run(self):
        print(f"[*] 启动全俄市场情报矩阵 - {self.timestamp}")
        for brand in BRANDS:
            print(f"[*] 正在穿透品牌: {brand}")
            for p in range(1, 11): # 强制 10 页深度
                try:
                    url = f"https://price.ru/search/?query=planshet+{brand.lower()}&page={p}"
                    time.sleep(random.uniform(3, 6)) # 基础频率对抗
                    r = self.session.get(url, headers=self._get_headers(), timeout=30)
                    if "captcha" in r.text.lower(): break
                    items = re.findall(r'title="(.*?)".*?price">(\d+[\s\d]*)', r.text, re.S)
                    if not items: break
                    for n, pr in items: self.solve_sku(n, pr, brand)
                except: continue
        
        # 写入结果
        output = sorted(list(self.master_data.values()), key=lambda x: (x['brand'], x['best']))
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({"items": output, "update": self.timestamp, "sku_count": len(output)}, f, ensure_ascii=False, indent=2)
        print(f"[+] 成功抓取 {len(output)} 个 SKU")

if __name__ == "__main__":
    RUMarketDragonV20().run()
