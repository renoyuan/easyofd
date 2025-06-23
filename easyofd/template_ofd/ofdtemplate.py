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

from loguru import logger
import xmltodict
import zipfile

__all__ = ["CurId", "OFDTemplate", "DocumentTemplate", "DocumentResTemplate",
           "PublicResTemplate", "ContentTemplate", "OFDStructure"]
"""
OFD目录结构
    │  OFD.xml
    │  
    └─Doc_0
        │  Document.xml
        │  DocumentRes.xml
        │  PublicRes.xml
        │  
        ├─Annots
        │  │  Annotations.xml
        │  │  
        │  └─Page_0
        │          Annotation.xml
        │          
        ├─Attachs
        │      Attachments.xml
        │      original_invoice.xml
        │      
        ├─Pages
        │  └─Page_0
        │          Content.xml
        │          
        ├─Res
        │      image_80.jb2
        │      
        ├─Signs
        │  │  Signatures.xml
        │  │  
        │  └─Sign_0
        │          Signature.xml
        │          SignedValue.dat
        │          
        ├─Tags
        │      CustomTag.xml
        │      CustomTags.xml
        │      
        └─Tpls
            └─Tpl_0
                    Content.xml
"""
class CurId(object):
    """文档内id控制对象"""
    def __init__(self):
        self.id = 1
        self.used = False
        self.uuid_map = {} # 资源文件生成id的时候手动添加进来后面构建page 可以 匹配ResourceID

    def add_uuid_map(self, k, v):
        logger.debug(f"uuid_map add {k}: {v}")
        self.uuid_map[k] = v
    def add(self):
        self.id += 1

    def get_id(self):
        if self.used:
            self.add()
            return self.id
        if not self.used:
            cur_id = self.id
            self.used =True
            return cur_id

    def get_max_id(self):
        MaxUnitID = self.id + 1
        return MaxUnitID

class TemplateBase(object):
    """模板基类"""
    key_map = {}  # 变量名对应 xml 中形式 映射 如 传入   DocID -> ofd:DocID
    id_keys = [ ]  # 对需要的要素添加 "@ID"
    template_name = ""
    def __init__(self,*args,**kwargs):
        # print(args)
        # print(kwargs)
        self.id_obj: CurId = kwargs.get("id_obj")
        # print("id_obj", self.id_obj)
        self.assemble(*args, **kwargs)


    def assemble(self,*args, **kwargs):
        """对ofdjson组装"""

        self.final_json = copy.deepcopy(self.ofdjson)

        # 往模板里面添加要素值
        if kwargs:
            for k, v in kwargs.items():
                if k in self.key_map:
                    self.modify(self.final_json, self.key_map[k], v)

        # 添加id
        for id_key in self.id_keys:
            print(f"开始gen_id >> {self.template_name}>>{id_key}")
            # print(f"final_json {self.final_json}")
            self.gen_id(self.final_json, id_key)

    def gen_id(self,ofdjson, id_key):
        """生成id"""
        # print("id_key ", id_key, "ofdjson ", ofdjson)

        for k, v in ofdjson.items():
            if k == id_key:
                # 添加id
                if isinstance(ofdjson[k], dict):
                    ofdjson[k]["@ID"] = f"{self.id_obj.get_id()}"

                    # logger.info(f"添加id -> {ofdjson[k]}")
                elif isinstance(ofdjson[k], list):
                    for i in ofdjson[k]:
                        i["@ID"] = f"{self.id_obj.get_id()}"

                        # logger.info(f"添加id ->i {i}")

            elif isinstance(v, dict):
                # logger.debug(f"dict_v{v}")
                self.gen_id(v, id_key)


            elif isinstance(v, list):
                for v_cell in v:
                    if isinstance(v_cell, dict):
                        # logger.debug(f"dict_v{v}")
                        self.gen_id(v_cell, id_key)

                    
    def modify(self, ofdjson, key, value):
        """对指定key的值更改  多个会统一改"""
        
        for k, v in ofdjson.items():
            if k == key:
                ofdjson[k] = value
            elif isinstance(v, dict):
                self.modify(v, key, value)
            elif isinstance(v, list):
                for v_cell in v:
                    if isinstance(v_cell, dict):
                        self.modify(v_cell, key, value)
    
    def save(self, path):
        xml_data = xmltodict.unparse(self.final_json, pretty=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml_data)

