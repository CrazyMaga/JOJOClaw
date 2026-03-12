import tushare as ts

# 设置 Token
ts.set_token('a8045f6bdc487eddca70b235c8b16cc0e2b3fbcb862b2c48755f73fd')

print('Tushare token 已设置成功！')
print('现在可以使用 tushare 获取金融数据了。')

# 测试连接
try:
    # 尝试获取一个简单数据集来验证
    df = ts.get_index_info()
    print(f'\n✓ 连接验证成功，共 {len(df)} 个市场指数可用')
except Exception as e:
    print(f'⚠ 连接检查：{e}')
