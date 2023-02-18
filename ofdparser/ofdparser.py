# encoding: utf-8
import zipfile
import xmltodict
import requests
import os
import shutil

import string
from uuid import uuid1
import random

def _genShortId(length=12):
        """
        :params length: 默认随机生成的uuid长度
        """
        uuid = str(uuid1()).replace('-', '')
        result = ''
        for i in range(0, 8):
            sub = uuid[i * 4: i * 4 + 4]
            x = int(sub, 16)
            uuidChars = tuple(list(string.ascii_letters) + list(range(10)))
            result += str(uuidChars[x % 0x3E])
        return result + ''.join(random.sample(uuid, length - 8))
    
class OfdParser(object):
    def __init__(self,ofdb64,zip_path="ofd.ofd") -> None:
        ofdbyte = base64.b64decode(ofdb64)
        zip_path = f"{str(_genShortId())}.ofd"
        with open(zip_path,"wb") as f:
            f.write(ofdbyte)
        self.zip_path = zip_path

    # 解压
    def unzip_file(self,zip_path, unzip_path=None):
        """
        :param zip_path: ofd格式文件路径
        :param unzip_path: 解压后的文件存放目录
        :return: unzip_path
        """
        zip_path = self.zip_path
        if not unzip_path:
            unzip_path = zip_path.split('.')[0]
        with zipfile.ZipFile(zip_path, 'r') as f:
            for file in f.namelist():
                f.extract(file, path=unzip_path)
        return unzip_path

    # 提取主要文本内容
    def parse_ofd(self, path) ->list:
        """
        :param content: ofd文件字节内容
        :param path: ofd文件存取路径
        """
        # with open(path, "wb") as f:
            # f.write(content)
        # file_path = unzip_file("path")
        file_path = self.unzip_file(path)
        xml_path = f"{file_path}/OFD.xml" 
        data_dict = {}
        rootPath = ""
        
        # read ROOTPATAH
        with open(xml_path, "r", encoding="utf-8") as f:
            _text = f.read()
            tree = xmltodict.parse(_text)
            rootPath = tree['ofd:OFD']['ofd:DocBody']['ofd:DocRoot']
            
            print(rootPath)
            
        # read contentPath&tplsPath
        with open(f"{file_path}/{rootPath}" , "r", encoding="utf-8") as f:
            _text = f.read()
            tree = xmltodict.parse(_text)
            contentPath = f"{file_path}/{rootPath.split('/')[0]}/{tree['ofd:Document']['ofd:Pages']['ofd:Page']['@BaseLoc']}"
            tplsPath = f"{file_path}/{rootPath.split('/')[0]}/{tree['ofd:Document']['ofd:CommonData']['ofd:TemplatePage']['@BaseLoc']}"
            print(contentPath)
            print(tplsPath)
    
    
        # 以下解析部分
        
        def parserContntXml(path:str)->list:
            cell_list = []
            with open(f"{path}" , "r", encoding="utf-8") as f:
                _text = f.read()
                tree = xmltodict.parse(_text)
                for row in tree['ofd:Page']['ofd:Content']['ofd:Layer']['ofd:TextObject']:
                    # print(row)
                    cell = (row['@Boundary'].split(" "),row['ofd:TextCode'].get('#text'))
                    # check cell null
                    cell = None if (not cell[0] or not cell[1]) else cell
                    if cell:
                        cell_list.append(cell)
                        # print(cell)
            return cell_list
        
        
        cell_list = [] # :cell [[pos,text]]
        cell_list = parserContntXml(contentPath)
        # print(cell_list)
        cell2 = parserContntXml(tplsPath)
    
        cell_list.extend(cell2)
        cell_list.sort(key=lambda pos_text:  (float(pos_text[0][1]),float(pos_text[0][0])))
                
        
        # print(cell_list)
        
        # 删除文件
        # shutil.rmtree(file_path)
        # os.remove(path)
        return cell_list

    # 转json格式
    def odf2json(self, ofd_date:list,dpi=None) ->dict:
        """
        坐标默认为毫米单位 
        dpi 有则转化为px
        """
        Op = 1 # 转换算子单位
        
        
        if dpi:
            Op = dpi/25.4
        document_id = 'v1' + '_' + _genShortId()
        pageList = []
        pageInfo = {}
        pageInfo["pageNo"] = 0
        pageInfo["pageNo"] = 0
        pageInfo["docID"] = document_id
        pageInfo["imageQuality"] ={
            "size": [
                0,
                0
            ]
        }
        pageInfo["lineList"] = []
        # 行信息构建
        for lineNo,values in enumerate(ofd_date):
            line = {}
            pos = []
            line["lineId"] = 'line_' + str(0) + '_' + str(lineNo) + '_' + _genShortId()
            line["lineNo"] = lineNo
            line["sortNo"] = lineNo
            line["rowNo"] = lineNo
            line["objType_postpreprocess"] = "text_postpreprocess"
            
         
            
            print(values)
            line['objContent'] = values[1]
            
            offset = float(values[0][3])*Op
            pos = [float(values[0][0])*Op,float(values[0][1])*Op,float(values[0][2])*Op,float(values[0][3])*Op]
            offsetPost = [offset*(i+1) for i in range(len(values[1]))]
            pos.append(offsetPost)
            line['objPos'] = pos
           
            line['objType'] = 'text'
            pageInfo["lineList"].append(line)
        
        contIndex = {}
        lineList = pageInfo.get("lineList")
        if lineList:
            for cell in lineList:
                contIndex[cell.get("lineId")] = {
                "lineNo": cell.get("lineNo"),
                "lineId": cell.get("lineId"),
                "objType":cell.get("objType"),
                "objContent": cell.get("objContent"),
                "objPos":  cell.get("objPos"),
                "sortNo": cell.get("lineNo"),
                "rowNo": cell.get("lineNo"),
                "objType_postpreprocess": "table_postpreprocess"
                
                }
        pageInfo["contIndex"] = contIndex
        pageList.append(pageInfo)
        return pageList
        
    # ofd2json流程
    def parserodf2json(self):
        unzip_path = self.unzip_file(self.zip_path)
        cell_list = self.parse_ofd(unzip_path)
        dict = self.odf2json(cell_list)
        shutil.rmtree(unzip_path)
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        return dict

if __name__ == "__main__":
    import time
    import json
    import base64
    f = open("增值税电子专票5.ofd","rb")
    ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    f.close
    t = time.time()
    # 传入b64 字符串
    data_dict = OfdParser(ofdb64).parserodf2json()
    
    print(data_dict)
    print(f"ofd解析耗时{(time.time()-t)*1000}/ms")	
    json.dump(data_dict,open("data_dict.json","w",encoding="utf-8"),ensure_ascii=False,indent=4)
    
