#!/usr/bin/env python3
"""
AI Daily Report Generator
每天自动生成AI新闻日报
"""

import os
import json
from datetime import datetime, timedelta
import subprocess
import requests

# 配置
SITE_NAME = "AI Daily Report"
SITE_DESCRIPTION = "每天更新AI科技新闻日报"
GITHUB_REPO = "你的用户名/ai-daily-report"  # TODO: 替换为你的GitHub仓库
SITE_URL = f"https://{GITHUB_REPO.split('/')[0]}.github.io/{GITHUB_REPO.split('/')[1]}/"

def get_yesterday_date():
    """获取昨天的日期"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y年%m月%d日")

def get_news_summary():
    """获取AI新闻摘要（调用搜索API）"""
    try:
        # 使用miaoda-studio-cli搜索昨天的AI新闻
        query = f"AI 人工智能 科技 新闻 {get_yesterday_date()}"
        result = subprocess.run(
            ['miaoda-studio-cli', 'search-summary', '--query', query, '--output', 'json'],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get('summary', '搜索失败，请稍后再试')
        else:
            return f"搜索失败: {result.stderr}"

    except Exception as e:
        return f"搜索出错: {str(e)}"

def parse_news_to_items(summary_text):
    """将新闻摘要解析为列表项"""
    items = []

    # 简单解析：按行分割
    lines = summary_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and (line.startswith('•') or line.startswith('-') or line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
            # 去掉行首标记
            clean_line = line.lstrip('•-').lstrip()
            if clean_line[0].isdigit() and '.' in clean_line[:5]:
                clean_line = clean_line.split('.', 1)[1].strip()
            items.append(clean_line)
        elif line and len(line) > 20 and not line.startswith('#'):
            items.append(line)

    return items[:10]  # 最多返回10条

def generate_html(news_items):
    """生成HTML页面"""
    date_str = get_yesterday_date()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_NAME} - {date_str}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .glass {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
        }}
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="glass rounded-2xl shadow-2xl p-8 mb-8 text-center">
            <h1 class="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
                🤖 {SITE_NAME}
            </h1>
            <p class="text-xl text-gray-600 mb-2">{SITE_DESCRIPTION}</p>
            <p class="text-gray-500">📅 {date_str}</p>
            <p class="text-sm text-gray-400 mt-2">更新时间: {timestamp}</p>
        </div>

        <!-- News Items -->
        <div class="glass rounded-2xl shadow-2xl p-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <span class="mr-2">📰</span>
                今日AI新闻
            </h2>

            <div class="space-y-4">
                {"".join([f'''
                <div class="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-5 border border-purple-100 hover:shadow-lg transition-shadow">
                    <p class="text-gray-700 leading-relaxed">{item}</p>
                </div>
                ''' for item in news_items])}
            </div>

            <!-- Empty state -->
            {'''
            <div class="text-center py-12 text-gray-500">
                <p class="text-6xl mb-4">🤔</p>
                <p>今天暂无新闻</p>
            </div>
            ''' if not news_items else ''}
        </div>

        <!-- Footer -->
        <div class="glass rounded-2xl shadow-2xl p-6 mt-8 text-center">
            <p class="text-gray-600">
                🦞 由 <strong>林的助手</strong> 自动生成
            </p>
            <p class="text-sm text-gray-500 mt-2">
                基于 GitHub Actions + GitHub Pages 自动部署
            </p>
            <a href="{SITE_URL}" class="inline-block mt-4 text-purple-600 hover:text-purple-800">
                🏠 访问网站
            </a>
        </div>
    </div>
</body>
</html>"""

    return html_template

def save_html(html_content, filename="index.html"):
    """保存HTML文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ 已生成 {filename}")

def main():
    """主函数"""
    print(f"🚀 开始生成AI日报...")
    print(f"📅 日期: {get_yesterday_date()}")

    # 获取新闻
    print("🔍 正在搜索AI新闻...")
    news_summary = get_news_summary()
    print(f"📰 搜索完成")

    # 解析新闻
    news_items = parse_news_to_items(news_summary)
    print(f"✨ 整理出 {len(news_items)} 条新闻")

    # 生成HTML
    print("🎨 正在生成网页...")
    html_content = generate_html(news_items)

    # 保存
    save_html(html_content)

    print("✅ 日报生成完成！")

if __name__ == "__main__":
    main()
