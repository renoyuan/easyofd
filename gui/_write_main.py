#!/usr/bin/env python
"""临时脚本：将当前 main.py 作为字符串写入自身（便于 PyInstaller 单文件打包嵌入）"""
import pathlib

src = pathlib.Path(__file__).resolve().parent / "main.py"
code = src.read_text(encoding="utf-8")

out = pathlib.Path(__file__).resolve().parent / "main_embedded.py"
script = '''#!/usr/bin/env python
"""自写入脚本 - 由 _write_main.py 自动生成"""
import pathlib, sys

code = {code!r}
if __name__ == "__main__":
    dst = pathlib.Path(__file__).resolve().parent / "main.py"
    dst.write_text(code, encoding="utf-8")
    print(f"OK - 已写入 {{dst}}")
'''

with open(out, "w", encoding="utf-8") as f:
    f.write(script.format(code=code))

print(f"OK - main_embedded.py 已生成")

