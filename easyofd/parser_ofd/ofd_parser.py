#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: D:\code\easyofd\easyofd\parser
# CREATE_TIME: 2023-07-27
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: ofd解析主流程

import os
import sys

from easyofd.parser_ofd.file_ofd_parser import OFDFileParser

sys.path.insert(0, "..")

import traceback
import base64
import re
import io

from typing import Any, List
from PIL import Image
from PIL.Image import Image as ImageClass
from loguru import logger

from .img_deal import DealImg
from .file_deal import FileRead
from .file_ofd_parser import OFDFileParser
from .file_doc_parser import DocumentFileParser
from .file_docres_parser import DocumentResFileParser
from .file_content_parser import ContentFileParser
from .file_annotation_parser import AnnotationFileParser,AnnotationsParser
from .file_publicres_parser import PublicResFileParser
from .file_signature_parser import SignaturesFileParser,SignatureFileParser
from .path_parser import PathParser
# todo 解析流程需要大改


class OFDParser(object):
    """
    OFDParser 解析
    1 解压文件 创建文件映射表 释放文件
    2 解析 xml 逐级去 收集需要信息  结构文本 以及 资源
    2 调用font 注册 字体

    图层顺序 tlp>content>annotation
    """

    def __init__(self, ofdb64):
        self.img_deal = DealImg()
        self.ofdb64 = ofdb64
        self.file_tree = None
        self.jbig2dec_path = r"C:/msys64/mingw64/bin/jbig2dec.exe"

    def img2data(self, imglist: List[ImageClass]):
        """
        imglist to ofd data
        
        """
        OP = 200 / 25.4
        doc_list = []
        img_info = {}
        page_size = []
        font_info = {}
        page_info_d = {}

        for idx, img_pil in enumerate(imglist):
            w, h = img_pil.size
            img_bytes = self.img_deal.pil2bytes(img_pil)
            imgb64 = str(base64.b64encode(img_bytes), encoding="utf-8")
            img_info[str(idx)] = {
                "format": "jpg",
                "wrap_pos": "",
                "type": "IMG",
                "suffix": "jpg",
                "fileName": f"{idx}.jpg",
                "imgb64": imgb64,

            }
            text_list = []
            img_list = []
            img_d = {}
            img_d["CTM"] = ""  # 平移矩阵换 平移 缩放 旋转
            img_d["ID"] = str(idx)  # 图片id
            img_d["ResourceID"] = str(idx)  # 图片id
            img_d["pos"] = [0, 0, w / OP, h / OP]  # 平移矩阵换
            page_size = [0, 0, w / OP, h / OP]
            # print(page_size)
            img_list.append(img_d)

            content_d = {
                "text_list": text_list,
                "img_list": img_list,
            }
            page_info_d[idx] = content_d
        doc_list.append({
            "pdf_name": "demo.pdf",
            "doc_no": "0",
            "images": img_info,
            "page_size": page_size,
            "fonts": font_info,
            "page_info": page_info_d
        })

        return doc_list

    # 获得xml 对象
    def get_xml_obj(self, label):
        assert label
        # print(self.file_tree.keys())
        label =label.lstrip('./')
        for abs_p in self.file_tree:
            # 统一符号，避免win linux 路径冲突

            abs_p_compare = abs_p.replace("\\\\", "-").replace("//", "-").replace("\\", "-").replace("/", "-")
            label_compare = label.replace("\\\\", "-").replace("//", "-").replace("\\", "-").replace("/", "-")
            if label_compare in abs_p_compare:
                # logger.info(f"{label} {abs_p}")
                return self.file_tree[abs_p]
        # logger.info(f"{label} ofd file path is not")
        return ""

    def jb22png(self, img_d: dict):
        """
        jb22png
        没有安装 jbig2dec 无法操作 
        """
        if not os.path.exists(self.jbig2dec_path):
            logger.warning(f"未安装jbig2dec，无法处理jb2文件")
            return

        # todo ib2 转png C:/msys64/mingw64/bin/jbig2dec.exe -o F:\code\easyofd\test\image_80.png F:\code\easyofd\test\image_80.jb2
        fileName = img_d["fileName"]
        new_fileName = img_d['fileName'].replace(".jb2", ".png")
        with open(fileName, "wb") as f:
            f.write(base64.b64decode(img_d["imgb64"]))
        command = "{} -o {} {}"
        res = os.system(command.format(self.jbig2dec_path, new_fileName, fileName))
        if res != 0:
            logger.warning(f"jbig2dec处理失败")
        if os.path.exists(fileName):
            os.remove(fileName)
        if os.path.exists(new_fileName):
            logger.info(f"jbig2dec处理成功{fileName}>>{new_fileName}")
            img_d["fileName"] = new_fileName
            img_d["suffix"] = "png"
            img_d["format"] = "png"
            with open(new_fileName, "rb") as f:
                data = f.read()
                img_d["imgb64"] = str(base64.b64encode(data), encoding="utf-8")

            os.remove(new_fileName)

    def bmp2jpg(self, img_d: dict):

        fileName = img_d["fileName"]
        new_fileName = img_d['fileName'].replace(".bmp", ".jpg")
        b64_nmp = self.get_xml_obj(fileName)
        image_data = base64.b64decode(b64_nmp)
        image = Image.open(io.BytesIO(image_data))
        rgb_image = image.convert("RGB")
        output_buffer = io.BytesIO()
        rgb_image.save(output_buffer, format="JPEG")
        image.close()
        jpeg_bytes = output_buffer.getvalue()
        b64_jpeg = base64.b64encode(jpeg_bytes).decode('utf-8')
        output_buffer.close()

        if b64_jpeg:
            logger.info(f"bmp2jpg处理成功{fileName}>>{new_fileName}")
            img_d["fileName"] = new_fileName
            img_d["suffix"] = "jpg"
            img_d["format"] = "jpg"
            img_d["imgb64"] = b64_jpeg

    def tif2jpg(self, img_d: dict):
        fileName = img_d["fileName"]
        new_fileName = img_d['fileName'].replace(".tif", ".jpg")
        tif_nmp = self.get_xml_obj(fileName)
        image_data = base64.b64decode(tif_nmp)
        image = Image.open(io.BytesIO(image_data))
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            image = image.convert("RGB")

            # 创建一个字节流来保存处理后的图像
        output_buffer = io.BytesIO()

        # 保存图像为 JPEG 格式到字节流中
        image.save(output_buffer, format="JPEG", quality=95)

        # 获取字节流中的内容并编码为 Base64 字符串
        jpeg_bytes = output_buffer.getvalue()
        b64_jpeg = base64.b64encode(jpeg_bytes).decode('utf-8')

        # 关闭图像对象和字节流
        image.close()
        output_buffer.close()

        if b64_jpeg:
            logger.info(f"tif2jpg处理成功{fileName}>>{new_fileName}")
            img_d["fileName"] = new_fileName
            img_d["suffix"] = "jpg"
            img_d["format"] = "jpg"
            img_d["imgb64"] = b64_jpeg

    def gif2jpg(self, img_d: dict):
        fileName = img_d["fileName"]
        new_fileName = img_d['fileName'].replace(".bmp", ".jpg")
        b64_gif = self.get_xml_obj(fileName)
        image_data = base64.b64decode(b64_gif)
        image = Image.open(io.BytesIO(image_data))
        if image.mode != "RGB":
            image = image.convert("RGB")
        output_buffer = io.BytesIO()
        image.save(output_buffer, format="JPEG", quality=95)
        image.close()
        jpeg_bytes = output_buffer.getvalue()
        b64_jpeg = base64.b64encode(jpeg_bytes).decode('utf-8')
        output_buffer.close()

        if b64_jpeg:
            logger.info(f"gif2jpg处理成功{fileName}>>{new_fileName}")
            img_d["fileName"] = new_fileName
            img_d["suffix"] = "jpg"
            img_d["format"] = "jpg"
            img_d["imgb64"] = b64_jpeg

    def parser(self, ):
        """
        解析流程
        doc_0默认只有 一层
        OFD >  Document.xml > [DocumentRes.xml, PublicRes.xml, Signatures.xml Annotations.xml] > []
        """

        page_size_details = []
        default_page_size = []
        doc_list = []
        ofd_xml_obj = self.get_xml_obj(self.file_tree["root_doc"])  # OFD.xml xml 对象 

        if ofd_xml_obj:
            ofd_obj_res = OFDFileParser(ofd_xml_obj)()
            doc_root_name = ofd_obj_res.get("doc_root")
            signatures = ofd_obj_res.get("signatures")
        else:
            # 考虑根节点丢失情况
            doc_root_name = ["Doc_0/Document.xml"]
            signatures = ["Doc_0/Signs/Signatures.xml"]

        doc_root_xml_obj = self.get_xml_obj(doc_root_name[0])
        doc_root_info = DocumentFileParser(doc_root_xml_obj)()
        doc_size = doc_root_info.get("size")

        if doc_size:
            try:
                default_page_size = [float(pos_i) for pos_i in doc_size.split(" ") if re.match("[\d\.]", pos_i)]
            except:
                traceback.print_exc()

        # 字体信息
        font_info = {}
        public_res_name: list = doc_root_info.get("public_res")
        if public_res_name:
            public_xml_obj = self.get_xml_obj(public_res_name[0])
            font_info = PublicResFileParser(public_xml_obj)()

            # 注册字体
            for font_id, font_v in font_info.items():
                file_name = font_v.get("FontFile")
                if file_name:
                    font_b64 = self.get_xml_obj(file_name)
                    if font_b64:
                        font_v["font_b64"] = font_b64

        # 图片资源
        img_info: dict = dict()
        document_res_name: list = doc_root_info.get("document_res")
        if document_res_name:
            document_res_xml_obj = self.get_xml_obj(document_res_name[0])

            img_info = DocumentResFileParser(document_res_xml_obj)()
            # 找到图片b64
            for img_id, img_v in img_info.items():
                img_v["imgb64"] = self.get_xml_obj(img_v.get("fileName"))
                # todo ib2 转png C:/msys64/mingw64/bin/jbig2dec.exe -o F:\code\easyofd\test\image_80.png F:\code\easyofd\test\image_80.jb2
                if img_v["suffix"] == 'jb2':
                    self.jb22png(img_v)
                elif img_v["suffix"] == 'bmp':
                    self.bmp2jpg(img_v)
                elif img_v["suffix"] == 'tif':
                    self.tif2jpg(img_v)
                elif img_v["suffix"] == 'gif':
                    self.gif2jpg(img_v)

        page_id_map: list = doc_root_info.get("page_id_map")
        signatures_page_id = {}

        # 签章信息
        if signatures and (signatures_xml_obj := self.get_xml_obj(signatures[0])):
            logger.debug(f"signatures_xml_obj is {signatures_xml_obj } signatures is {signatures} ")
            signatures_info = SignaturesFileParser(signatures_xml_obj)()
            if signatures_info:  # 获取签章具体信息
                for _, signatures_cell in signatures_info.items():
                    # print(signatures_info)
                    BaseLoc = signatures_cell.get("BaseLoc")
                    signature_xml_obj = self.get_xml_obj(BaseLoc)
                    # print(BaseLoc)
                    prefix = BaseLoc.split("/")[0]
                    signatures_info = SignatureFileParser(signature_xml_obj)(prefix=prefix)
                    # print(signatures_info)
                    logger.debug(f"signatures_info {signatures_info}")
                    PageRef = signatures_info.get("PageRef")
                    Boundary = signatures_info.get("Boundary")
                    SignedValue = signatures_info.get("SignedValue")
                    sing_page_no = page_id_map.get(PageRef)
                    # print("self.file_tree",self.file_tree.keys)
                    # print(page_id_map,PageRef)
                    # print(SignedValue, self.get_xml_obj(SignedValue))
                    # with open("b64.txt","w") as f:
                    #     f.write(self.get_xml_obj(SignedValue))
                    if signatures_page_id.get(sing_page_no):
                        signatures_page_id[sing_page_no].append(
                            {
                                "sing_page_no": sing_page_no,
                                "PageRef": PageRef,
                                "Boundary": Boundary,
                                "SignedValue": self.get_xml_obj(SignedValue),
                            }
                        )
                    else:
                        signatures_page_id[sing_page_no] = [
                            {
                                "sing_page_no": sing_page_no,
                                "PageRef": PageRef,
                                "Boundary": Boundary,
                                "SignedValue": self.get_xml_obj(SignedValue),
                            }
                        ]

        # 注释信息 按照页码信息
        annotation_info = {}
        annotations_name: list = doc_root_info.get("Annotations") #获取到入口文件
        logger.debug(f"annotations_name is {annotations_name}")
        if annotations_name and (annotations_xml_obj:= self.get_xml_obj(annotations_name[0])) : # and False
            # TODO 注释解析
            
            try:
                annotations_info = AnnotationsParser(annotations_xml_obj)()
                if annotations_info:
                    logger.debug(f"annotations_info is {annotations_info}")
                    for page_id, annotations_cell in annotations_info.items():
                        file_loc = annotations_cell.get("FileLoc")
                        anno_page_no = annotations_cell.get("pageNo")
                        if file_loc:
                            annotation_xml_obj = self.get_xml_obj(file_loc)
                            if annotation_xml_obj:
                                # 解析注释文件
                                logger.debug(f"annotation_xml_obj is {annotation_xml_obj}")
                                annotation_page_info = AnnotationFileParser(annotation_xml_obj)()
                                annotation_info[anno_page_no] = annotation_page_info
                logger.debug(f"annotation_info is {annotation_info}")
            except Exception as e:
                logger.error(f"AnnotationFileParser error  {e}")
                
      
            


        # 正文信息 会有多页 情况
        page_name: list = doc_root_info.get("page")

        page_info_d = {}
        if page_name:
            for index, _page in enumerate(page_name):
                page_xml_obj = self.get_xml_obj(_page)
                # 重新获取页面size
                try:
                    page_size = [float(pos_i) for pos_i in
                                     page_xml_obj.get('ofd:Page', {}).get("ofd:Area", {}).get("ofd:PhysicalBox",
                                                                                              "").split(" ")
                                     if re.match("[\d\.]", pos_i)]
                    if page_size and len(page_size) >= 2:
                        page_size_details.append(page_size)
                    else:
                        page_size_details.append([])
                except Exception as e:
                    traceback.print_exc()
                    page_size.append([])
                page_info = ContentFileParser(page_xml_obj)()
                pg_no = re.search(r"\d+", _page)
                if pg_no:
                    pg_no = int(pg_no.group())
                else:
                    pg_no = index
                page_info_d[pg_no] = page_info

        # 模板信息
        tpls_name: list = doc_root_info.get("tpls")
        if tpls_name:
            for index, _tpl in enumerate(tpls_name):
                tpl_xml_obj = self.get_xml_obj(_tpl)
                tpl_info = ContentFileParser(tpl_xml_obj)()
                tpl_no = re.search(r"\d+", _tpl)

                if tpl_no:
                    tpl_no = int(tpl_no.group())
                else:
                    tpl_no = index

                if tpl_no in page_info_d:
                    page_info_d[pg_no]["text_list"].extend(tpl_info["text_list"])
                    page_info_d[pg_no]["text_list"].sort(
                        key=lambda pos_text: (float(pos_text.get("pos")[1]), float(pos_text.get("pos")[0])))
                    page_info_d[pg_no]["img_list"].extend(tpl_info["img_list"])
                    page_info_d[pg_no]["img_list"].sort(
                        key=lambda pos_text: (float(pos_text.get("pos")[1]), float(pos_text.get("pos")[0])))
                    page_info_d[pg_no]["line_list"].extend(tpl_info["line_list"])
                    page_info_d[pg_no]["line_list"].sort(
                        key=lambda pos_text: (float(pos_text.get("pos")[1]), float(pos_text.get("pos")[0])))
                else:
                    page_info_d[tpl_no] = tpl_info
                    page_info_d[tpl_no].sort(
                        key=lambda pos_text: (float(pos_text.get("pos")[1]), float(pos_text.get("pos")[0])))
        docNo = 0  # 没遇到过doc多个的情况 出现再看
        # print("page_info",len(page_info))
        doc_list.append({
            "default_page_size": default_page_size,
            "page_size": page_size_details,
            "pdf_name": self.file_tree["pdf_name"],
            "doc_no": docNo,
            "images": img_info,
            "signatures_page_id": signatures_page_id,
            "annotation_info": annotation_info,
            "page_id_map": page_id_map,
            "fonts": font_info,
            "page_info": page_info_d,
            "page_tpl_info": page_info_d,
            "page_content_info": page_info_d,
            "page_info": page_info_d,
        })
        return doc_list

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        输出ofd解析结果
        """
        save_xml = kwargs.get("save_xml", False)
        xml_name = kwargs.get("xml_name")
        self.file_tree = FileRead(self.ofdb64)(save_xml=save_xml, xml_name=xml_name)
        # logger.info(self.file_tree)
        return self.parser()


if __name__ == "__main__":
    with open(r"E:\code\easyofd\test\增值税电子专票5.ofd", "rb") as f:
        ofdb64 = str(base64.b64encode(f.read()), "utf-8")
    print(OFDParser(ofdb64)())
