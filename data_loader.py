"""
FQA数据加载
"""
import os
import re
from typing import Dict,List,Any

from llama_index.core  import (Document,
                               VectorStoreIndex,
                               StorageContext,
                               load_index_from_storage,
                               Settings)
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.llms.dashscope import DashScope

from config import setting


class FQADataLoader:
    """FQA数据加载"""
    def __int__(self):
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


