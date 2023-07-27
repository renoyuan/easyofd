
#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: E:\code\pyofdpaerser\test
#CREATE_TIME: 2023-03-28 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 

if __name__ == "__main__":
    import time
    import json
    import base64
    import sys
    import os
    
    print(os.path.abspath( os.path.dirname(os.getcwd())))
    sys.path.insert(0,os.path.abspath( os.path.dirname(os.getcwd())))
    print(sys.path)
    from easyofd import OfdParser
    f = open("增值税电子专票5.ofd","rb")
    ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    f.close
    t = time.time()
    # 传入b64 字符串
    data_dict = OfdParser(ofdb64).parserodf2json()
    pdfbytes = OfdParser(ofdb64).ofd2pdf()
    with open(f"test.pdf","wb") as f:
            f.write(pdfbytes)
    print(data_dict)
    print(f"ofd解析耗时{(time.time()-t)*1000}/ms")	
    json.dump(data_dict,open("data_dict.json","w",encoding="utf-8"),ensure_ascii=False,indent=4)