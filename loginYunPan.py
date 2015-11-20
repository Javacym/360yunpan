#!/usr/bin/env python
# coding=utf-8

"""
云盘登陆，该类可以登录所有使用360账号登录的网站
@Example
    login = loginYunPan()
    userinfo = login.run('user', 'pwd')
    print userinfo

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
import urllib.parse
from http import cookiejar
import time
import random
import hashlib
import json
import re
import os

class LoginYunPan():

    cookieFile = None
    cookie_jar = None
    serverAddr = None
    userFile = None

    def __init__(self):
        self._envInit()
        self._loginInit()

    def _envInit(self):

        base = sys.path[0] + "/tmp"
        self.userFile = base + '/user.dat'
        self.cookieFile = base + '/cookie.dat'
        if not os.path.isdir(base):
            os.mkdir(base)
        if not os.path.exists(self.userFile):
            open(self.userFile, 'w').close()
        if not  os.path.exists(self.cookieFile):
            open(self.cookieFile, 'w').close()

    def _loginInit(self):
        self.cookie_jar  = cookiejar.LWPCookieJar(self.cookieFile)
        try:
            self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
        except Exception:
            self.cookie_jar.save(self.cookieFile, ignore_discard=True, ignore_expires=True)
        cookie_support = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        handler=urllib.request.HTTPHandler()
        opener = urllib.request.build_opener(cookie_support,handler)
        urllib.request.install_opener(opener)

    def getToken(self, username):
        '''根据用户名等信息获得登陆的token值
            username 字符串,用户名
            return 返回Token 值
        '''
        login = {
            'callback' : 'QiUserJsonP1377767974691',
            'func' : 'test',
            'm' : 'getToken',
            'o' : 'sso',
            'rand' : str(random.random()),
            'userName' : username
        }
        url = "https://login.360.cn/?"
        queryString = urllib.parse.urlencode(login)
        url += queryString
        result = urllib.request.urlopen(url).read()
        result=result.decode('utf8')
        #result like test({"errno":0,"errmsg":"","token":"a217ee1cb87f9dc0"})
        result = result.strip(' ')
        result = json.loads(result[5:-1])
        token = ''
        if int(result['errno']) == 0:
            print ('getToken Success')
            token = result['token']
            self.cookie_jar.save(self.cookieFile, ignore_discard=True, ignore_expires=True)
        else:
            print ('getToken Failed, Errno:' + str(result['errno']))
            sys.exit()
        return token


    def doLogin(self, username, password, token):
        '''开始执行登陆操作
            username 字符串,用户名
            password 字符串, 密码
            token 字符串, 根据getToken获得
        '''
        login = {
            'callback' : 'QiUserJsonP1377767974692',
            'captFlag' : '',
            'from' : 'pcw_cloud',
            'func' : 'test',
            'isKeepAlive' : '0',
            'm' : 'login',
            'o' : 'sso',
            'password' : self.pwdHash(password),
            'pwdmethod' : '1',
            'r' : str(time.time()*100),
            'rtype' : 'data',
            'token' : token,
            'userName' : username
        }
        url = "https://login.360.cn/?"
        queryString = urllib.parse.urlencode(login)
        url += queryString
        result = urllib.request.urlopen(url).read()
        result=result.decode('utf8')
        result = result.replace("\n", '').strip(' ')
        result = json.loads(result[5:-1])
        userinfo = {}
        if int(result['errno']) == 0:
            print ('Login Success')
            userinfo = result['userinfo']
            open(self.userFile, 'w').write(json.dumps(userinfo))
            self.cookie_jar.save(self.cookieFile, ignore_discard=True, ignore_expires=True)
        else:
            print ('Login Failed,Errno Type:' + str(result['errno']))
            sys.exit()
        return userinfo

    def getServer(self):
        '''获得分布式服务器的地址
            return True 已登录 False 未登录
        '''
        url = 'http://yunpan.360.cn/user/login?st=163'
        result = urllib.request.urlopen(url).read()
        result=result.decode('utf8')
        regx = "web : '([^']*)'"
        server = re.findall(regx, result)
        if len(server) and server[0] != '' > 0:
            print ("Get Server Success, Server Address:" + server[0])
            self.serverAddr = server[0]
            return True
        else:
            print ("Logining!")
            return False

    def run(self, username, password):
        '''开始执行登陆流程
            username String 用户名
            password String 密码
        '''
        userinfo = None
        if self.getServer():
            print ('Login Success!')
            userinfo = open(self.userFile).read()
            userinfo = json.loads(userinfo)
            return userinfo
        else:
            # 获取token
            token = self.getToken(username)
            # 登陆
            userinfo = self.doLogin(username, password, token);
            # 获得分布式服务器
            self.getServer()
        return userinfo

    def pwdHash(self, password):
        '''md5操作函数用于密码加密
            password String 需要加密的密码
            return 加密后的密码
        '''
        password = password.encode('utf8')
        md5 = hashlib.md5()
        md5.update(password)
        return md5.hexdigest()

if __name__ == '__main__':
    login = LoginYunPan()
    userinfo = login.run('userName', 'password')
    print (userinfo)
