#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
tools

360yunpan - 360YunPan Command-line tools, support: Linux Mac Windows
Licensed under the MIT license:
  http://www.opensource.org/licenses/mit-license.php
Project home:
  https://github.com/logbird/360yunpan
Version:  1.0.0

@Author logbird@126.com
***This is a change for Python3.5***
"""

__author__ = 'cheng'
__version__ = '1.2.0'

import sys
import json
import re
import os
import hashlib
import importlib

importlib.reload(sys)
# sys.setdefaultencoding("utf-8")

def jsonRepair(str_json):
    #str = str.replace(' ', '')
    regx = r'([{|,])[\' ]*([a-zA-Z_]*)[\' ]*:'
    str_json = re.sub(regx, r'\1"\2" :', str_json);
    str_json = str_json.replace("'", '"')
    return str_json

def getConfig(key):
    config = {
        'tmpDir' : sys.path[0] + '/tmp'
    }
    if key in config:
        return config[key]
    else:
        return ''

def isText(s):
    text_characters = "".join(list(map(chr, range(32, 127))) + list("\n\r\t\b"))
    _null_trans = str.maketrans("", "")
    '''
        判断文件是文本还是二进制
    '''
    if "\0" in s:
        return False

    if not s:
        return 1
    t = s.translate(_null_trans, text_characters)
    if float(len(t))/float(len(s)) > 0.30:
        return False
    return True

def checkFileHash(fpath, fhash):
    '''根据路径和文件的hash值来验证文件是否产生变化

    '''
    pass
