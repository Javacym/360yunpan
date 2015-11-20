#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
main.py

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
import urllib.request
from http import cookiejar
import time
import random
import hashlib
import json
import re
import os
import importlib

importlib.reload(sys)
# sys.setdefaultencoding("utf-8")

import utilsYunPan
from loginYunPan import LoginYunPan
from dirYunPan import DirYunPan
from downloadYunPan import DownloadYunPan
from downloadYunPan import DownloadManager


if __name__ == '__main__':
    login = LoginYunPan()
    userinfo = login.run('用户名', '密码')
    pathYunPan = '~/test/'
    dir = DirYunPan(pathYunPan, login.serverAddr)
    # 需要下载的云盘路径
    tree = dir.downloadDirTree('/', True)
    DownloadManager.pushQueue(tree)
    # 设置线程数
    DownloadManager.start(dir, 10)
    # 离线下载
    #result = dir.offlineDownload("http://todeer.sinaapp.com/include/lib/js/common_tpl.js");
    # 获取离线下载列表
    #result = dir.offlineList();
