"""
简单的文本总结功能 - 用于测试 Summarize 技能概念
"""

def simple_summarize(text, max_sentences=3):
    """简单的文本总结 - 提取前N个句子"""
    sentences = text.split('。')
    # 过滤空句子
    sentences = [s.strip() for s in sentences if s.strip()]
    # 取前N句
    summary = '。'.join(sentences[:max_sentences])
    if summary and not summary.endswith('。'):
        summary += '。'
    return summary

# 测试文本
test_text = """
2026年3月10日，A股市场表现强劲。上证指数开盘4098.59点，最高触及4123.96点，
最低4098.59点，收盘4123.14点，上涨0.65%。成交量达到674922194股，
成交额8505.74亿元。市场整体呈现普涨格局，超过4500只个股上涨。

从板块来看，新能源板块表现突出。光伏、风电等概念股领涨，
晶科科技、协鑫集成等个股涨停。科技股也表现活跃，二六三等通信概念股涨停。

资金流向方面，北向资金净流入超过100亿元，显示外资对A股市场信心充足。
机构资金主要集中在新能源、科技等高成长板块。

展望后市，分析师认为短期市场可能延续震荡反弹格局，
建议关注新能源、科技等主线板块的投资机会，同时注意控制仓位风险。
"""

print("=== 原始文本 ===")
print(test_text[:200] + "...\n")

print("=== 总结结果（3句话）===")
summary = simple_summarize(test_text, 3)
print(summary)

print("\n=== 总结完成 ===")
print(f"原文长度: {len(test_text)} 字符")
print(f"总结长度: {len(summary)} 字符")
print(f"压缩率: {len(summary)/len(test_text)*100:.1f}%")
