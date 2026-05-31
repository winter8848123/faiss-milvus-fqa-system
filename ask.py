"""
查询脚本 - 从磁盘加载索引到内容并查询售后问题
"""

import os
from data_loader import FQADataLoader
from config import setting


def main():
    """主函数：从磁盘加载索引并查询售后问题"""
    print("FAQ查询系统")
    print("=" * 40)

    # 检查索引文件是否存在
    if not os.path.exists(setting.faiss_index_path):
        print(f"错误：索引文件{setting.faiss_index_path}不存在")
        return

    # 从磁盘加载索引到内存
    print("正在从磁盘加载索引到内存...")
    data_loader = FQADataLoader()
    index = data_loader.load_index(setting.faiss_index_path)

    if index is None:
        print("加载索引失败")
        return

    print("索引加载成功")

    # 查询售后问题
    query = "如何退货"
    print(f"查询：{query}")
    query_engine = index.as_query_engine(similarity_top_k=setting.top_k)
    response = query_engine.query(query)

    print(f"查询结果")
    print("\n" + "=" * 40)
    print(f"最相关的FAQ条数：")
    print("\n" + "=" * 40)

    # 输出条目
    for i, node in enumerate(response.source_nodes, 1):
        metadata = node.node.metadata
        score =node.score
        print(f"\n【FAQ条目 {i}】(相似度: {score:.4f})")
        print(f"问题: {metadata.get('question', 'N/A')}")
        print(f"答案: {metadata.get('answer', 'N/A')}")
        print("-" * 30)


if __name__ == "__main__":
    main()