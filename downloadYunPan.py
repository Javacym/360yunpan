#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
多线程下载管理器

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

import json
import sys
from threading import Thread
import utilsYunPan

class DownloadYunPan(Thread):
    dir = None
    def __init__(self, dir):
        Thread.__init__(self)
        self.dir = dir

    def run(self):
        while True:
            try:
                finfo = DownloadManager.popFile()
                self.dir.downloadFile(finfo['path'], finfo['nid'], finfo['fhash'])
                sys.stdout.flush()
            except IndexError:
                break


class DownloadManager():
    '''
        oriName = "反面.jpg"
        path = "/图片/反面.jpg"
        nid = "13745783832785911"
        date = "2013-07-23 19:19"
        oriSize = "167332"
        size = "163.4KB"
        scid = "21"
        preview = "1"
        hasThumb = true
        thumb = "http://t21-1.yunpan.360...972bb352e450&d=20130902"
        pic = "http://dl21.yunpan.360....af49d7acdabaad563cb964&"
        fhash = "88196e3f6edfe9280ede0aa98a28ac02e471be88"
        fileType = "jpg"
        mtime = "2013-07-23 19:19:52"
        fmtime = "2013-07-23 19:19"
    '''
    downloadQueue = []

    @classmethod
    def pushQueue(self, tree):
        '''将目录树种的待下载文件压入队列中
            tree List 目录树
        '''
        # 整理下载队列
        for i in tree:
            if len(i) > 0 and i.get('isDir',0) == 1:
                # 查询子目录
                if len(i.get('childs','')) > 0:
                    tree += i['childs']
            elif len(i) > 0 and 'oriSize' in i and 'fileType' in i:
                self.downloadQueue.append(i)


    @classmethod
    def popFile(self):
        return self.downloadQueue.pop(0)

    @classmethod
    def start(self, dir, threadCount = 1):
        sThread = []
        print ("Download Starting in {0} Threads, Please Wait!".format(threadCount))
        sys.stdout.flush()
        for i in range(0, threadCount):
            c = DownloadYunPan(dir)
            c.start()
            sThread.append(c)

        for st in sThread:
            st.join()

        print ("All Is Done!")
