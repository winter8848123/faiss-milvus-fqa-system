"""
配置文件
"""

import os
import dotenv
dotenv.load_dotenv(override=True)

#DashScope配置
DASHSCOPE_API_KEY= os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_EMBEDDING_MODEL= "text-embedding-v3"

#向量配置
FAISS_INDEX_PATN = "./data/faiss_index"
VECTOR_DIMENSION=512


FAQ_FILE_PATH="./FAQ.txt"

#检索配置
TOP_K = 3

class Setting:
    """系统配置文件"""
    dashscope_api_key= DASHSCOPE_API_KEY
    dashscope_embedding_model = DASHSCOPE_EMBEDDING_MODEL
    faiss_index_path = FAISS_INDEX_PATN
    vector_dimension = VECTOR_DIMENSION
    faq_file_path = FAQ_FILE_PATH
    top_k = TOP_K


setting = Setting()