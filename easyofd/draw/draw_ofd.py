#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: F:\code\easyofd\easyofd\draw
# CREATE_TIME: 2023-10-26
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# note:  写入 xml 目录并打包成ofd 文件
from datetime import datetime
from io import BytesIO
from typing import Optional

from PIL import Image
from loguru import logger

from .ofdtemplate import CurId, OFDTemplate, DocumentTemplate, DocumentResTemplate, PublicResTemplate, ContentTemplate, \
    OFDStructure
from .pdf_parse import DPFParser


class OFDWrite(object):
    """
    写入ofd 工具类
    """

    def __init__(self, ):
        self.OP = 200 / 25.4
        # self.OP = 1

    def build_ofd_entrance(self, id_obj: Optional[CurId] = None):
        """
        build_ofd_entrance
        """
        CreationDate = str(datetime.now())
        ofd_entrance = OFDTemplate(CreationDate=CreationDate, id_obj=id_obj)
        return ofd_entrance

    def build_document(self, img_len, id_obj: Optional[CurId] = None, PhysicalBox: Optional[str] = "0 0 140 90"):
        """
        build_document
        """
        pages = []

        for idx in range(img_len):
            pages.append(
                {
                    "@ID": f"{idx + 1}",
                    "@BaseLoc": f"Pages/Page_{idx}/Content.xml"
                }
            )
        document = DocumentTemplate(Page=pages, id_obj=id_obj, PhysicalBox=PhysicalBox)
        return document

    def build_document_res(self, img_len: int = 0, id_obj: Optional[CurId] = None,
                           pfd_res_uuid_map: Optional[dict] = None):
        """
        build_document_res
        """
        MultiMedia = []
        DrawParams = []  # todo DrawParams 参数后面有空增加
        if img_len and not pfd_res_uuid_map:
            for num in range(img_len):
                MultiMedia.append({
                    "@ID": 0,
                    "@Type": "Image",
                    "ofd:MediaFile": f"Image_{num}.jpg",
                    "res_uuid": f"{num}",
                })
        elif pfd_res_uuid_map and (pfd_img := pfd_res_uuid_map.get("img")):
            for res_uuid in pfd_img.keys():
                name = f"Image_{res_uuid}.jpg"
                MultiMedia.append({
                    "@ID": 0,
                    "@Type": "Image",
                    "ofd:MediaFile": name,
                    "res_uuid": res_uuid,

                })

        document_res = DocumentResTemplate(MultiMedia=MultiMedia, id_obj=id_obj)
        return document_res

    def build_public_res(self, id_obj: CurId = None, pfd_res_uuid_map: dict = None):
        """
        build_public_res
        """
        fonts = []
        if pfd_res_uuid_map and (pfd_font := pfd_res_uuid_map.get("font")):
            for res_uuid, font in pfd_font.items():
                fonts.append({
                    "@ID": 0,
                    "@FontName": font,
                    "@FamilyName": font,  # 匹配替代字型
                    "res_uuid": res_uuid,
                    "@FixedWidth": "false",
                    "@Serif": "false",
                    "@Bold": "false",
                    "@Charset": "prc"
                })
        else:
            pass

        public_res = PublicResTemplate(Font=fonts, id_obj=id_obj)
        return public_res

    def build_content_res(self, pil_img_list=None, pdf_info_list=None, id_obj: CurId = None,
                          pfd_res_uuid_map: dict = None):
        """
        pil_img_list - >一张图片是一页
        content_res -> 写入 pdf 信息
        """
        PhysicalBox = None
        content_res_list = []
        if pil_img_list:
            for idx, pil_img in enumerate(pil_img_list):
                # print(pil_img)
                # print(idx, pil_img[1], pil_img[2])
                PhysicalBox = f"0 0 {pil_img[1]} {pil_img[2]}"
                ImageObject = [{
                    "@ID": 0,
                    "@CTM": f"{pil_img[1]} 0 0 {pil_img[2]} 0 0",
                    "@Boundary": f"0 0 {pil_img[1]} {pil_img[2]}",
                    "res_uuid": f"{idx}",  # 资源标识
                    "@ResourceID": f""
                }]

                conten = ContentTemplate(PhysicalBox=PhysicalBox, ImageObject=ImageObject,

                                         CGTransform=[], PathObject=[], TextObject=[], id_obj=id_obj)
                # print(conten)
                content_res_list.append(conten)
        elif pdf_info_list:  # 写入读取后的pdf 结果 # todo 图片id 需要关联得提前定义或者有其他方式反向对齐

            for idx, content in enumerate(pdf_info_list):
                ImageObject = []
                TextObject = []
                PhysicalBox = pfd_res_uuid_map["other"]["page_size"][idx]
                PhysicalBox = f"0 0 {PhysicalBox[0]} {PhysicalBox[1]}"  # page_size 没有的话使用document 里面的
                for block in content:
                    # print(block)

                    bbox = block['bbox']
                    x0, y0, length, height = bbox[0] / self.OP, bbox[1] / self.OP, (bbox[2] - bbox[0]) / self.OP, (
                            bbox[3] - bbox[1]) / self.OP
                    if block["type"] == "text":

                        count = len(block.get("text"))

                        TextObject.append({
                            "@ID": 0,
                            "res_uuid": block.get("res_uuid"),  # 资源标识
                            "@Font": "",
                            "ofd:FillColor": {"Value": "156 82 35"},

                            "ofd:TextCode": {
                                "#text": block.get("text"),
                                "@X": "0",
                                "@Y": f"{block.get('size') / self.OP}",
                                "@DeltaX": f"g {count - 1} {length / count}"
                            },

                            "@size": block.get("size") / self.OP,
                            "@Boundary": f"{x0} {y0} {length} {height}",

                        })
                    elif block["type"] == "img":
                        ImageObject.append({
                            "@ID": 0,
                            "res_uuid": block.get("res_uuid"),  # 资源标识

                            "@Boundary": f"{x0} {y0} {length} {height}",
                            "@ResourceID": f""  # 需要关联public res 里面的结果

                        })

                # for i in content:
                #     if i["type"] == "img":
                #         ImageObject.append(i)
                #     elif i["type"] == "text":
                #         TextObject.append(i)

                conten = ContentTemplate(PhysicalBox=PhysicalBox, ImageObject=ImageObject,

                                         CGTransform=[], PathObject=[], TextObject=TextObject, id_obj=id_obj)
                # print(conten)
                content_res_list.append(conten)
        else:
            pass
        return content_res_list

    def pil_2_bytes(self, image):
        """"""
        # 创建一个 BytesIO 对象
        img_bytesio = BytesIO()

        # 将图像保存到 BytesIO 对象
        image.save(img_bytesio, format='PNG')  # 你可以根据需要选择其他图像格式

        # 获取 BytesIO 对象中的字节
        img_bytes = img_bytesio.getvalue()

        # 关闭 BytesIO 对象
        img_bytesio.close()
        return img_bytes

    def __call__(self, pdf_bytes=None, pil_img_list=None, optional_text=False):
        """
        input pdf | imgs if pdf  >optional_text or not
        0 解析pdf文件
        1 构建必要的ofd template
        2 转化为 ofd
        """
        pdf_obj = DPFParser()
        page_pil_img_list = None

        # 插入图片ofd
        if pil_img_list:  # 读取 图片
            page_pil_img_list = [(self.pil_2_bytes(_img), _img.size[0] / self.OP, _img.size[1] / self.OP) for _img in
                                 pil_img_list]
        else:  # 读取 pdf 转图片
            if optional_text:  # 生成可编辑ofd:
                pdf_info_list, pfd_res_uuid_map = pdf_obj.extract_text_with_details(pdf_bytes)  # 解析pdf
                logger.debug(f"pdf_info_list: {pdf_info_list} \n pfd_res_uuid_map {pfd_res_uuid_map}")
            else:
                img_list = pdf_obj.to_img(pdf_bytes)
                page_pil_img_list = [(self.pil_2_bytes(Image.frombytes("RGB", [_img.width, _img.height],
                                                                       _img.samples)), _img.width / self.OP,
                                      _img.height / self.OP) for _img in img_list]

        id_obj = CurId()

        if page_pil_img_list:  # img 内容转ofd
            res_static = {}  # 图片资源
            pfd_res_uuid_map = {"img": {}}
            PhysicalBox = f"0 0 {page_pil_img_list[0][1]} {page_pil_img_list[0][2]}"
            for idx, pil_img_tuple in enumerate(page_pil_img_list):
                pfd_res_uuid_map["img"][f"{idx}"] = pil_img_tuple[0]
                res_static[f"Image_{idx}.jpg"] = pil_img_tuple[0]
            ofd_entrance = self.build_ofd_entrance(id_obj=id_obj)
            document = self.build_document(len(page_pil_img_list), id_obj=id_obj, PhysicalBox=PhysicalBox)
            public_res = self.build_public_res(id_obj=id_obj)
            document_res = self.build_document_res(len(page_pil_img_list), id_obj=id_obj,
                                                   pfd_res_uuid_map=pfd_res_uuid_map)

            content_res_list = self.build_content_res(page_pil_img_list, id_obj=id_obj,
                                                      pfd_res_uuid_map=pfd_res_uuid_map)


        else:
            #  生成的文档结构对象需要传入id实例
            ofd_entrance = self.build_ofd_entrance(id_obj=id_obj)
            document = self.build_document(len(pdf_info_list), id_obj=id_obj)
            public_res = self.build_public_res(id_obj=id_obj, pfd_res_uuid_map=pfd_res_uuid_map)
            document_res = self.build_document_res(len(pdf_info_list), id_obj=id_obj, pfd_res_uuid_map=pfd_res_uuid_map)
            content_res_list = self.build_content_res(pdf_info_list=pdf_info_list, id_obj=id_obj,
                                                      pfd_res_uuid_map=pfd_res_uuid_map)

            res_static = {}  # 图片资源

            print("pfd_res_uuid_map", pfd_res_uuid_map)
            img_dict = pfd_res_uuid_map.get("img")
            if img_dict:
                for key, v_io in img_dict.items():
                    res_static[f"Image_{key}.jpg"] = v_io.getvalue()

        # 生成 ofd 文件
        ofd_byte = OFDStructure("123", ofd=ofd_entrance, document=document, public_res=public_res,
                                document_res=document_res, content_res=content_res_list, res_static=res_static)(
            test=True)
        return ofd_byte


if __name__ == "__main__":
    pdf_p = r"D:\renodoc\技术栈\GBT_33190-2016_电子文件存储与交换格式版式文档.pdf"
    pdf_p = r"F:\code\easyofd\test"
    with open(pdf_p, "rb") as f:
        content = f.read()

    ofd_content = OFDWrite()(content)

    with open("ofd.ofd", "wb") as f:
        f.write(ofd_content)
