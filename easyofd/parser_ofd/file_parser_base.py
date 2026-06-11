#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME:  file_parser_base.py
# CREATE_TIME: 2025/3/28 11:43
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: base 解析器

import sys
import logging
from typing import Any, List, Union, Dict, Optional

sys.path.insert(0, "..")
from .parameter_parser import ParameterParser

logger = logging.getLogger("root")


class FileParserBase(object):
    """xml 解析基类，提供递归抽取 xml 要素的能力"""

    def __init__(self, xml_obj: Optional[Union[Dict, str]]) -> None:
        """
        Args:
            xml_obj: xml 字典对象（由 xmltodict 解析后产生）。
                      不允许为 None 或空值。
        Raises:
            AssertionError: 当 xml_obj 为 None 时抛出。
        """
        if xml_obj is None:
            raise ValueError("xml_obj 不能为 None，请检查 OFD 文件是否正确解析")
        self.ofd_param = ParameterParser()
        self.xml_obj: Union[Dict, str] = xml_obj

    def recursion_ext(
        self,
        need_ext_obj: Any,
        ext_list: List,
        key: str,
        parent_draw_param: str = "",
    ) -> None:
        """
        递归抽取 xml 中指定 key 的要素

        Args:
            need_ext_obj: 当前遍历的 xml 片段（dict / list / str）
            ext_list: 结果收集容器
            key: 要抽取的标签名，如 "ofd:Page", "ofd:TextObject"
            parent_draw_param: 父级 DrawParam 引用，用于继承
        """
        if isinstance(need_ext_obj, dict):
            current_draw_param = need_ext_obj.get("@DrawParam", parent_draw_param)
            if current_draw_param:
                need_ext_obj["@DrawParam"] = current_draw_param
            for k, v in need_ext_obj.items():
                if k == key:
                    if isinstance(v, (dict, str)):
                        if isinstance(v, dict) and "@DrawParam" not in v and current_draw_param:
                            v["@DrawParam"] = current_draw_param
                        ext_list.append(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                if "@DrawParam" not in item and current_draw_param is not None:
                                    item["@DrawParam"] = current_draw_param
                        ext_list.extend(v)
                else:
                    if isinstance(v, dict):
                        self.recursion_ext(v, ext_list, key, parent_draw_param=current_draw_param)
                    elif isinstance(v, list):
                        for cell in v:
                            self.recursion_ext(cell, ext_list, key, parent_draw_param=current_draw_param)
        # else: 非 dict/list 类型（int/str）直接忽略，不做任何操作

