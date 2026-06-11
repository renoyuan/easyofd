#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: easyofd
# CREATE_TIME:
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: 参数解析器，负责解析 OFD 中的 CTM、Boundary、Color 等参数
import re
from typing import List, Dict, Any, Union, Tuple, Optional

from loguru import logger


class ParameterParser(object):
    """
    OFD 参数解析器
    解析 CTM 矩阵、Boundary 边界、颜色值等标准 OFD 属性
    """

    parameter = {
        "ofd:FillColor": (dict, dict),
        "ofd:StrokeColor": (dict, dict),
        "ofd:Test": ((str, int), str),
        "ofd:Font": (str, str),
        "@Value": (str, str),
    }

    def __call__(self, key: str, container: dict) -> Any:
        """
        安全获取参数值，带类型校验

        Args:
            key: 参数字段名
            container: 参数字典

        Returns:
            参数值，类型不匹配时返回默认值
        """
        if key in self.parameter:
            v = container.get(key, None)
            t = self.parameter[key]
            if isinstance(v, t[0]):
                return v
            else:
                return t[1]()
        else:
            logger.warning(f"{key} not in ParameterParser")
            return None

    @staticmethod
    def parse_CTM(ctm_str: str) -> List[float]:
        """
        解析 CTM 矩阵字符串为浮点数列表

        Args:
            ctm_str: CTM 字符串，如 "1 0 0 1 0 0"

        Returns:
            6 个浮点数列表，解析失败返回单位矩阵 [1, 0, 0, 1, 0, 0]
        """
        if not ctm_str:
            return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        try:
            parts = [float(x) for x in ctm_str.split() if re.match(r"[\d\.\-]", x)]
            if len(parts) == 6:
                return parts
            return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        except (ValueError, AttributeError):
            logger.warning(f"CTM 解析失败: {ctm_str}")
            return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

    @staticmethod
    def parse_Boundary(boundary_str: str) -> List[float]:
        """
        解析 Boundary 边界字符串

        Args:
            boundary_str: Boundary 字符串，如 "0 0 595 842"

        Returns:
            4 个浮点数列表 [x, y, w, h]，解析失败返回空列表
        """
        if not boundary_str:
            return []
        try:
            return [float(x) for x in boundary_str.split() if re.match(r"[\d\.\-]", x)]
        except (ValueError, AttributeError):
            logger.warning(f"Boundary 解析失败: {boundary_str}")
            return []

    @staticmethod
    def parse_Color(color_value: Any) -> Optional[Tuple[int, int, int]]:
        """
        解析 OFD 颜色值

        Args:
            color_value: 颜色字典，如 {"Value": "255 0 0"}，或 None

        Returns:
            RGB 三元组，解析失败返回 None
        """
        if color_value is None:
            return None
        try:
            if isinstance(color_value, dict):
                value = color_value.get("Value", "")
                if isinstance(value, str):
                    parts = [int(float(x)) for x in value.split() if re.match(r"[\d\.]", x)]
                    if len(parts) >= 3:
                        return (parts[0], parts[1], parts[2])
            return None
        except (ValueError, AttributeError):
            return None
