import os
from config import setting

print(os.path.exists(setting.fqa_file_path))

print("\n")
print(os.path.exists("./FQA.txt"))