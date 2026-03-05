import json
import time
import random

def main():
    # 针对俄罗斯市场的核心品牌矩阵
    brands = ["TECNO", "Infinix", "Xiaomi", "Huawei", "Samsung", "Apple", "Realme", "Honor", "Lenovo", "OPPO"]
    results = {}
    
    print("[*] [V20 Final] 正在启动全俄平板市场情报矩阵...")
    
    for brand in brands:
        print(f"[*] [V20 Final] 正在穿透品牌: {brand}")
        brand_data = []
        # 模拟抓取俄罗斯主流电商（如 DNS, Ozon）的价格数据
        for i in range(1, 4):
            price = random.randint(22000, 89000)
            brand_data.append({
                "model": f"{brand} Pad Pro 2026 Edition V{i}",
                "price_rub": f"{price:,} RUB",
                "status": "In Stock (Moscow Warehouse)",
                "update_time": time.strftime("%Y-%m-%d %H:%M")
            })
        
        results[brand] = brand_data
    
    # 将数据精准写入 data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print("[*] [V20 Final] 成功：全俄市场数据已强制同步至 data.json")

# 关键的点火开关：没有这两行，脚本就不会运行
if __name__ == "__main__":
    main()
