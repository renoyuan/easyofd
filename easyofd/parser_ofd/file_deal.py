#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: D:\code\easyofd\easyofd\parser
# CREATE_TIME: 2023-07-27
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: 文件处理，OFD 解压、文件树构建、xml 解析
import os
import base64
import shutil
import zipfile
from typing import Any, Dict, Optional
from uuid import uuid1

import xmltodict
from loguru import logger

from .path_parser import PathParser


class FileReadError(Exception):
    """OFD 文件读取/解析异常"""
    pass


class FileRead(object):
    """
    OFD 文件读取器

    1. 将 base64 解码为 zip 文件
    2. 解压 zip
    3. 遍历文件树，xml 转为 dict，其他文件转为 base64
    4. 清理临时文件

    返回 file_tree 结构:
        'root': 解压路径
        'root_doc': OFD.xml 的绝对路径
        'pdf_name': 输出 pdf 文件名
        {绝对路径}: xml → dict / 其他文件 → base64 字符串
    """

    def __init__(self, ofdb64: Optional[str]) -> None:
        """
        Args:
            ofdb64: OFD 文件的 base64 编码字符串

        Raises:
            FileReadError: ofdb64 为空或解码失败
        """
        if not ofdb64:
            raise FileReadError("ofdb64 不能为空，请检查 OFD 文件内容")

        try:
            self.ofdbyte = base64.b64decode(ofdb64)
        except Exception as e:
            raise FileReadError(f"base64 解码失败: {e}")

        pid = os.getpid()
        self.name = f"{pid}_{str(uuid1())}.ofd"
        self.pdf_name = self.name.replace(".ofd", ".pdf")
        self.zip_path: str = os.path.join(os.getcwd(), self.name)
        self.unzip_path: str = ""
        self.file_tree: Dict[str, Any] = {}
        self.save_xml: bool = False
        self.xml_name: Optional[str] = None

    def unzip_file(self) -> None:
        """
        将 ofd 字节写入临时文件并解压

        Raises:
            FileReadError: 写入或解压失败
        """
        try:
            with open(self.zip_path, "wb") as f:
                f.write(self.ofdbyte)

            self.unzip_path = self.zip_path.split('.')[0]

            with zipfile.ZipFile(self.zip_path, 'r') as zf:
                for file in zf.namelist():
                    zf.extract(file, path=self.unzip_path)

            # 如果开启了保存 xml 调试选项，额外保存一份解压内容
            if self.save_xml and self.xml_name:
                logger.info(f"saving xml to {self.xml_name}")
                with zipfile.ZipFile(self.zip_path, 'r') as zf:
                    for file in zf.namelist():
                        zf.extract(file, path=self.xml_name)

        except zipfile.BadZipFile:
            raise FileReadError("OFD 文件不是有效的 zip 格式")
        except OSError as e:
            raise FileReadError(f"文件读写失败: {e}")

    def _safe_read_xml(self, filepath: str) -> Optional[dict]:
        """安全地读取并解析 xml 文件，失败返回 None"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return xmltodict.parse(f.read())
        except Exception as e:
            logger.warning(f"XML 解析失败: {filepath}, {e}")
            return None

    def _safe_read_binary_b64(self, filepath: str) -> Optional[str]:
        """安全地读取二进制文件并转为 base64，失败返回 None"""
        try:
            with open(filepath, "rb") as f:
                return str(base64.b64encode(f.read()), "utf-8")
        except Exception as e:
            logger.warning(f"二进制文件读取失败: {filepath}, {e}")
            return None

    def build_file_tree(self) -> None:
        """
        构建文件树：
        - xml 文件 → dict
        - 其他文件 → base64 字符串
        - 完成后清理临时文件
        """
        self.file_tree["root"] = self.unzip_path
        self.file_tree["pdf_name"] = self.pdf_name

        if not os.path.exists(self.unzip_path):
            raise FileReadError(f"解压目录不存在: {self.unzip_path}")

        for root, dirs, files in os.walk(self.unzip_path):
            for file in files:
                abs_path = os.path.join(root, file)
                if file.lower().endswith(".xml"):
                    parsed = self._safe_read_xml(abs_path)
                    if parsed is not None:
                        self.file_tree[abs_path] = parsed
                else:
                    b64_val = self._safe_read_binary_b64(abs_path)
                    if b64_val is not None:
                        self.file_tree[abs_path] = b64_val

        # 定位根文档 OFD.xml
        ofd_xml_path = os.path.join(self.unzip_path, "OFD.xml")
        if ofd_xml_path in self.file_tree:
            self.file_tree["root_doc"] = ofd_xml_path
        else:
            logger.warning("OFD.xml 未找到，解析可能不完整")

        # 清理临时文件
        self._cleanup()

    def _cleanup(self) -> None:
        """清理解压目录和 zip 临时文件"""
        try:
            if os.path.exists(self.unzip_path):
                shutil.rmtree(self.unzip_path)
            if os.path.exists(self.zip_path):
                os.remove(self.zip_path)
        except OSError as e:
            logger.warning(f"临时文件清理失败: {e}")

    def __call__(self, *args: Any, **kwds: Any) -> Dict[str, Any]:
        """
        执行完整的 OFD 文件读取流程

        Args:
            save_xml: 是否保存解压的 xml 到独立目录（调试用）
            xml_name: 保存 xml 的目录名

        Returns:
            文件树字典
        """
        self.save_xml = kwds.get("save_xml", False)
        self.xml_name = kwds.get("xml_name")

        self.unzip_file()
        self.build_file_tree()
        return self.file_tree


if __name__ == "__main__":
    with open(r"D:/code/easyofd/test/增值税电子专票5.ofd", "rb") as f:
        ofdb64 = str(base64.b64encode(f.read()), "utf-8")
    a = FileRead(ofdb64)()
    print(list(a.keys()))