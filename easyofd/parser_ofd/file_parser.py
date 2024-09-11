#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: D:\code\easyofd\easyofd\parser
# CREATE_TIME: 2023-07-27
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: 每种类型的文件定义一个解析器

import sys

sys.path.insert(0, "..")
import logging
import os
import traceback
import base64
import re
from typing import Any
from .parameter_parser import ParameterParser
logger = logging.getLogger("root")


class FileParserBase(object):
    """xml解析"""

    def __init__(self, xml_obj):
        assert xml_obj
        self.ofd_param = ParameterParser()
        self.xml_obj = xml_obj
        # print(xml_obj)

    def recursion_ext(self, need_ext_obj, ext_list, key):
        """
        抽取需要xml要素
        need_ext_obj : xmltree
        ext_list: data container
        key: key
        """

        if isinstance(need_ext_obj, dict):

            for k, v in need_ext_obj.items():
                if k == key:

                    if isinstance(v, (dict, str)):
                        ext_list.append(v)
                    elif isinstance(v, list):
                        ext_list.extend(v)


                else:

                    if isinstance(v, dict):
                        self.recursion_ext(v, ext_list, key)
                    elif isinstance(v, list):
                        for cell in v:
                            self.recursion_ext(cell, ext_list, key)
                    else:

                        pass
        else:

            print(type(need_ext_obj))


class OFDFileParser(FileParserBase):
    def __call__(self):
        info = {}
        # DocRoot 
        doc_root: list = []
        doc_root_key = "ofd:DocRoot"
        # print(self.xml_obj,doc_root)
        self.recursion_ext(self.xml_obj, doc_root, doc_root_key)
        info["doc_root"] = doc_root

        signatures: list = []
        signatures_key = "ofd:Signatures"
        self.recursion_ext(self.xml_obj, signatures, signatures_key)
        info["signatures"] = signatures

        # ofd:Creator 
        creator: list = []
        creator_key = "ofd:Creator"
        self.recursion_ext(self.xml_obj, creator, creator_key)
        info["creator"] = creator

        # ofd:CreationDate 
        reation_date: list = []
        creation_date_key = "ofd:CreationDate"
        self.recursion_ext(self.xml_obj, reation_date, creation_date_key)
        info["creationDate"] = reation_date

        return info


class DocumentFileParser(FileParserBase):
    """
    Document 为doc内的根节点 包含：
    1 文件的路径 2 doc的size 
    """

    def loc2page_no(self, loc, idx):
        pg_no = re.search(r"\d+", loc)
        if pg_no:
            pg_no = int(pg_no.group())
        else:
            pg_no = idx
        return pg_no

    def __call__(self):
        document_info = {}

        # size 
        physical_box: list = []
        physical_box_key = "ofd:PhysicalBox"
        self.recursion_ext(self.xml_obj, physical_box, physical_box_key)
        document_info["size"] = physical_box[0] if physical_box else ""

        # ofd:PublicRes路径 包含字体路径信息 
        public_res: list = []
        public_res_key = "ofd:PublicRes"
        self.recursion_ext(self.xml_obj, public_res, public_res_key)
        document_info["public_res"] = public_res

        # ofd:DocumentRes路径  包含静态资源图片
        document_res: list = []
        document_res_key = "ofd:DocumentRes"
        self.recursion_ext(self.xml_obj, document_res, document_res_key)
        document_info["document_res"] = document_res

        # ofd:Page 正文
        page: list = []
        page_id_map = {}
        apage_key = "ofd:Page"
        self.recursion_ext(self.xml_obj, page, apage_key)
        if page:
            page_id_map = {
                i.get("@ID"): self.loc2page_no(i.get("@BaseLoc"), idx)
                for idx, i in enumerate(page)
            }
            page = [i.get("@BaseLoc") if isinstance(i, dict) else i for i in page]

        document_info["page"] = page
        document_info["page_id_map"] = page_id_map

        tpls: list = []
        template_page_key = "ofd:TemplatePage"
        self.recursion_ext(self.xml_obj, tpls, template_page_key)
        if tpls:
            tpls = [i.get("@BaseLoc") if isinstance(i, dict) else i for i in tpls]
        document_info["tpls"] = tpls

        return document_info


