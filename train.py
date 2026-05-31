"""
训练脚本  -从FQA.txt 加载数据到faiss向量数据库并保持持久化
"""

import os
from  data_loader import FQADataLoader
from config  import setting

def main():
    """主函数：从FQA.txt加载数据并构建faiss索引"""

    print("开始构建faiss索引")
    #检查API秘钥
    if not setting.dashscope_api_key:
        print("错误：请设置DashScope API密钥")
        return

     #检查FQA文件
    if  not os.path.exists(setting.fqa_file_path):
        print(f"错误：FQA文件{setting.fqa_file_path}不存在")
        return

    #创建爱数据加载并构建索引
    data_loader = FQADataLoader()
    index = data_loader.initialize_faq_system(force_rebuild=True)
    if index :
        print(f"构建成功，索引保存在{setting.faiss_index_path}")

    else:
        print("构建失败")


if __name__ == "__main__":
    main()