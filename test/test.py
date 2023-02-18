


if __name__ == "__main__":
    import time
    import json
    import base64
    from ofdparser import OfdParser
    f = open("增值税电子专票5.ofd","rb")
    ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    f.close
    t = time.time()
    # 传入b64 字符串
    data_dict = OfdParser(ofdb64).parserodf2json()
    
    print(data_dict)
    print(f"ofd解析耗时{(time.time()-t)*1000}/ms")	
    json.dump(data_dict,open("data_dict.json","w",encoding="utf-8"),ensure_ascii=False,indent=4)