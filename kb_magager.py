"""
知识库管理器 -实现知识库的动态管理功能
包括FAQ条目的增删改查 、批量导入导出 、版本管理
"""

import os
import json
import shutil
import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pandas as pd
import re

from data_loader import FAQDataLoader
from config import setting


class KnowledgeBaseManager:
    """初始化知识库管理器"""

    def __init__(self, faq_file_path: str, index_path: str):
        """初始化知识库管理器"""
        self.faq_file_path = faq_file_path or setting.faq_file_path
        self.index_path = index_path or setting.faiss_index_path
        self.data_loader = FAQDataLoader()

        # 版本管理相关路径
        self.backup_dir = "./data/backups"
        self.version_file = "./data/version.json"

        # 确保必要目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.version_file), exist_ok=True)

        # 初始化版本信息
        self.__init_version_info()

    def __init_version_info(self):
        """初始化版本信息"""
        if not os.path.exists(self.version_file):
            version_info = {
                "current_version": "1.0.0",
                "versions": [],
                "created_at": datetime.datetime.now().isoformat()
            }
            with open(self.version_file, "w", encoding="utf-8") as f:
                json.dump(version_info, f, ensure_ascii=False, indent=2)

    def __get_version_info(self) -> Dict[str, Any]:
        """获取版本信息"""
        with open(self.version_file, "r", encoding="utf-8") as f:
            print("获取版本信息：" + json.load(f))
            return json.load(f)

    def __update_version_info(self, version_info: Dict[str, Any]):
        """更新版本信息"""
        with open(self.version_file, "w", encoding="utf-8") as f:
            json.dump(version_info, f, ensure_ascii=False, indent=2)

    def __generate_version_info(self) -> str:
        """生成新的版本号"""
        version_info = self.__init_version_info()
        current = version_info["current_version"]
        major, minor, patch = map(int, current.split("."))

        return f"{major}.{minor}.{patch + 1}"

    # FAQ 条目的增删改查功能
    def get_all_faqs(self) -> List[Dict[str, Any]]:
        """获取所有FAQ条目"""
        if not os.path.exists(self.faq_file_path):
            return []
        return self.data_loader.parse_faq_file(self.faq_file_path)

    def get_faq_by_id(self, faq_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取FAQ条目"""
        faqs = self.get_all_faqs()
        for faq in faqs:
            if faq["id"] == faq_id:
                return faq

        return None

    def reseach_faq(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索FAQ条目"""
        faqs = self.get_all_faqs()
        result = []
        keyword_lower = keyword.lower()

        for faq in faqs:
            if keyword_lower in faq["question"].lower() or keyword_lower in faq["answer"].lower():
                result.append(faq)

        return result

    def add_faq(self, question: str, answer: str, auto_rebuild: bool = True):
        """添加新的FAQ条目"""
        faqs = self.get_all_faqs()

        # 生成新的ID
        new_id = max([faq["id"] for faq in faqs], default=0) + 1
        new_faq = {
            "id": new_id,
            "question": question.strip(),
            "answer": answer.strip()
        }

        faqs.append(new_faq)
        self._save_faqs_to_file(faqs)

        if auto_rebuild:
            self.rebuild_index()

    def update_faq(self, faq_id: int, question: str = None, answer: str = None, auto_rebuild: bool = True) -> bool:
        """更新条目"""
        faqs = self.get_all_faqs()

        for faq in faqs:
            if faq["id"] == faq_id:
                if question:
                    faq["question"] = question.strip()
                if answer:
                    faq["answer"] = answer.strip()

                self._save_faqs_to_file(faqs)

                if auto_rebuild:
                    self.rebuild_index()

                return True

        return False

    def delete_faq(self, faq_id: int, auto_rebuild: bool = True) -> bool:
        """删除条目"""
        faqs = self.get_all_faqs()
        original_count = len(faqs)
        faqs = [faq for faq in faqs if faq["id"] != faq_id]

        if len(faqs) < original_count:
            # 重新分配id以保持连续性
            for i, faq in enumerate(faqs, start=1):
                faq["id"] = i
                self._save_faqs_to_file(faqs)

                if auto_rebuild:
                    self.rebuild_index()

                return True

        return False

    def _save_faqs_to_file(self, faqs: List[Dict[str, Any]]):
        """保存FAQ条目到文件"""
        content = ""
        for faq in faqs:
            content += f"Q: {faq['question']}\nA: {faq['answer']}\n\n"

        with open(self.faq_file_path, "w", encoding="utf-8") as f:
            f.write(content.rstrip() + "\n")

    # 动态知识库更新
    def rebuild_index(self):
        """重建索引"""
        try:
            print("正在重建索引...")
            index = self.data_loader.initialize_faq_system(force_rebuild=True)
            print("向量索引重建成功")
            return True
        except Exception as e:
            print(f"重建索引失败：{e}")
            return False

    def update_knowledge_base(self, new_faqs: List[Dict[str, str]],
                              merge_strategy: str = "append") -> bool:
        """
        更新知识库
        args:
            new_faqs:新的FAQ列表，格式为[{”question":...,"answer":"..."
            merge_strategy:合并策略，“append"追加  或者 "replace"
        :param new_faqs:
        :return:
        """
        try:
            if merge_strategy == "replace":
                # 替换模式：清空现有的FAQ，使用新FAQ
                faqs = []
                for i, faq_data in enumerate(new_faqs, 1):
                    faqs.append({
                        "id": i,
                        "question": faq_data['question'].strip(),
                        "answer": faq_data['answer'].strip()
                    })

            else:
                # 追加模式
                faqs = self.get_all_faqs()
                current_max_id = max([faq["id"] for faq in faqs], default=0)

                for i, faq_data in enumerate(new_faqs, 1):
                    faqs.append({
                        'id': current_max_id + 1,
                        "question": faq_data["question"].strip(),
                        "answer": faq_data['answer'].strip()
                    })

            self._save_faqs_to_file(faqs)
            self.rebuild_index()

            print(f"知识库更新完成，共{len(faqs)}个FAQ条目")

            return True

        except Exception as e:
            print(f"更新失败：{str(e)}")

    # 批量导入导出功能

    def export_to_json(self, output_path: str) -> bool:
        """导出FAQ到JSON文件"""
        try:
            faqs = self.get_all_faqs()
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(faqs, f, ensure_ascii=True, encoding="utf-8-sig")

            print(f"FAQ已导出{output_path}")
            return True

        except Exception as e:
            print(f"导出到JSON文件失败{str(e)}")

    def export_to_csv(self, output_path: str) -> bool:
        """导出FAQ到CSV文件"""
        try:
            faqs = self.get_all_faqs()
            df = pd.DataFrame(faqs)
            df.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"FAQ已导出到{output_path}")

            return True

        except Exception as e:
            print(f"导出到csv失败：{str(e)}")
            return False

    def export_to_txt(self, output_path: str) -> bool:
        """导出FAQ到TXT文件"""
        try:
            shutil.copy2(self.faq_file_path, output_path)
            print(f"FAQ已导出到: {output_path}")
            return True
        except Exception as e:
            print(f"导出到TXT失败: {str(e)}")
            return False

    def import_from_json(self, input_path: str, merge_strategy: str = "append") -> bool:
        """从JSON文件导入FAQ"""
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 转换格式
            new_faqs = []
            for item in data:
                if isinstance(item, dict) and "question" in item and "answer" in item:
                    new_faqs.append({
                        "question": item['question'],
                        "answer": item["answer"]
                    })

            return self.update_knowledge_base(new_faqs, merge_strategy)

        except Exception as e:
            print(f"从json导入失败")
            return False

    def import_from_csv(self, input_path: str, merge_strategy: str = "append") -> bool:
        """从CSV文件导入FAQ"""
        try:
            df = pd.read_csv(input_path, encoding='utf-8-sig')

            # 检查必要的列
            if 'question' not in df.columns or 'answer' not in df.columns:
                print("CSV文件必须包含'question'和'answer'列")
                return False

            new_faqs = []
            for _, row in df.iterrows():
                new_faqs.append({
                    'question': str(row['question']),
                    'answer': str(row['answer'])
                })

            return self.update_knowledge_base(new_faqs, merge_strategy)

        except Exception as e:
            print(f"从CSV导入失败: {str(e)}")
            return False

    def import_from_txt(self, input_path: str, merge_strategy: str = "append") -> bool:
        """从TXT文件导入FAQ"""
        try:
            # 解析TXT文件
            new_faqs_data = self.data_loader.parse_faq_file(input_path)

            new_faqs = []
            for faq in new_faqs_data:
                new_faqs.append({
                    'question': faq['question'],
                    'answer': faq['answer']
                })

            return self.update_knowledge_base(new_faqs, merge_strategy)

        except Exception as e:
            print(f"从TXT导入失败: {str(e)}")
            return False
