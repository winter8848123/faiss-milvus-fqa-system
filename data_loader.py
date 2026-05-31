"""
FAQ数据加载
"""
import os
import re
from typing import Dict, List, Any

from llama_index.core import (Document,
                              VectorStoreIndex,
                              StorageContext,
                              load_index_from_storage,
                              Settings)
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.llms.dashscope import DashScope

from config import setting


class FAQDataLoader:
    """FAQ数据加载"""

    def __init__(self):
        """初始化"""
        embed_model = DashScopeEmbedding(
            api_key=setting.dashscope_api_key,
            model=setting.dashscope_embedding_model,
            dimension=setting.vector_dimension,
            batch_size=10,
        )

        llm = DashScope(api_key=setting.dashscope_api_key)

        Settings.embed_model = embed_model
        Settings.llm = llm
    #
    # def parse_faq_file(self, file_path) -> List[Dict[str, Any]]:
    #     """解析FAQ文件"""
    #     with open(file_path, "r", encoding="utf-8") as f:
    #         content = f.read()  # 读取文件内容
    #
    #     qa_parttern = r'Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|$)' # 正则条件
    #     matches = re.findall(qa_parttern, content, re.DOTALL)  # 使用正则实现筛选匹配
    #
    #     faq_items = []
    #     for i, (question, answer) in enumerate(matches):  # 迭代实现加入列表
    #         faq_items.append({
    #             "id": i+1,
    #             "question": question.strip(),
    #             "answer": answer.strip()
    #         })
    #         print(f"筛选的{len(faq_items)}")
    #
    #         return faq_items
    def parse_faq_file(self, file_path: str) -> List[Dict[str, Any]]:
        """解析FAQ文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        qa_pattern = r'Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|$)'
        matches = re.findall(qa_pattern, content, re.DOTALL)

        faq_items = []
        for i, (question, answer) in enumerate(matches):
            faq_items.append({
                'id': i + 1,
                'question': question.strip(),
                'answer': answer.strip()
            })

        return faq_items

    def create_documents(self, faq_items: List[Dict[str, Any]]) -> List[Document]:
        """构建文档"""
        documents = []
        for item in faq_items:
            content = f"问题：{item['question']}\n 答案：{item['answer']}"

            document = Document(
                text=content,
                metadata={
                    "id": item["id"],
                    "question": item["question"],
                    "answer": item["answer"]
                }
            )
            documents.append(document)

        return documents

    def build_vector_index(self, documents: List[Document]) -> VectorStoreIndex:
        """构建向量索引"""
        index = VectorStoreIndex.from_documents(documents, show_progress=True)

        return index

    def save_index(self, index: VectorStoreIndex, index_path: str):
        """保存索引"""
        os.makedirs(index_path, exist_ok=True)
        index.storage_context.persist(index_path)

    def load_index(self, index_path: str):
        """加载索引"""
        if index_path is None:
            index_path = setting.faiss_index_path
        store_context = StorageContext.from_defaults(persist_dir=index_path)
        index = load_index_from_storage(store_context)
        return index

    def initialize_faq_system(self, force_rebuild: bool = False) -> VectorStoreIndex:
        """初始化FAQ系统"""
        index_path = setting.faiss_index_path

        if force_rebuild or not os.path.exists(index_path):
            print(f"构建新的向量索引")
            faq_items = self.parse_faq_file(setting.faq_file_path)
            print(f"解析到{len(faq_items)}个条目")
            documents = self.create_documents(faq_items)
            index = self.build_vector_index(documents)
            self.save_index(index, index_path)

        else:
            print(f"加载已有的向量索引")
            index = self.load_index(index_path)

        return index