class OFDTemplate(TemplateBase):
    """根节点全局唯一 OFD.xml"""
    template_name = "OFD"
    key_map = {"Author": "ofd:Author", "DocID": "ofd:DocID"  ,"CreationDate": "ofd:CreationDate"
    }

    ofdjson = {

        "ofd:OFD": {
            "@xmlns:ofd": "http://blog.yuanhaiying.cn",
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
    """DOC 内唯一 表示DOC内部结构 Document.xml

    """
    template_name = "Document"
    key_map = {"Page": "ofd:Page","PhysicalBox":"ofd:PhysicalBox"}
    id_keys = ["ofd:Page"]
    ofdjson ={
    "ofd:Document": {
        "@xmlns:ofd": "http://blog.yuanhaiying.cn",
        "ofd:CommonData": {
            "ofd:MaxUnitID": 0,
            "ofd:PageArea": {
                "ofd:PhysicalBox": "0 0 140 90"
            },
            "ofd:PublicRes": "PublicRes.xml",
            "ofd:DocumentRes": "DocumentRes.xml"
        },
        "ofd:Pages":
            {
            "ofd:Page": [{
                "@ID": 0,
                "@BaseLoc": "Pages/Page_0/Content.xml"
            }]
        }
    }
}

    def update_max_unit_id(self, final_json=None):
        if not final_json:
            final_json = self.final_json

        for k, v in final_json.items():
            if k == "ofd:MaxUnitID":
                final_json["ofd:MaxUnitID"]=self.id_obj.get_max_id()
                return

            elif isinstance(v, dict):
                self.update_max_unit_id(v)
            elif isinstance(v, list):
                for v_cell in v:
                    if isinstance(v_cell, dict):
                        self.update_max_unit_id(v_cell)

    def update_page(self,page_num):
        pass

class DocumentResTemplate(TemplateBase):
    """DOC 内唯一 表示MultyMedia 资源信息 如 图片 DocumentRes.xml """
    template_name = "DocumentRes"
    key_map = {"MultiMedia": "ofd:MultiMedia"}
    id_keys = ["ofd:DrawParam", "ofd:MultiMedia"]
    ofdjson = {
        "ofd:Res": {
            "@xmlns:ofd": "http://blog.yuanhaiying.cn",
            "@BaseLoc": "Res",
            "ofd:MultiMedias": {
                "ofd:MultiMedia": [
                    {
                        "@ID": 0,
                        "@Type": "Image",
                        "ofd:MediaFile": "Image_2.jpg"
                    }
                ]
            }
        }
    }
    def gen_id(self,ofdjson, id_key):
        """生成id"""
        # print("id_key ", id_key, "ofdjson ", ofdjson)

        for k, v in ofdjson.items():
            if k == id_key:
                # 添加id
                if isinstance(ofdjson[k], dict):
                    ofdjson[k]["@ID"] = f"{self.id_obj.get_id()}"
                    if res_uuid := ofdjson[k].get("res_uuid"):
                        self.id_obj.add_uuid_map(res_uuid, ofdjson[k]["@ID"])
                    # logger.info(f"添加id -> {ofdjson[k]}")
                elif isinstance(ofdjson[k], list):
                    for i in ofdjson[k]:

                        i["@ID"] = f"{self.id_obj.get_id()}"
                        if res_uuid := i.get("res_uuid"):
                            self.id_obj.add_uuid_map(res_uuid, i["@ID"])
                        # logger.info(f"添加id ->i {i}")

            elif isinstance(v, dict):
                # logger.debug(f"dict_v{v}")
                self.gen_id(v, id_key)


            elif isinstance(v, list):
                for v_cell in v:
                    if isinstance(v_cell, dict):
                        # logger.debug(f"dict_v{v}")
                        self.gen_id(v_cell, id_key)

class PublicResTemplate(TemplateBase):
    """DOC 内唯一 公共配置资源信息 如 Font  Color 等 PublicRes.xml"""
    template_name = "PulicRes"
    key_map = {"Font": "ofd:Font"}
    id_keys = ["ofd:ColorSpace", "ofd:Font"]
    ofdjson = {
        "ofd:Res": {
            "@xmlns:ofd": "http://blog.yuanhaiying.cn",
            "@BaseLoc": "Res",
            "ofd:ColorSpaces": {
                "ofd:ColorSpace": {
                    "@ID": 0,
                    "@Type": "RGB",
                    "@BitsPerComponent": "8",
                    "#text":""
                }
            },
            "ofd:Fonts": {
                "ofd:Font": [
                {
                    "@ID": 0,
                    "@FontName": "宋体",
                    "@FamilyName": "宋体",

                }
            ]
            }
        }
    }
    def gen_id(self,ofdjson, id_key):
        """生成id"""
        # print("id_key ", id_key, "ofdjson ", ofdjson)

        for k, v in ofdjson.items():
            if k == id_key:
                # 添加id
                if isinstance(ofdjson[k], dict):
                    ofdjson[k]["@ID"] = f"{self.id_obj.get_id()}"
                    if res_uuid := ofdjson[k].get("res_uuid"):
                        self.id_obj.add_uuid_map(res_uuid, ofdjson[k]["@ID"])
                    # logger.info(f"添加id -> {ofdjson[k]}")
                elif isinstance(ofdjson[k], list):
                    for i in ofdjson[k]:

                        i["@ID"] = f"{self.id_obj.get_id()}"
                        if res_uuid := i.get("res_uuid"):
                            self.id_obj.add_uuid_map(res_uuid, i["@ID"])
                        # logger.info(f"添加id ->i {i}")

            elif isinstance(v, dict):
                # logger.debug(f"dict_v{v}")
                self.gen_id(v, id_key)


            elif isinstance(v, list):
                for v_cell in v:
                    if isinstance(v_cell, dict):
                        # logger.debug(f"dict_v{v}")
                        self.gen_id(v_cell, id_key)

'''
    "ofd:Font": [

    {
        "@ID": 0,
        "@FontName": "STSong",
        "@FamilyName": "SimSun",
        "@Serif": "true",
        "@FixedWidth": "true",
        "@Charset": "prc"
    }
            "ofd:Area": {
            "ofd:PhysicalBox": "0 0 210 140"
        },
'''


class ContentTemplate(TemplateBase):
    """正文部分 Content.xml"""
    #"@Type": "Body",
    template_name = "Content"
    key_map = {"ImageObject": "ofd:ImageObject",
               "PathObject": "ofd:PathObject",
               "TextObject": "ofd:TextObject",
               "CGTransform": "ofd:CGTransform",
               "PhysicalBox": "ofd:PhysicalBox",
               }
    id_keys = ["ofd:Layer", "ofd:TextObject", "ofd:PathObject", "ofd:Clips", "ofd:ImageObject"]
    correlate_map = {"ofd:TextObject": "@Font",
                     "ofd:ImageObject": "@ResourceID"

                     }

    ofdjson = {
    "ofd:Page": {
        "@xmlns:ofd": "http://blog.yuanhaiying.cn",

        "ofd:Content": {
            "ofd:PageArea": {
                "ofd:PhysicalBox": "0 0 210 140"
            },
            "ofd:Layer":  {
                "@ID": 0,
                "@Type": "Foreground",


                "ofd:TextObject": [{
                        "@ID": 0,
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
                "ofd:ImageObject": []
                }
        }}}
    def __init__(self,*args,**kwargs):
        # print(args)
        # print(kwargs)
        super().__init__(*args, **kwargs)
        # 关联res_uuid
        for key, targe_key in self.correlate_map.items():
            self.correlate_res_uuid(self.final_json,key,targe_key)

    def correlate_res_uuid(self, ofdjson,key,targe_key):
        """correlate_res_uuid"""
        print("========uuid_map", self.id_obj.uuid_map)
        for k, v in ofdjson.items():
            if k == key:
                if isinstance(v, dict) and (res_uuid := v_cell.pop("res_uuid", None)):

                    v[targe_key] = self.id_obj.uuid_map[res_uuid]
                    logger.debug(f'{targe_key} >>> {v[targe_key]} -- {res_uuid}')
                elif isinstance(v, list):
                    for v_cell in v:
                        if isinstance(v_cell, dict) and (res_uuid := v_cell.pop("res_uuid", None)):

                            v_cell[targe_key] = self.id_obj.uuid_map[res_uuid]
                            logger.debug(f'{targe_key} >>> {v_cell[targe_key]} -- {res_uuid}')
                        else:
                            print(f"v_cell {v_cell}")
                    pass
                else:
                    pass
            elif isinstance(v, dict):
                self.correlate_res_uuid(v, key, targe_key)
            elif isinstance(v, list):
                for v_cell in v:
                    if isinstance(v_cell, dict):
                        self.correlate_res_uuid(v_cell, key, targe_key)


'''
                "ofd:PathObject": [{
                        "@ID": 0,
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
                                        "@ID": 0,
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
                
"ofd:ImageObject": [{
                        "@ID": 0,
                        "@CTM": "19.7512 0 0 19.7512 0 0",
                        "@Boundary": "7.23035 7.40671 19.7512 19.7512",
                        "@ResourceID": "104"
                    }],
'''

class OFDStructure(object):
    """OFD structure"""
    def __init__(self, name, ofd=None, document=None,
                 document_res=None, public_res=None,
                  content_res:list=[], res_static: dict={}):
        # 初始化的时候会先自动初始化 默认参数值
        id_obj = CurId()
        self.name = name
        self.ofd = ofd if ofd else OFDTemplate(id_obj=id_obj)
        self.document = document if document else DocumentTemplate(id_obj=id_obj)
        self.document_res = document_res if document_res else  DocumentResTemplate(id_obj=id_obj)
        self.public_res = public_res if public_res else PublicResTemplate(id_obj=id_obj)
        self.content_res = content_res if content_res else [ContentTemplate(id_obj=id_obj)]
        self.res_static = res_static
       
    def __call__(self, test=False):
        """写入文件生成ofd"""
        with tempfile.TemporaryDirectory() as t_dir:
            if test:
                temp_dir = r"./test"
                os.mkdir(temp_dir)
            else:
                temp_dir = t_dir
            # 创建过程目录
            temp_dir_doc_0 = os.path.join(temp_dir, 'Doc_0')
            temp_dir_pages = os.path.join(temp_dir, 'Doc_0', "Pages")
            temp_dir_res = os.path.join(temp_dir, 'Doc_0', "Res")  # 静态资源路径
            for i in [temp_dir_doc_0, temp_dir_pages, temp_dir_res]:
                # print(i)
                os.mkdir(i)

            # 写入 OFD
            self.ofd.save(os.path.join(temp_dir, 'OFD.xml'))

            # 更新 max_unit_id & 写入 Document
            self.document.update_max_unit_id()
            self.document.save(os.path.join(temp_dir_doc_0, 'Document.xml'))

            # 写入 DocumentRes
            self.document_res.save(os.path.join(temp_dir_doc_0, 'DocumentRes.xml'))

            # 写入 PublicRes
            self.public_res.save(os.path.join(temp_dir_doc_0, 'PublicRes.xml'))

            # 写入 content_res
            for idx, page in enumerate(self.content_res):
                temp_dir_pages_idx = os.path.join(temp_dir_pages, f"Page_{idx}")
                os.mkdir(temp_dir_pages_idx)
                # os.mkdir(i)
                page.save(os.path.join(temp_dir_pages_idx, 'Content.xml'))

            # 写入静态资源
            for k, v in self.res_static.items():
                  with open(os.path.join(temp_dir_res, k), "wb") as f:
                      f.write(v)

            # 打包成ofd
            zip = zipfile.ZipFile("test.ofd", "w", zipfile.ZIP_DEFLATED)
            for path, dirnames, filenames in os.walk(temp_dir):
                # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
                fpath = path.replace(temp_dir, '')

                for filename in filenames:
                    zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
            zip.close()
            with open("test.ofd", "rb") as f:
                content = f.read()
            if os.path.exists("test.ofd"):
               os.remove("test.ofd")
            return content

if  __name__ == "__main__":
    print("---------")
    # 资源文件
    img_path = r"F:\code\easyofd\test\test_img0.jpg"
    # with open(img_path, "rb") as f:
    #     content = f.read()
    content = b""
    res_static = {"Image_0.jpg": content}

    # 构建数据
    font = [
            {

                "@FontName": "宋体",
                "@FamilyName": "宋体",

            }
            ]

    MultiMedia = [
                {

                    "@Type": "Image",
                    "ofd:MediaFile": "Image_0.jpg"
                }
            ]

    ImageObject = [{

                        "@CTM": "200 0 0 140 0 0",
                        "@Boundary": "0 0 200 140",
                        "@ResourceID": "55"
                    }]
    TextObject = [
        {


        "@Boundary": "50 5 100 20",
        "@Font": "2",
        "@Size": "5",
        "ofd:FillColor": {

            "@Value": "156 82 35",
            "@ColorSpace" : "1"
        },

        "ofd:TextCode": {
            "@X": "5",
            "@Y": "5",
            "@DeltaX": "7 7 7 7 7 7 7 7 7",
            "#text": "电⼦发票（普通发票）"
        }
    }, {


        "@Boundary": "0 0 100 100",
        "@Font": "2",
        "@Size": "10",
        "ofd:FillColor": {

            "@Value": "156 82 35"
        },

        "ofd:TextCode": {
            "@X": "0",
            "@Y": "0",
            "@DeltaX": "0",
            "#text": "电"
        }
    }
    ]

    # 实例化模板
    id_obj = CurId()
    print("id_obj实例化", id_obj)

    ofd = OFDTemplate(id_obj=id_obj)
    document = DocumentTemplate(id_obj=id_obj)
    public_res = PublicResTemplate(Font=font, id_obj=id_obj)
    document_res = DocumentResTemplate(MultiMedia=MultiMedia, id_obj=id_obj)
    # ImageObject=ImageObject
    content_res = ContentTemplate(CGTransform=[], PathObject=[], TextObject=TextObject, ImageObject=[], id_obj=id_obj)



    ofd_byte = OFDStructure("123",ofd=ofd, document=document,public_res=public_res,
                            document_res=document_res, content_res=[content_res], res_static=res_static)(test=True)

    with open("test.ofd", "wb") as f:
        content = f.write(ofd_byte)
