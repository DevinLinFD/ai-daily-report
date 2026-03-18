#!/usr/bin/env python3
"""
AI Daily Report Generator
每天自动生成AI新闻日报（使用Tavily API + 翻译）
数据保存为JSON，支持历史数据累积
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

# 搜索关键词（按分类，中英文混合搜索）
SEARCH_CATEGORIES = {
    "AI模型发布": ["OpenAI GPT最新发布", "AI大模型发布", "Claude Gemini最新消息"],
    "芯片与硬件": ["Nvidia GPU AI芯片最新", "AI芯片算力硬件", "TPU半导体最新动态"],
    "大公司动态": ["Google Microsoft Meta AI最新", "百度字节腾讯AI", "科技巨头AI布局"],
    "创业公司": ["AI创业公司融资", "AI startup funding", "人工智能投资并购"],
    "AI应用": ["AI应用工具产品", "AI工具平台发布", "人工智能落地应用"],
    "研究论文": ["AI研究论文最新", "人工智能学术突破", "深度学习前沿研究"],
    "政策法规": ["AI政策监管法规", "人工智能治理", "AI伦理安全法规"],
    "行业趋势": ["AI行业趋势市场", "人工智能市场规模", "AI发展趋势分析"]
}

def get_today_date():
    """获取今天的日期"""
    today = datetime.now()
    return today.strftime("%Y年%m月%d日")

def translate_to_chinese(text):
    """翻译成中文（直接返回原文，翻译在get_all_news中批量处理）"""
    return text

def translate_batch(texts):
    """使用Tavily API批量翻译多条文本"""
    if not texts:
        return texts
    
    # 合并所有需要翻译的文本
    combined = "\n---\n".join([f"[{i}] {t}" for i, t in enumerate(texts)])
    
    try:
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": f"请将以下英文内容逐条翻译成中文，保持格式，每条以[序号]开头：\n{combined}",
            "search_depth": "basic",
            "max_results": 1,
            "include_answer": True
        }
        response = requests.post(TAVILY_API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            answer = response.json().get("answer", "")
            if answer and len(answer) > 10:
                # 解析翻译结果
                results = {}
                import re
                for match in re.finditer(r'\[(\d+)\]\s*(.+?)(?=\[\d+\]|$)', answer, re.DOTALL):
                    idx = int(match.group(1))
                    translated = match.group(2).strip()
                    results[idx] = translated
                
                # 对于没匹配到的，返回原文
                final = []
                for i, t in enumerate(texts):
                    final.append(results.get(i, t))
                print(f"    ✓ 翻译 {len(results)}/{len(texts)} 条")
                return final
        print(f"    ⚠️ 翻译服务未返回结果")
        return texts
    except Exception as e:
        print(f"    ⚠️ 批量翻译失败: {str(e)[:50]}")
        return texts

def search_tavily(query, max_results=3):
    """使用Tavily API搜索"""
    try:
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
            "include_images": False,
            "include_domains": [],
            "exclude_domains": [],
            "topic": "news"
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

        category_news = []
        seen_urls = set()
        
        for query in keywords:
            # 每个关键词搜索2条，避免太多重复
            results = search_tavily(query, max_results=2)

            for result in results:
                url = result.get("url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title = result.get("title", "")
                content = result.get("content", "")
                published_date = result.get("published_date", "")

                category_news.append({
                    "title": title,
                    "content": content,
                    "url": url,
                    "published_date": published_date
                })

            if len(category_news) >= 5:
                break

        if category_news:
            all_news[category] = category_news[:5]
            print(f"    ✓ 找到 {len(category_news)} 条")

    # 批量翻译所有新闻的标题和内容
    print("\n🌐 开始批量翻译...")
    for category, news_list in all_news.items():
        # 收集所有标题和内容
        titles = [n["title"] for n in news_list]
        contents = [n["content"] for n in news_list]
        
        # 批量翻译标题
        translated_titles = translate_batch(titles)
        # 批量翻译内容
        translated_contents = translate_batch(contents)
        
        # 更新翻译结果
        for i, news in enumerate(news_list):
            news["title"] = translated_titles[i]
            news["content"] = translated_contents[i]
        
        print(f"  ✅ {category} 翻译完成")

    return all_news

def load_existing_data(filename="data.json"):
    """加载现有的历史数据，兼容旧格式和新格式"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 兼容旧格式（单日数据）
                if "dates" not in data and "metadata" in data:
                    print(f"⚠️ 检测到旧格式数据，正在迁移...")
                    today = data["metadata"]["generated_date"]
                    new_data = {
                        "dates": {
                            today: data
                        },
                        "latest_date": today
                    }
                    # 立即保存新格式
                    with open(filename, 'w', encoding='utf-8') as f_new:
                        json.dump(new_data, f_new, ensure_ascii=False, indent=2)
                    print(f"✅ 已迁移到新格式")
                    return new_data
                
                # 新格式（多日数据）
                if "dates" in data:
                    return data
                
                return {"dates": {}, "latest_date": ""}
        except Exception as e:
            print(f"⚠️ 读取历史数据失败: {str(e)}")
    return {"dates": {}, "latest_date": ""}

def save_data_json(all_news, filename="data.json"):
    """保存数据为JSON文件，累积历史数据"""
    today = get_today_date()
    
    # 先加载历史数据
    data = load_existing_data(filename)
    
    # 如果今天的数据已存在，先删除（重新生成）
    if today in data["dates"]:
        print(f"⚠️ 今日数据已存在，将重新生成...")
    
    # 构建今日数据
    today_data = {
        "metadata": {
            "site_name": SITE_NAME,
            "site_description": SITE_DESCRIPTION,
            "site_url": SITE_URL,
            "generated_date": today,
            "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generated_timestamp": int(datetime.now().timestamp()),
            "categories_count": len(all_news),
            "total_news": sum(len(news) for news in all_news.values())
        },
        "categories": all_news
    }
    
    # 更新数据
    data["dates"][today] = today_data
    data["latest_date"] = today
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {filename}，共 {len(data['dates'])} 天的数据")

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

    # 保存JSON数据（累积历史）
    save_data_json(all_news)

    # 部署
    deploy_to_gh_pages()

    print()
    print("✅ 数据生成完成！")
    print(f"🌐 访问: {SITE_URL}")

if __name__ == "__main__":
    main()
