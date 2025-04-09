#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME:  path_parser.py
# CREATE_TIME: 2025/4/9 16:31
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE:
from enum import Enum
import os

class PathType(Enum):
    absolutely = 1
    relative = 2

class PathParser:
    """
    Parser Path
    路径解析器
    解析文件路径返回绝对路径
    "/ROOT/a.xml"
    "./ROOT/a.xml"
    "../ROOT/a.xml"
    "ROOT/a.xml"
    """

    def __init__(self, root_path:str):
        if os.name == 'nt':
            self.os = "nt"
        else:
            self.os = "posix"

        self.root_path = self.format_path(root_path)

    def format_path(self,path:str):
        normalized = os.path.normpath(path)
        if self.os == "nt":
            return normalized.replace("/","\\")
        else:
            return normalized.replace("\\","/")

    def get_path_type(self, path:str):
        if os.path.isabs(path):
            return PathType.absolutely
        else:
            return PathType.relative

    def __call__(self,cur_path:str,loc_path:str):
        """
        loc_path is posix style
        """
        path_type = self.get_path_type(loc_path)
        if path_type == PathType.absolutely:
            return self.format_path(loc_path)
        if path_type == PathType.relative:
            if loc_path.startswith("./"):
                path = os.path.join(cur_path, self.format_path(loc_path[2:]))
            elif loc_path.startswith("../"):
                path = os.path.join(os.path.dirname(cur_path), self.format_path(loc_path[3:]))
            else:
                path = os.path.join(os.path.dirname(cur_path), self.format_path(loc_path))
            return path