class ContentFileParser(FileParserBase):
    """
    Parser Contents&tpls

    """

    def fetch_cell_info(self, row, TextObject):
        """fetch_cell_info"""
        cell_d = {}
        cell_d = {}
        cell_d["ID"] = row['@ID']  # 字体
        # 字体字形信息
        if row.get("ofd:CGTransform"):
            Glyphs_d = {
                "Glyphs": row.get("ofd:CGTransform").get("ofd:Glyphs"),
                "GlyphCount": row.get("ofd:CGTransform").get("@GlyphCount"),
                "CodeCount": row.get("ofd:CGTransform").get("@CodeCount"),
                "CodePosition": row.get("ofd:CGTransform").get("@CodePosition")
            }
            cell_d["Glyphs_d"] = Glyphs_d

        cell_d["pos"] = [float(pos_i) for pos_i in row['@Boundary'].split(" ")]  # 文本框
        if row.get('ofd:Clips', {}).get('ofd:Clip', {}).get('ofd:Area', {}).get('ofd:Path', {}):
            cell_d["clips_pos"] = [float(pos_i) for pos_i in
                                   row.get('ofd:Clips', {}).get('ofd:Clip', {}).get('ofd:Area', {}).get('ofd:Path',
                                                                                                        {}).get(
                                       '@Boundary', "").split(" ")]
        cell_d["text"] = str(TextObject.get('#text'))
        cell_d["font"] = row['@Font']  # 字体
        cell_d["size"] = float(row['@Size'])  # 字号
        # print("row", row)

        color =self.ofd_param("ofd:FillColor", row).get("@Value", "0 0 0")

        cell_d["color"] = tuple(color.split(" "))  # 颜色
        cell_d["DeltaY"] = TextObject.get("@DeltaY", "")  # y 轴偏移量 竖版文字表示方法之一
        cell_d["DeltaX"] = TextObject.get("@DeltaX", "")  # x 轴偏移量
        cell_d["CTM"] = row.get("@CTM", "")  # 平移矩阵换

        cell_d["X"] = TextObject.get("@X", "")  # X 文本之与文本框距离
        cell_d["Y"] = TextObject.get("@Y", "")  # Y 文本之与文本框距离
        return cell_d

    def __call__(self) -> list:
        """
       
        输出主体坐标和文字信息 cell_list
        [{"pos":row['@Boundary'].split(" "),
                    "text":row['ofd:TextCode'].get('#text'),
                    "font":row['@Font'],
                    "size":row['@Size'],}]
        """
        text_list = []
        img_list = []
        line_list = []

        content_d = {
            "text_list": text_list,
            "img_list": img_list,
            "line_list": line_list,
        }

        text: list = []  # 正文
        text_key = "ofd:TextObject"
        self.recursion_ext(self.xml_obj, text, text_key)

        if text:
            for row in text:
                # print("row", row.get('ofd:TextCode', {}))
                if isinstance(row.get('ofd:TextCode', {}), list):
                    for _i in row.get('ofd:TextCode', {}):
                        if not _i.get('#text'):
                            continue
                        cell_d = self.fetch_cell_info(row, _i)
                        text_list.append(cell_d)

                elif isinstance(row.get('ofd:TextCode', {}), dict):
                    if not row.get('ofd:TextCode', {}).get('#text'):
                        continue
                    cell_d = self.fetch_cell_info(row, row.get('ofd:TextCode', {}))
                    text_list.append(cell_d)

                else:
                    logger.error(f"'ofd:TextCode' format nonsupport  {row.get('ofd:TextCode', {})}")
                    continue

        line: list = []  # 路径线条
        line_key = "ofd:PathObject"
        self.recursion_ext(self.xml_obj, line, line_key)

        if line:
            # print(line)
            for _i in line:
                line_d = {}
                # print("line",_i)
                line_d["ID"] = _i.get("@ID", "")  # 图片id
                line_d["pos"] = [float(pos_i) for pos_i in _i['@Boundary'].split(" ")]  # 平移矩阵换
                line_d["LineWidth"] = _i.get("@LineWidth", "")  # 图片id
                line_d["AbbreviatedData"] = _i.get("ofd:AbbreviatedData", "")  # 路径指令
                line_d["FillColor"] = self.ofd_param("ofd:FillColor", _i).get('@Value', "0 0 0").split(" ")  # 颜色
                line_d["StrokeColor"] = self.ofd_param("ofd:StrokeColor", _i).get('@Value', "0 0 0")  # 颜色

                line_list.append(line_d)

        img: list = []  # 图片
        img_key = "ofd:ImageObject"
        self.recursion_ext(self.xml_obj, img, img_key)

        if img:
            for _i in img:
                img_d = {}
                img_d["CTM"] = _i.get("@CTM", "")  # 平移矩阵换
                img_d["ID"] = _i.get("ID", "")  # 图片id
                img_d["ResourceID"] = _i.get("@ResourceID", "")  # 图片id
                img_d["pos"] = [float(pos_i) for pos_i in _i['@Boundary'].split(" ")]  # 平移矩阵换
                img_list.append(img_d)

        return content_d


