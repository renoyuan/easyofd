#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: F:\code\easyofd\easyofd\draw
#CREATE_TIME: 2023-10-30 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  ofd 基础结构模板
import tempfile
import os
import abc
import copy

import xmltodict
import zipfile

__all__ = ["OFDTemplate","DocumentTemplate","DocumentResTemplate","PulicResTemplate","ContentTemplate","OFDStructure"]
class TemplateBase(object):
    """模板基类"""
    key_map = {}
    def __init__(self,*args,**kwargs):
        self.assemble(*args,**kwargs)
        
  
    def assemble(self,*args,**kwargs):
        """对ofdjson组装"""
        self.final_json = copy.deepcopy(self.ofdjson)

        if kwargs:
            for k,v in kwargs.items():
                if k in self.key_map :
                    self.modify(self.final_json,self.key_map[k],v)
                    
    def modify(self,ofdjson,key,value):
        """对指定key的值更改 多个会统一改"""
        
        for k,v in ofdjson.items():
            if k == key:
                ofdjson[k] = value
            elif isinstance(v,dict):
                self.modify(v,key,value)
            elif isinstance(v,list):
                for v_cell in v:
                    if isinstance(v_cell,dict):
                        self.modify(v_cell,key,value)
    
    def save(self,path):
        xml_data = xmltodict.unparse(self.final_json, pretty=True)
        with open(path,"w",encoding="utf-8") as f:
            f.write(xml_data)

class OFDTemplate(TemplateBase):
    """根节点全局唯一"""
    ofdjson = {
        "ofd:OFD": {
            "@xmlns:ofd": "http://blog.yuanhaiying.cn/",
            "@Version": "1.1",
            "@DocType": "OFD",
            "ofd:DocBody": [{
                "ofd:DocInfo": {
                    "ofd:DocID": "0C1D4F7159954EEEDE517F7285E84DC4",
                    "ofd:Creator": "easyofd",
                    "ofd:author": "renoyuan",
                    "ofd:authoremail": "renoyuan@foxmail.com",
                    "ofd:CreatorVersion": "1.0",
                    "ofd:CreationDate": "2023-10-27"
                },
                "ofd:DocRoot": "Doc_0/Document.xml"
            }]
        }
    }

        
class DocumentTemplate(TemplateBase):
    """DOC 内唯一 表示DOC内部结构"""
    key_map = {"Page":"ofd:Page"}
    
    ofdjson ={
    "ofd:Document": {
        "@xmlns:ofd": "http://blog.yuanhaiying.cn/",
        "ofd:CommonData": {
            "ofd:MaxUnitID": "106",
            "ofd:PageArea": {
                "ofd:PhysicalBox": "0 0 215.89999 279.39999"
            },
            "ofd:PublicRes": "PublicRes.xml",
            "ofd:DocumentRes": "DocumentRes.xml"
        },
        "ofd:Pages": {
            "ofd:Page": {
                "@ID": "1",
                "@BaseLoc": "Pages/Page_0/Content.xml"
            }
        }
    }
}
    


class DocumentResTemplate(TemplateBase):
    """DOC 内唯一 表示MultyMedia 资源信息 如 图片 """
    key_map = {"MultiMedia":"ofd:MultiMedia"}
    ofdjson ={
    "ofd:Res": {
        "@xmlns:ofd": "http://blog.yuanhaiying.cn/",
        "@BaseLoc": "Res",
        "ofd:MultiMedias": {
            "ofd:MultiMedia": [
                {
                    "@ID": "104",
                    "@Type": "Image",
                    "ofd:MediaFile": "Image_2.jpg"
                }
            ]
        }
    }
}   


class PulicResTemplate(TemplateBase):
    """DOC 内唯一 公共配置资源信息 如 Font  Color 等"""
    key_map = {"Font":"ofd:Font"}
    
    ofdjson = {
    "ofd:Res": {
        "@xmlns:ofd": "http://blog.yuanhaiying.cn/",
        "@BaseLoc": "Res",
        "ofd:ColorSpaces": {
            "ofd:ColorSpace": {
                "@ID": "4",
                "@Type": "RGB"
            }
        },
        "ofd:Fonts": {
            "ofd:Font": [

                {
                    "@ID": "69",
                    "@FontName": "STSong",
                    "@FamilyName": "SimSun",
                    "@Serif": "true",
                    "@FixedWidth": "true",
                    "@Charset": "prc"
                }
            ]
        }
    }
}


                    
        
