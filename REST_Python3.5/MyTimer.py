#!/usr/bin/env python
# -*- coding:  utf-8 -*-
# author: albert  time:$(DATA)
from TimeBase import TimeBase

'''
使用方法
创建对象时传入回调函数/定时时间/启动标志
如下：
g_QueryKline = MyTimer(GetContractKline, 5, True)
g_QueryKline.setRunFlag(True); # 可执行也可不执行，创建时传入了True
g_QueryKline.start();

# 启动定时器，定时查询k线
	timeQurey = threading.Timer(5, GetContractKline)
	timeQurey.start();
这种方式是指在5秒后执行GetContractKline函数一次，如果还需执行则需要重复上面两操作
while True：
	timeQurey = threading.Timer(5, GetContractKline)
	timeQurey.start();
'''


class MyTimer(TimeBase):
    def __init__(self, func, sleepTime, runFlag):
        TimeBase.__init__(self, func, sleepTime, runFlag)
        self.func = func

    def fun(self):
        self.func()
