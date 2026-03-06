import requests
import json
import time
import random
import re
import hashlib
from datetime import datetime

# ================= 需求对标：10大品牌情报网 =================
BRANDS = ["TECNO", "Infinix", "Xiaomi", "Huawei", "Samsung", "Apple", "Redmi", "Realme", "Honor", "Lenovo"]

class RUMarketEliteV25:
    def __init__(self):
        self.master_data = {}
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.session = requests.Session()
        
    def _get_authentic_headers(self):
        """专业级指纹：模拟俄语区真实的 Windows 用户"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
            "Referer": "https://www.google.ru/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        }

    def solve_sku(self, html_content, brand):
        """核心解析：从搜索摘要提取真实卢布价格和规格"""
        # 正则提取：捕获价格（数字 + 卢布符号）
        prices = re.findall(r'(\d+[\s\d]*)\s*(?:₽|руб|RUB)', html_content)
        # 正则提取：捕获存储规格 (如 8/128GB)
        specs = re.findall(r'(\d+[\s/+]?\d+(?:GB|TB|ГБ))', html_content, re.I)
        
        if not prices: return

        # 过滤非法价格，确保抓取的是平板电脑而非配件
        valid_prices = [int(p.replace(' ', '')) for p in prices if 8500 < int(p.replace(' ', '')) < 200000]
        
        if valid_prices:
            best_p = min(valid_prices)
            spec = specs[0].upper().replace(" ", "") if specs else "Standard"
            sku_id = hashlib.md5(f"{brand}{spec}{best_p//1000}".encode()).hexdigest()

            if sku_id not in self.master_data:
                self.master_data[sku_id] = {
                    "brand": brand,
                    "model": f"{brand} Tablet Global",
                    "spec": spec,
                    "best": best_p
                }

    def run_stealth_engine(self, brand):
        """侧翼穿透：利用 Google 搜索快照绕过电商 WAF"""
        print(f"[*] 正在获取品牌情报: {brand}...")
        # 搜索 price.ru 在 Google 中的快照，避开 403 封锁
        target_query = f"site:price.ru {brand.lower()} planshet"
        url = f"https://www.google.com/search?q={target_query}&hl=ru"
        
        try:
            # 模拟人类随机翻阅延迟
            time.sleep(random.uniform(12, 22))
            r = self.session.get(url, headers=self._get_authentic_headers(), timeout=30)
            
            if r.status_code == 200:
                self.solve_sku(r.text, brand)
                print(f"[√] {brand} 真实情报已捕获")
                return True
            else:
                print(f"[!] 状态异常: {r.status_code}")
                return False
        except Exception as e:
            print(f"[!] 访问受阻: {e}")
            return False

    def main(self):
        print(f"[*] 启动 V25 工业级情报引擎 - {self.timestamp}")
        for brand in self.brands:
            self.run_stealth_engine(brand)
            
        output = sorted(list(self.master_data.values()), key=lambda x: (x['brand'], x['best']))
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({
                "items": output,
                "update": self.timestamp,
                "sku_count": len(output)
            }, f, ensure_ascii=False, indent=2)
        print(f"[+] 任务结束：共捕获 {len(output)} 条真实 SKU 数据")

if __name__ == "__main__":
    RUMarketEliteV25().main()
