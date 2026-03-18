#!/usr/bin/env python3
"""
AI Daily Report Generator
每天自动生成AI新闻日报（使用Tavily API + 翻译）
数据保存为JSON，网页独立渲染
"""

import os
import json
import requests
from datetime import datetime, timedelta

# 配置
SITE_NAME = "AI Daily Report"
SITE_DESCRIPTION = "每天更新AI科技新闻日报"
GITHUB_REPO = "DevinLinFD/ai-daily-report"
SITE_URL = f"https://{GITHUB_REPO.split('/')[0]}.github.io/{GITHUB_REPO.split('/')[1]}/"

# Tavily API配置（优先从环境变量读取）
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "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")
TAVILY_API_URL = "https://api.tavily.com/search"

# 搜索关键词（按分类）
SEARCH_CATEGORIES = {
    "AI模型发布": ["OpenAI", "GPT", "Claude", "Anthropic", "AI model release", "AI model launch"],
    "芯片与硬件": ["Nvidia", "GPU", "AI chip", "TPU", "semiconductor", "hardware"],
    "大公司动态": ["Google", "Microsoft", "Meta", "Amazon", "Apple", "AI announcement"],
    "创业公司": ["AI startup", "funding", "Series", "venture capital"],
    "AI应用": ["AI application", "AI tool", "AI product", "AI platform"],
    "研究论文": ["AI research", "paper", "arXiv", "NeurIPS", "ICML"],
    "政策法规": ["AI regulation", "AI policy", "EU AI Act", "AI law"],
    "行业趋势": ["AI trend", "AI market", "AI industry", "AI adoption"]
}

def get_today_date():
    """获取今天的日期"""
    today = datetime.now()
    return today.strftime("%Y年%m月%d日")

def translate_to_chinese(text):
    """翻译成中文（使用免费翻译API）"""
    # 临时禁用翻译，直接返回原文
    return text
    """
    try:
        # 使用Google Translate的免费API
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",  # 自动检测源语言
            "tl": "zh-CN",  # 翻译成中文
            "dt": "t",
            "q": text
        }

        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            translated = ""
            for item in result[0]:
                if item[0]:
                    translated += item[0]
            return translated
        return text
    except Exception as e:
        print(f"⚠️ 翻译失败: {str(e)}")
        return text
    """

def search_tavily(query, max_results=3):
    """使用Tavily API搜索"""
    try:
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
            "include_images": False
        }

        print(f"    🔎 搜索: {query}")
        response = requests.post(TAVILY_API_URL, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"    ✓ 返回 {len(results)} 条结果")
            return results
        else:
            print(f"    ✗ API错误: {response.status_code}")
            return []
    except Exception as e:
        print(f"    ⚠️ 异常: {str(e)}")
        return []

def get_all_news():
    """获取所有分类的新闻"""
    print("🔍 开始搜索AI新闻...")
    all_news = {}

    for category, keywords in SEARCH_CATEGORIES.items():
        print(f"  📂 {category}...")

        # 简化搜索：只用第一个关键词
        query = keywords[0] if keywords else "AI"
        results = search_tavily(query, max_results=3)

        category_news = []
        for result in results:
            # 提取并翻译
            title = translate_to_chinese(result.get("title", ""))
            content = translate_to_chinese(result.get("content", ""))
            url = result.get("url", "")
            published_date = result.get("published_date", "")

            category_news.append({
                "title": title,
                "content": content,
                "url": url,
                "published_date": published_date
            })

        if category_news:
            all_news[category] = category_news
            print(f"    ✓ 找到 {len(category_news)} 条")

    return all_news

def save_data_json(all_news, filename="data.json"):
    """保存数据为JSON文件"""
    data = {
        "metadata": {
            "site_name": SITE_NAME,
            "site_description": SITE_DESCRIPTION,
            "site_url": SITE_URL,
            "generated_date": get_today_date(),
            "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generated_timestamp": int(datetime.now().timestamp()),
            "categories_count": len(all_news),
            "total_news": sum(len(news) for news in all_news.values())
        },
        "categories": all_news
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {filename}")

def deploy_to_gh_pages():
    """部署到gh-pages分支 - 已弃用，由GitHub Actions自动处理"""
    print("ℹ️ 部署由GitHub Actions自动处理，无需手动操作")

def main():
    """主函数"""
    print(f"🚀 开始生成AI日报...")
    print(f"📅 日期: {get_today_date()}")
    print()

    # 搜索新闻
    all_news = get_all_news()
    print()

    total = sum(len(news) for news in all_news.values())
    print(f"✨ 共整理出 {total} 条新闻，{len(all_news)} 个分类")
    print()

    # 保存JSON数据
    save_data_json(all_news)

    # 部署
    deploy_to_gh_pages()

    print()
    print("✅ 数据生成完成！")
    print(f"🌐 访问: {SITE_URL}")

if __name__ == "__main__":
    main()
