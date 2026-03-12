import lancedb
import datetime
import json
import os

# 配置
DB_PATH = "C:\\Users\\yezhihong\\.openclaw\\workspace\\.elite-memory.db"

class EliteMemory:
    """Elite Longterm Memory - WARM STORE (向量搜索)"""
    
    def __init__(self):
        self.db = lancedb.connect(DB_PATH)
        self._init_schema()
    
    def _init_schema(self):
        """初始化向量表结构"""
        try:
            # 尝试打开已有表
            self.table = self.db.open_table("memories")
        except:
            # 创建新表
            import pyarrow as pa
            schema = pa.schema([
                ("id", pa.string()),
                ("content", pa.string()),
                ("type", pa.string()),  # preference, decision, context
                ("timestamp", pa.string()),
                ("vector", pa.list_(pa.float32(), 384))  # 384维向量
            ])
            self.table = self.db.create_table("memories", schema=schema)
    
    def add_memory(self, content, memory_type="context"):
        """添加记忆"""
        import hashlib
        
        # 生成简单向量（实际应使用 embedding 模型）
        vector = [float(ord(c)) % 100 / 100 for c in content[:384]]
        while len(vector) < 384:
            vector.append(0.0)
        
        memory_id = hashlib.md5(content.encode()).hexdigest()[:8]
        
        self.table.add([{
            "id": memory_id,
            "content": content,
            "type": memory_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "vector": vector
        }])
        
        return memory_id
    
    def search_memory(self, query, limit=5):
        """搜索记忆"""
        # 生成查询向量
        query_vector = [float(ord(c)) % 100 / 100 for c in query[:384]]
        while len(query_vector) < 384:
            query_vector.append(0.0)
        
        results = self.table.search(query_vector).limit(limit).to_pandas()
        return results
    
    def list_all(self):
        """列出所有记忆"""
        return self.table.to_pandas()

# 测试
if __name__ == "__main__":
    print("=== Elite Longterm Memory - WARM STORE ===\n")
    
    memory = EliteMemory()
    
    # 添加测试记忆
    print("[ADD] Adding memories...")
    memory.add_memory("Master likes cute tone, call 'Master'", "preference")
    memory.add_memory("Check Hangzhou weather at 9am daily", "preference")
    memory.add_memory("Stock query use Tushare only, not AkShare", "decision")
    memory.add_memory("Installed 6 skills: qveris, tushare, tavily-search, self-improving, github-assistant, elite-longterm-memory", "context")
    
    print("[OK] Memories added!\n")
    
    # 搜索记忆
    print("[SEARCH] Search memory 'stock'...")
    results = memory.search_memory("stock")
    print(results[['content', 'type']].to_string(index=False))
    
    print("\n[LIST] All memories:")
    all_memories = memory.list_all()
    print(f"Total: {len(all_memories)} memories")
