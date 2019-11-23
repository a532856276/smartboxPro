#!/usr/bin/env python
# -*- coding:  utf-8 -*-
# author: albert  time:$(DATA)
import time
import threading
from abc import abstractmethod


class TimeBase(threading.Thread):
    def __init__(self, func, sleepTime, runFlag):
        self.sleepTime = sleepTime
        self.func = func
        self.runFlag = runFlag
        self.doFlag = False
        #self.timer_thread = threading.Thread(target=self.run(), args={"aaa"})
        #self.timer_thread.start()
        threading.Thread.__init__(self)

    def run(self, args=(), kwargs=None):
        print(u'时间定时器工作{0} -- {1}'.format(args, kwargs))
        
        
        #self.fun()
        while self.runFlag:
            time_now = time.localtime()
            time_now_min = time.strftime("%M", time_now)  # 刷新
            print(u'时间nowTime:1')
            if int(time_now_min) % self.sleepTime == 0: #此处设置每天定时的时间
                if self.doFlag is False:
                    time.sleep(1) #等待1s保证获取到新的kline
                    self.fun()
                    self.doFlag  = True
                    print(u'时间定时器工作{0}min,nowTime:{1}'.format(self.sleepTime,time_now))
                    #time.sleep(self.sleepTime)
            else:
                self.doFlag = False
            time.sleep(1)

    @abstractmethod
    def fun(self):
        # fun 为虚函数，需要在子类实现
        pass

    def setRunFlag(self, runFlag):
        self.runFlag = runFlag