class DocumentResFileParser(FileParserBase):
    """
    Parser DocumentRes 抽取里面图片信息

    """

    def __call__(self):
        info = {}
        muti_media: list = []
        muti_media_key = "ofd:MultiMedia"
        self.recursion_ext(self.xml_obj, muti_media, muti_media_key)
        if muti_media:
            for media in muti_media:
                name = media.get("ofd:MediaFile", "")
                info[media.get("@ID")] = {
                    "format": media.get("@Format", ""),
                    "wrap_pos": media.get("@wrap_pos", ""),
                    "type": media.get("@Type", ""),
                    "suffix": os.path.splitext(name)[-1].replace(".", ""),  # 文件后缀名
                    "fileName": name,
                }
        return info


class PublicResFileParser(FileParserBase):
    """
    Parser PublicRes 抽取里面 获取公共信息 字体信息

    """

    def __call__(self):
        info = {}
        public_res: list = []
        public_res_key = "ofd:Font"
        self.recursion_ext(self.xml_obj, public_res, public_res_key)

        if public_res:
            for i in public_res:
                info[i.get("@ID")] = {
                    "FontName": i.get("@FontName"),
                    "FamilyName": i.get("@FamilyName"),
                    "Bold": i.get("@Bold"),
                    "Serif": i.get("@Serif"),
                    "FixedWidth": i.get("@FixedWidth"),
                    "FontFile": i.get("ofd:FontFile"),
                }
        return info


class AnnotationFileParser(FileParserBase):
    """
    Parser Annotation
    签名信息 暂不用
    """
    pass


class SignaturesFileParser(FileParserBase):
    """
    Parser Signatures
    签章信息-总
    """

    def __call__(self):
        info = {}
        signature_res: list = []
        signature_res_key = "ofd:Signature"
        self.recursion_ext(self.xml_obj, signature_res, signature_res_key)

        if signature_res:
            for i in signature_res:
                info[i.get("@ID")] = {
                    "BaseLoc": i.get("@BaseLoc"),
                    "Type": i.get("@Type"),
                    "ID": i.get("@ID"),

                }
        return info


class SignatureFileParser(FileParserBase):
    """
    Parser Signature
    签章信息
    """

    def __call__(self, prefix=""):
        info = {}
        StampAnnot_res: list = []
        StampAnnot_res_key = "ofd:StampAnnot"

        self.recursion_ext(self.xml_obj, StampAnnot_res, StampAnnot_res_key)

        SignedValue_res: list = []
        SignedValue_res_key = "ofd:SignedValue"
        self.recursion_ext(self.xml_obj, SignedValue_res, SignedValue_res_key)

        # print("SignedValue_res", SignedValue_res)
        # print("prefix", prefix)
        if StampAnnot_res:
            for i in StampAnnot_res:
                info = {
                    "PageRef": i.get("@PageRef"),  # page id
                    "Boundary": i.get("@Boundary"),
                    "ID": i.get("@ID"),
                    "SignedValue": f"{prefix}/{SignedValue_res[0]}" if SignedValue_res else f"{prefix}/SignedValue.dat",
                }

        return info


if __name__ == "__main__":
    FileParserBase("")()
