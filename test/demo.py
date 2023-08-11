import sys
import os
import base64

project_dir = os.path.join(os.path.dirname(os.getcwd()),"easyofd")
sys.path.insert(0,project_dir)
print(project_dir)
from main import OFD2PDF

if __name__ == "__main__":
    with open(r"增值税电子专票5.ofd","rb") as f:
        ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    pdf_bytes = OFD2PDF()(ofdb64)
    with open(r"test.pdf","wb") as f:
        ofdb64 = f.write(pdf_bytes)
       