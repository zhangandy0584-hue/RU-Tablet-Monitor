import requests
import json
import time
import random
import re
import os
import hashlib
from datetime import datetime

# ================= 工业级配置：10大品牌 + 6大渠道 =================
BRANDS = ["TECNO", "Infinix", "Xiaomi", "Huawei", "Samsung", "Apple", "Redmi", "Realme", "Honor", "Lenovo"]
CHANNELS = ["dns", "mvideo", "citilink", "ozon", "wildberries", "yandex"]

class RUMarketDragonV20:
    def __init__(self):
        self.master_data = {}
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
    def _get_mutated_headers(self):
        """核心对抗：俄系 A-Parser 随机字典序变异"""
        uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0"
        ]
        headers = {
            "User-Agent": random.choice(uas),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
            "X-Forwarded-For": f"185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "DNT": "1",
            "Connection": "keep-alive"
        }
        # 乱序变异逻辑（对抗 WAF 签名）
        h_list = list(headers.items())
        random.shuffle(h_list)
        return dict(h_list)

    def solve_sku(self, name, price, brand, tag):
        """语义解析：规格识别 + MD5 哈希去重"""
        try:
            p_val = int(re.sub(r'[^\d]', '', str(price)))
            if p_val < 8500: return 

            # 规格提取 (RAM/ROM)
            spec_m = re.search(r'(\d+[\s/+]?(\d+GB|\d+TB|\d+ГБ))', name, re.I)
            spec = spec_m.group(0).upper().replace(" ", "") if spec_m else "STD"
            model = name.upper().replace("ПЛАНШЕТ", "").replace(brand.upper(), "").split('(')[0].strip()[:35]
            
            # 生成唯一标识符
            sku_id = hashlib.md5(f"{brand}{model}{spec}".encode()).hexdigest()

            if sku_id not in self.master_data:
                self.master_data[sku_id] = {
                    "brand": brand, "model": model, "spec": spec,
                    "prices": {ch: 0 for ch in CHANNELS},
                    "best": p_val, "avg": 0, "strategy": tag, "id": sku_id
                }
            
            # 6 渠道对撞逻辑
            n_low = name.lower()
            for ch in CHANNELS:
                if ch in n_low:
                    curr = self.master_data[sku_id]["prices"][ch]
                    if curr == 0 or p_val < curr:
                        self.master_data[sku_id]["prices"][ch] = p_val
            
            # 动态底价计算
            actives = [v for v in self.master_data[sku_id]["prices"].values() if v > 0]
            self.master_data[sku_id]["best"] = min(actives)
            self.master_data[sku_id]["avg"] = sum(actives) / len(actives)
        except: pass

    def run(self):
        # 增量持久化检查
        if os.path.exists('data.json'):
            try:
                with open('data.json', 'r', encoding='utf-8') as f:
                    self.master_data = json.load(f).get('raw_dict', {})
            except: pass

        session = requests.Session()
        for brand in BRANDS:
            print(f"[*] [V20 Final] 正在穿透品牌: {brand}")
            # 需求：强制 10 页深度探测，绝不减料
            for p in range(1, 11):
                try:
                    url = f"https://price.ru/search/?query=planshet+{brand.lower()}&page={p}"
                    # 拟人化指数级退避
                    time.sleep(random.uniform(25, 45))
                    r = session.get(url, headers=self._get_mutated_headers(), timeout=50)
                    if "captcha" in r.text.lower(): break
                    items = re.findall(r'title="(.*?)".*?price">(\d+[\s\d]*)', r.text, re.S)
                    if not items: break
                    for n, pr in items: self.solve_sku(n, pr, brand, f"P{p}")
                except: continue
            self.save_checkpoint()

    def save_checkpoint(self):
        output = sorted(list(self.master_data.values()), key=lambda x: (x['brand'], x['best']))
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({
                "items": output, "raw_dict": self.master_data, 
                "update": self.timestamp, "sku_count": len(output)
            }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    RUMarketDragonV20().run()
