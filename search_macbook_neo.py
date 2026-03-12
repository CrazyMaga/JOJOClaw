import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_macbook_neo():
    """搜索 MacBook Neo 评价"""
    
    # 使用 Bing 搜索
    query = "MacBook Neo review 评测 评价"
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        print("正在搜索 MacBook Neo 评价...")
        print("="*60)
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找搜索结果
        results = []
        
        # Bing 搜索结果通常在 .b_algo 类中
        for item in soup.find_all('li', class_='b_algo')[:5]:
            try:
                # 提取标题和链接
                title_tag = item.find('a')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link = title_tag.get('href', '')
                    
                    # 提取摘要
                    snippet_tag = item.find('p')
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                    
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })
            except Exception as e:
                continue
        
        if results:
            print(f"\n找到 {len(results)} 条相关结果：\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   链接: {result['link']}")
                if result['snippet']:
                    print(f"   摘要: {result['snippet'][:150]}...")
                print()
        else:
            print("未找到搜索结果，尝试备用方案...")
            # 备用：直接访问几个已知的技术评测网站
            print("\n推荐查看以下网站获取 MacBook Neo 评测：")
            print("1. 知乎 - 搜索 'MacBook Neo 评测'")
            print("2. 什么值得买 - 搜索 'MacBook Neo'")
            print("3. 哔哩哔哩 - 搜索 'MacBook Neo 开箱'")
            print("4. YouTube - 搜索 'MacBook Neo Review'")
            
    except Exception as e:
        print(f"搜索出错: {e}")
        print("\n建议直接访问以下网站查看评测：")
        print("- 知乎: https://www.zhihu.com/search?type=content&q=MacBook+Neo")
        print("- 什么值得买: https://search.smzdm.com/?s=MacBook+Neo")
        print("- 哔哩哔哩: https://search.bilibili.com/all?keyword=MacBook+Neo")

if __name__ == '__main__':
    search_macbook_neo()
