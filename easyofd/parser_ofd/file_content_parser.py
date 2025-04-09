#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME:  file_content_parser.py
# CREATE_TIME: 2025/3/28 11:47
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: 解析正文
from loguru import  logger
from .file_parser_base import FileParserBase


class ContentFileParser(FileParserBase):
    """
    Parser Contents&tpls
    /xml_dir/Doc_0/Doc_0/Pages/Page_0/Content.xml
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

        color = self.ofd_param("ofd:FillColor", row).get("@Value", "0 0 0")

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
                try:
                    line_d["ID"] = _i.get("@ID", "")  # 图片id
                    line_d["pos"] = [float(pos_i) for pos_i in _i['@Boundary'].split(" ")]  # 平移矩阵换
                    line_d["LineWidth"] = _i.get("@LineWidth", "")  # 图片id
                    line_d["AbbreviatedData"] = _i.get("ofd:AbbreviatedData", "")  # 路径指令
                    line_d["FillColor"] = self.ofd_param("ofd:FillColor", _i).get('@Value', "0 0 0").split(" ")  # 颜色
                    line_d["StrokeColor"] = self.ofd_param("ofd:StrokeColor", _i).get('@Value', "0 0 0")  # 颜色
                except KeyError as e:
                    logger.error(f"{e} \n line is {_i} \n")
                    continue
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

