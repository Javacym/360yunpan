#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
目录下载 文件下载

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

class DirYunPan:

    serverAddr = None
    pathYunPan = None
    directoryTree = None

    def __init__(self, pathYunPan, serverAddr):
        '''构造函数

            pathYunPan String 本地云盘的绝对路径
            serverAddr String 登陆成功后 loginYunPan的serverAddr属性
        '''
        self.serverAddr = serverAddr
        self.pathYunPan = pathYunPan
        self.mkdir(pathYunPan)

    def df(self):
        '''获取网盘剩余空间
        '''
        url = self.serverAddr + "/user/getsize/?t=1377829621254&ajax=1"
        result = urllib.request.urlopen(url).read()
        result=result.decode('utf8')
        result = json.loads(result)
        if int(result['errno']) == 0:
            size = {}
            size['total'] = int(result['data']['total_size'])
            size['used'] = int(result['data']['used_size'])
            size['free'] = int(result['data']['total_size']) - int(result['data']['used_size'])

            return size
        else:
            print ('Fetch Free Space Size Error! Message: '+ result['errmsg'])
            sys.exit()

    def offlineList(self):
        '''获取离线下载列表
        '''
        url = self.serverAddr + "/offline/getOfflineTaskList"
        args = {
            'ajax' : '1',
        }
        referer = self.serverAddr + "/my/index/"
        result = self._getResult(url,args,referer)
        if int(result['errno']) == 0:
            return result['data']
        else:
            print ('Get Offline Tast List Err! Message: '+ result['errmsg'])
            sys.exit()

    def offlineDownload(self, offurl):
        '''离线下载
        '''
        url = self.serverAddr + "/offline/offlineDownload"
        args = {
            'ajax' : '1',
            'url' : offurl,
        }
        referer = self.serverAddr + "/my/index/"
        result = self._getResult(url,args,referer)
        if int(result['errno']) == 0:
            return result['data']
        else:
            print ('Create Offline Tast Err! Message: '+ result['errmsg'])
            sys.exit()

    def _getResult(url,args,referer):
        args = urllib.parse.urlencode(args)
        reqArgs  = urllib.request.Request(
            url = url,
            data = bytes(args,'utf8')
        )
        reqArgs.add_header("Referer", referer);
        result = urllib.request.urlopen(reqArgs).read()
        result = result.decode('utf8')
        result = utilsYunPan.jsonRepair(result)
        result = json.loads(result)
        return result

    def ls(self, path = '/'):
        '''获取path目录下的文件列表

            path String 需要查询的路径 根目录为 /
        '''
        url = self.serverAddr + '/file/list'
        args = {
            'ajax' : '1',
            'field' : 'file_name',
            'order' : 'desc',
            'page' : '0',
            'page_size' : '300',
            'path' : path,
            't' : str(random.random()),
            'type' : '2'
        }
        referer = "http://c21.yunpan.360.cn/my/index/"
        result = self._getResult(url,args,referer)
        if int(result['errno']) == 0:
            return result['data']
        else:
            print ('Get Dir List Error, Please try again later! Message: '+ result['errmsg'])
            sys.exit()

    def downloadFile(self, fname, nid, fileHash):
        ''' 根据文件名和节点ip下载文件

            fname String 文件路径名称 path
            nid Long 节点id
            fielHash String 文件的hash值
        '''
        # 如果hash值相同则无需下载
        #if fileHash == utilsYunPan.getFileHash(fname):
        #    return True
        url = self.serverAddr + "/file/download"
        args = {
            'fname' : fname,
            'hid' : '',
            'nid' : nid
        }
        referer = "http://c21.yunpan.360.cn/my/index/"
        result  = self._getResult(url,args,referer)
        # 这里需要做一些验证
        result = urllib.request.urlopen(result['data']['download_url']).read()
        fname = self.pathYunPan + fname
        if utilsYunPan.isText(result[0:512]):
            print ("Download File: " + fname + " type: ASCII")
            open(fname, 'w').write(result)
        else:
            print ("Download File: " + fname + " type: Binary")
            open(fname, 'wb').write(result)

    def downloadDirTree(self, path = '/', force = False):
        dirTreeName = utilsYunPan.getConfig('tmpDir') + '/dirTree.dat'
        tree = []
        if os.path.exists(dirTreeName):
            tree = open(dirTreeName).read()
            tree = json.loads(tree)

        if len(tree) == 0 or force:
            tree = self.fetchDirTree(path)
            open(dirTreeName, "w").write(json.dumps(tree))

        # 保存文件数
        self.directoryTree = tree

        # 开始下载文件夹
        for i in tree:
            if len(i) > 0 and i.get('isDir',0) == 1:
                self.mkdir(self.pathYunPan + i['path'])
                print ("Download Directroy: " + i['path'])
                # 查询子目录
                if len(i.get('childs','')) > 0:
                    tree += i['childs']
        return tree

    def fetchDirTree(self, path = '/'):
        dirList = self.ls(path)
        for i in dirList:
            if len(i) > 0 and i.get('isDir',0) == 1:
                print ("Fetch Directroy: " + i['path'])
                i['childs']= self.fetchDirTree(i['path']);
        sys.stdout.flush()
        return dirList

    def mkdir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)


if __name__ == '__main__':
    login = LoginYunPan()
    userinfo = login.run('user', 'pwd')
    pathYunPan = 'E:/testyun'
    dir = dirYunPan(pathYunPan, login.serverAddr)
    dir.downloadFile('/文档/体检报告.pdf', '13679929262714855', 'c26aac23bd0e3c1565adeee9d6681dcab37fb2a9')





# 签到 http://c21.yunpan.360.cn/user/signin/
'''
ajax	1
'''

# 提示 http://c21.yunpan.360.cn/notice/getNoticeCount
'''
ajax	1
method	check
qid	15747194
t	1377830443043
'''

# 上传 http://c21.yunpan.360.cn/upload/getuploadaddress/
'''
ajax    1
'''