class ContentTemplate(TemplateBase):
    """正文部分"""
    key_map = {"ImageObject":"ofd:ImageObject",
               "PathObject":"ofd:PathObject",
               "TextObject":"ofd:TextObject",
               "CGTransform":"ofd:CGTransform",
               "PhysicalBox":"ofd:PhysicalBox",
               }
    ofdjson = {
    "ofd:Page": {
        "@xmlns:ofd": "http://blog.yuanhaiying.cn/",
        "ofd:Area": {
            "ofd:PhysicalBox": "0 0 211.62 141.08"
        },
        "ofd:Content": {
            "ofd:Layer":  {
                "@ID": "2",
                "@Type": "Body",
                "ofd:PathObject": [          {
                        "@ID": "3",
                        "@CTM": "0.3527 0 0 -0.3527 0.35 141.43001",
                        "@Boundary": "-0.35 -0.35 212.33 141.78999",
                        "@LineWidth": "1",
                        "@MiterLimit": "10",
                        "@Stroke": "false",
                        "@Fill": "true",
                        "ofd:FillColor": {
                            "@ColorSpace": "4",
                            "@Value": "255 255 255"
                        },
                        "ofd:StrokeColor": {
                            "@ColorSpace": "4",
                            "@Value": "0 0 0"
                        },
                        "ofd:Clips": {
                            "ofd:Clip": {
                                "ofd:Area": {
                                    "ofd:Path": {
                                        "@ID": "5",
                                        "@Boundary": "0.00766 -0.00763 600 400.00003",
                                        "@Stroke": "false",
                                        "@Fill": "true",
                                        "ofd:AbbreviatedData": "M 0 0 L 600 0 L 600 400.00003 L 0 400.00003 C"
                                    }
                                }
                            }
                        },
                        "ofd:AbbreviatedData": "M -1 401 L 601 401 L 601 -1 L -1 -1 C"
                    },],
                "ofd:TextObject": [         {
                        "@ID": "1",
                        "@CTM": "7.054 0 0 7.054 0 134.026",
                        "@Boundary": "69 7 72 7.6749",
                        "@Font": "69",
                        "@Size": "6.7028",
                        "ofd:FillColor": {
                            "@ColorSpace": "4",
                            "@Value": "156 82 35"
                        },
                        "ofd:CGTransform": {
                            "@CodePosition": "0",
                            "@CodeCount": "10",
                            "@GlyphCount": "10",
                            "ofd:Glyphs": "18 10 11 42 60 53 24 11 42 61"
                        },
                        "ofd:TextCode": {
                            "@X": "13.925",
                            "@Y": "10",
                            "@DeltaX": "7 7 7 7 7 7 7 7 7",
                            "#text": "电⼦发票（普通发票）"
                        }
                    }],
                "ofd:ImageObject": [{
                        "@ID": "3",
                        "@CTM": "19.7512 0 0 19.7512 0 0",
                        "@Boundary": "7.23035 7.40671 19.7512 19.7512",
                        "@ResourceID": "104"
                    }],
                }            
        }}}

                    
                    
class OFDStructure(object):
    """OFD structure"""
    def __init__(self,name,ofd=OFDTemplate(),document=DocumentTemplate(),document_res=DocumentResTemplate(),pulic_res=PulicResTemplate(),content_res:list=[ContentTemplate()],res_static:dict={}):
       self.name = name
       self.ofd = ofd
       self.document = document
       self.document_res = document_res
       self.pulic_res = pulic_res
       self.content_res = content_res
       self.res_static = res_static
       
    def __call__(self,):
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建过程目录
            temp_dir_doc_0 = os.path.join(temp_dir, 'Doc_0')
            temp_dir_pages = os.path.join(temp_dir, 'Doc_0',"Pages")
            temp_dir_res = os.path.join(temp_dir, 'Doc_0',"Res")
            for i in [temp_dir_doc_0,temp_dir_pages,temp_dir_res]:
                # print(i)
                os.mkdir(i)

            # 写入 OFD
            self.ofd.save(os.path.join(temp_dir, 'OFD.xml'))
            
            # 写入 Document
            self.document.save(os.path.join(temp_dir_doc_0, 'Document.xml'))
            
            # 写入 DocumentRes
            self.document_res.save(os.path.join(temp_dir_doc_0, 'DocumentRes.xml'))
            
            # 写入 PublicRes
            self.pulic_res.save(os.path.join(temp_dir_doc_0, 'PublicRes.xml'))
            
            # 写入 content_res
            for idx,page in enumerate(self.content_res):
                temp_dir_pages_idx = os.path.join(temp_dir_pages, f"Page_{idx}")
                os.mkdir(temp_dir_pages_idx)
                # os.mkdir(i)
                page.save( os.path.join(temp_dir_pages_idx, 'Content.xml'))
                
            # 写入静态资源
            for k,v in self.res_static.items():
                  with open(os.path.join(temp_dir_res,k),"wb") as f:
                      f.write(v)
                      
            # 打包成ofd
            zip = zipfile.ZipFile("test.ofd", "w", zipfile.ZIP_DEFLATED)
            for path, dirnames, filenames in os.walk(temp_dir):
                # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
                fpath = path.replace(temp_dir, '')
        
                for filename in filenames:
                    zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
            zip.close()
            with open("test.ofd","rb") as f:
                content = f.read()
            if os.path.exists("test.ofd"):
               os.remove("test.ofd") 
            return content


if  __name__ == "__main__":
    
    
    font = [
                {
                    "@ID": "69",
                    "@FontName": "STSong",
                    "@FamilyName": "SimSun",
                    "@Serif": "true",
                    "@FixedWidth": "true",
                    "@Charset": "prc"
                }
            ]
    
    MultiMedia = [
                {
                    "@ID": "55",
                    "@Type": "Image",
                    "ofd:MediaFile": "Image_0.jpg"
                }
            ]
            
    pulic_res=PulicResTemplate(Font=font)
    document_res=DocumentResTemplate(MultiMedia=MultiMedia)
    ImageObject = [{
                        "@ID": "55",
                        "@CTM": "200 0 0 140 0 0",
                        "@Boundary": "0 0 200 140",
                        "@ResourceID": "55"
                    }]
    content_res = ContentTemplate(ImageObject=ImageObject,CGTransform=[],PathObject=[],TextObject=[])
    path  = r"F:\code\easyofd\easyofd\draw\Image_0.jpg"
    f = open(path, "rb")
    content = f.read()
    f.close()
    res_static = {"Image_0.jpg":content}
    ofd_byte = OFDStructure("123",pulic_res=pulic_res,document_res=document_res,content_res=[content_res],res_static=res_static)()
    with open("test.ofd","wb") as f:
        content = f.write(ofd_byte)
                