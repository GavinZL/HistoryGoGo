"""
明朝皇帝基础数据
用于爬虫的种子数据
"""

# 明朝16位皇帝的基础信息
MING_EMPERORS = [
    {
        "name": "朱元璋",
        "temple_name": "明太祖",
        "reign_title": "洪武",
        "dynasty_order": 1,
        "reign_years": "1368-1398",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱元璋",
        "baidu_url": "https://baike.baidu.com/item/朱元璋"
    },
    {
        "name": "朱允炆",
        "temple_name": "明惠帝",
        "reign_title": "建文",
        "dynasty_order": 2,
        "reign_years": "1398-1402",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱允炆",
        "baidu_url": "https://baike.baidu.com/item/朱允炆"
    },
    {
        "name": "朱棣",
        "temple_name": "明成祖",
        "reign_title": "永乐",
        "dynasty_order": 3,
        "reign_years": "1402-1424",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱棣",
        "baidu_url": "https://baike.baidu.com/item/朱棣"
    },
    {
        "name": "朱高炽",
        "temple_name": "明仁宗",
        "reign_title": "洪熙",
        "dynasty_order": 4,
        "reign_years": "1424-1425",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱高炽",
        "baidu_url": "https://baike.baidu.com/item/朱高炽"
    },
    {
        "name": "朱瞻基",
        "temple_name": "明宣宗",
        "reign_title": "宣德",
        "dynasty_order": 5,
        "reign_years": "1425-1435",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱瞻基",
        "baidu_url": "https://baike.baidu.com/item/朱瞻基"
    },
    {
        "name": "朱祁镇",
        "temple_name": "明英宗",
        "reign_title": "正统/天顺",
        "dynasty_order": 6,
        "reign_years": "1435-1449, 1457-1464",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱祁镇",
        "baidu_url": "https://baike.baidu.com/item/朱祁镇"
    },
    {
        "name": "朱祁钰",
        "temple_name": "明代宗",
        "reign_title": "景泰",
        "dynasty_order": 7,
        "reign_years": "1449-1457",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱祁钰",
        "baidu_url": "https://baike.baidu.com/item/朱祁钰"
    },
    {
        "name": "朱见深",
        "temple_name": "明宪宗",
        "reign_title": "成化",
        "dynasty_order": 8,
        "reign_years": "1464-1487",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱见深",
        "baidu_url": "https://baike.baidu.com/item/朱见深"
    },
    {
        "name": "朱祐樘",
        "temple_name": "明孝宗",
        "reign_title": "弘治",
        "dynasty_order": 9,
        "reign_years": "1487-1505",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱祐樘",
        "baidu_url": "https://baike.baidu.com/item/朱祐樘"
    },
    {
        "name": "朱厚照",
        "temple_name": "明武宗",
        "reign_title": "正德",
        "dynasty_order": 10,
        "reign_years": "1505-1521",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱厚照",
        "baidu_url": "https://baike.baidu.com/item/朱厚照"
    },
    {
        "name": "朱厚熜",
        "temple_name": "明世宗",
        "reign_title": "嘉靖",
        "dynasty_order": 11,
        "reign_years": "1521-1567",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱厚熜",
        "baidu_url": "https://baike.baidu.com/item/朱厚熜"
    },
    {
        "name": "朱载坖",
        "temple_name": "明穆宗",
        "reign_title": "隆庆",
        "dynasty_order": 12,
        "reign_years": "1567-1572",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱载坖",
        "baidu_url": "https://baike.baidu.com/item/朱载坖"
    },
    {
        "name": "朱翊钧",
        "temple_name": "明神宗",
        "reign_title": "万历",
        "dynasty_order": 13,
        "reign_years": "1572-1620",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱翊钧",
        "baidu_url": "https://baike.baidu.com/item/朱翊钧"
    },
    {
        "name": "朱常洛",
        "temple_name": "明光宗",
        "reign_title": "泰昌",
        "dynasty_order": 14,
        "reign_years": "1620-1620",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱常洛",
        "baidu_url": "https://baike.baidu.com/item/朱常洛"
    },
    {
        "name": "朱由校",
        "temple_name": "明熹宗",
        "reign_title": "天启",
        "dynasty_order": 15,
        "reign_years": "1620-1627",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱由校",
        "baidu_url": "https://baike.baidu.com/item/朱由校"
    },
    {
        "name": "朱由检",
        "temple_name": "明思宗",
        "reign_title": "崇祯",
        "dynasty_order": 16,
        "reign_years": "1627-1644",
        "wikipedia_url": "https://zh.wikipedia.org/wiki/朱由检",
        "baidu_url": "https://baike.baidu.com/item/朱由检"
    }
]

# 明朝基础信息
MING_DYNASTY = {
    "dynasty_id": "ming",
    "name": "明朝",
    "start_year": 1368,
    "end_year": 1644,
    "capital": "北京",
    "founder": "朱元璋",
    "description": "明朝（1368年-1644年）是中国历史上最后一个由汉族建立的大一统王朝，共传十六帝，享国276年。"
}
