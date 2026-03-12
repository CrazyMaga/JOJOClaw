import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

def search_macbook_neo():
    """使用多个搜索引擎搜索 MacBook Neo 评价"""
    
    results = []
    
    # 1. 尝试 Bing 搜索
    try:
        query = "MacBook Neo review 评测"
        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取搜索结果
        for item in soup.find_all('li', class_='b_algo')[:3]:
            title_tag = item.find('a')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href', '')
                snippet_tag = item.find('p')
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                
                if 'macbook' in title.lower() or 'mac' in title.lower():
                    results.append({
                        'source': 'Bing',
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })
    except Exception as e:
        print(f"Bing 搜索失败: {e}")
    
    return results

def fetch_page_content(url):
    """获取页面内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题
        title = soup.find('title')
        title = title.get_text() if title else "No title"
        
        # 提取主要内容
        paragraphs = soup.find_all('p')
        content = []
        for p in paragraphs[:10]:
            text = p.get_text(strip=True)
            if len(text) > 50:
                content.append(text)
        
        return {
            'title': title,
            'content': '\n'.join(content[:5])
        }
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    print("="*70)
    print("MacBook Neo 评价搜索")
    print("="*70)
    
    results = search_macbook_neo()
    
    if results:
        print(f"\n找到 {len(results)} 条相关结果：\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   来源: {result['source']}")
            print(f"   链接: {result['link']}")
            if result['snippet']:
                print(f"   摘要: {result['snippet'][:200]}...")
            print()
    else:
        print("\n未找到 MacBook Neo 的具体评测")
        print("\n可能的原因：")
        print("1. 'MacBook Neo' 可能不是官方产品名称")
        print("2. 可能是特定地区或渠道的命名")
        print("3. 产品可能尚未正式发布")
        
        print("\n建议搜索关键词：")
        print("- MacBook Air M3 评测")
        print("- MacBook Pro M3 评测") 
        print("- 新款 MacBook 2024/2025 评测")
    
    print("\n" + "="*70)
