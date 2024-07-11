#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: easyofd test
# CREATE_TIME: 2024/7/2 15:19
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:recursion & singletons


a = range(997)
def test_recursion(a,num):

    if num == len(a):
        print("over")
        return
    else:
        print(a[num])
        test_recursion(a, num+1)

class Singletons(object):
    obj = None
    @staticmethod
    def instance():
        if Singletons.obj:
            print("exists")
            return Singletons.obj
        else:
            print("new instance")
            Singletons.obj = Singletons()
            return Singletons.obj

if __name__ =="__main__":
    # try:
    #     test_recursion(a, 0)
    # except RecursionError as e:
    #     raise e
    import time
    for i in range(5):
        time.sleep(0.02)
        obj = Singletons.instance()
