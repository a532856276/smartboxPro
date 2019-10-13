#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataProcess.JudgeData import *
from queue import Queue  # LILO????
from dataProcess.mycommondef import *

import copy

# q = Queue() #创建队列对象
# q.put(0)    #在队列尾部插入元素
# q.put(1)
# q.put(2)
# print('LILO队列',q.queue)  #查看队列中的所有元素
# print(q.get())  #返回并删除队列头部元素
# print(q.queue)
g_HighQueue = Queue()
g_LowQueue = Queue()
KlineQueue = Queue()
g_KlineUpDwnSquence = 0
maxLine = []
lowLine = []
g_LastKline = {}
g_LastTwoKline = 0
g_KlineSave =[]
g_WillDoing= 0
def doNothing():
    pass
def ProcessKline(noDo, willDo):
    if willDo in [myEnum.RISING_HAS_FALLING, myEnum.RISING_IN_FALLING, myEnum.RISING_TO_FALLING]:
        g_OrderSellOpenEvent.set()
    elif willDo in[myEnum.FALLING_HAS_RISING, myEnum.FALLING_IN_RISING, myEnum.FALLING_HAS_RISING]:
        g_OrderBuyOpenEvent.set()
    else:
        print("ProcessKline Error")

# 相当于 getUpDwnSquence
def dataDecodeFromNet(contractKLineLst):
    # {'amount': 50414.6651812045, 'close': 263.537, 'count': 8355, 'high': 265.5, 'id': 1560524400,
    #       'low': 263.2, 'open': 264.461, 'vol': 1332474}
    # 最新数据在list最后
    global maxLine
    global lowLine
    global g_KlineUpDwnSquence
    global g_LastKline
    global g_WillDoing
    global g_halfOfLastKline

    currentKline = 0
    lastKline = 0

    if len(maxLine) or len(lowLine):
        lastKline = g_KlineUpDwnSquence & 0x1
        lastKlinePos = len(g_KlineSave) - 1
        idex = len(contractKLineLst) - 1 - 1
        
        g_halfOfLastKline = getHalfOfKline(contractKLineLst[idex])

        currentKline = getUpOrDwn(contractKLineLst[idex])
        g_KlineUpDwnSquence = g_KlineUpDwnSquence << 1 | currentKline
        tempKline = copy.deepcopy(contractKLineLst[idex])

        #nowStatus = ishammer(tempKline)
        nextDoing = getType(g_KlineSave[lastKlinePos],contractKLineLst[idex])
        #ProcessKline(nowStatus, nextDoing)

        if nextDoing in [myEnum.RISING_HAS_FALLING, myEnum.RISING_IN_FALLING, myEnum.RISING_TO_FALLING]:
            g_OrderSellOpenEvent.set()
            logger.info(u'开空 by kLine:{0}:{1},nextDoing:{2}'.format(lastKline, currentKline, nextDoing))
        elif nextDoing in[myEnum.FALLING_HAS_RISING, myEnum.FALLING_IN_RISING, myEnum.FALLING_HAS_RISING]:
            g_OrderBuyOpenEvent.set()
            logger.info(u'开多 by kLine:{0}:{1},nextDoing:{2}'.format(lastKline, currentKline, nextDoing))
        elif nextDoing in [myEnum.RISING_ONLY_DWN,myEnum.RISING_EQ_DWN,myEnum.RISING_EQ_EQ,myEnum.RISING_EQ_UP,myEnum.RISING_HAMMER_UP,myEnum.RISING_HAMMER_DWN,myEnum.RISING_ONLY_DWN] :
            if currentKline == 1: # and nextDoing == myEnum.RISING_ONLY_DWN:
                g_OrderSellOpenEvent.set()
                logger.info(u'开空 by kLine:{0}:{1},nextDoing'.format(lastKline, currentKline))
            else:
                g_OrderBuyOpenEvent.set()
                logger.info(u'开多 by kLine:{0}:{1}'.format(lastKline, currentKline))
        #if lastKline > currentKline: # 阳阴
        #    if nextDoing in [myEnum.RISING_HAS_FALLING, myEnum.RISING_IN_FALLING, myEnum.RISING_TO_FALLING]:
        #        g_OrderSellOpenEvent.set()
        #        logger.info(u'开空 by kLine:{0}:{1},nextDoing:{2}'.format(lastKline, currentKline, nextDoing))
        #    maxLine.append(tempKline)
        #elif lastKline < currentKline: # 阴阳
        #    if nextDoing in[myEnum.FALLING_HAS_RISING, myEnum.FALLING_IN_RISING, myEnum.FALLING_HAS_RISING]:
        #        g_OrderBuyOpenEvent.set()
        #        logger.info(u'开多 by kLine:{0}:{1},nextDoing:{2}'.format(lastKline, currentKline, nextDoing))
        #    lowLine.append(tempKline)
        #else: # ͬ保持不变
        #    if nowStatus in [myEnum.RISING_ONLY_DWN,myEnum.RISING_EQ_DWN,myEnum.RISING_EQ_EQ,myEnum.RISING_EQ_UP,myEnum.RISING_HAMMER_UP,myEnum.RISING_HAMMER_DWN,myEnum.RISING_ONLY_DWN] :
        #        if currentKline == 1:
        #            g_OrderSellOpenEvent.set()
        #            logger.info(u'开空 by kLine:{0}:{1},nextDoing:{2}'.format(lastKline, currentKline, nowStatus))
        #        else:
        #            g_OrderBuyOpenEvent.set()
        #            logger.info(u'开多 by kLine:{0}:{1},nowStatus:{2}'.format(lastKline, currentKline, nowStatus))

        g_LastKline = copy.deepcopy(contractKLineLst[idex])
        g_KlineSave.append(g_LastKline)
        
        #getLastState()
    else:
        g_KlineUpDwnSquence = 0
        logger.info(u' kLine:{0}'.format(contractKLineLst))
        for idex in range(len(contractKLineLst) - 1):
            currentKline = getUpOrDwn(contractKLineLst[idex])
            g_KlineUpDwnSquence = g_KlineUpDwnSquence << 1 | currentKline
            tempKline = copy.deepcopy(contractKLineLst[idex])
            if lastKline > currentKline: # 阳阴
                maxLine.append(tempKline)
            elif lastKline < currentKline: # 阴阳
                lowLine.append(tempKline)
            else: # ͬ保持不变
                pass
            lastKline = currentKline
            g_LastKline.clear()
            g_LastKline = copy.deepcopy(contractKLineLst[idex])
            g_halfOfLastKline = getHalfOfKline(contractKLineLst[idex])
            g_KlineSave.append(tempKline)

def getLastState():
    lastTwoKline = g_KlineUpDwnSquence & 0x3
    lenAll = len(g_KlineSave)
    is_Hammer = ishammer(g_KlineSave[lenAll-1])
    if lastTwoKline == 0 or lastTwoKline == 3:
        lastThrKline = g_KlineUpDwnSquence & 0x7
        if is_Hammer is myEnum.RISING_EQ_UP :
            if lastTwoKline == 0:
                g_OrderBuyOpenEvent.set() #开多
                logger.info(u'开多 by kLine:{0},{1}'.format(lastTwoKline, is_Hammer))
                if lastThrKline == 0:
                    g_OrderBuyOpenEvent.set() #开多
                    logger.info(u'开多 by kLine:{0},{1}'.format(lastTwoKline, is_Hammer))
        elif is_Hammer is myEnum.RISING_EQ_EQ:
            pass
        elif is_Hammer is myEnum.RISING_EQ_DWN:
            if lastTwoKline == 3:
                g_OrderSellOpenEvent.set() #开空
                logger.info(u'开空 by kLine:{0},{1}'.format(lastTwoKline, is_Hammer))
                if lastThrKline == 7:
                    g_OrderBuyOpenEvent.set() #开多
                    logger.info(u'开多 by kLine:{0},{1}'.format(lastTwoKline, is_Hammer))
        
    else: # 2
        if is_Hammer is None:
            pass
        elif is_Hammer is myEnum.RISING_ONLY_DWN.value or is_Hammer is myEnum.RISING_ONLY_UP.value\
          or is_Hammer is myEnum.RISING_HAMMER_DWN.value or is_Hammer is myEnum.RISING_HAMMER_UP.value:
            if lastTwoKline == 1:
                g_OrderBuyOpenEvent.set() #开多
                logger.info(u'开多 by kLine:{0},{1}'.format(lastTwoKline, is_Hammer))
            else:
                g_OrderSellOpenEvent.set() #开空
                logger.info(u'开空 by kLine:{0},{1}'.format(lastTwoKline, is_Hammer))


def testdataDecodeFromNet():
    global g_KlineUpDwnSquence
    global g_PrintFlag
    g_PrintFlag = False
    inputdata = [\
        {'amount': 17137.364187577074, 'close': 314.737, 'count': 3028, 'high': 317.259, 'id': 1569121200, 'low': 314.126, 'open': 317.144, 'vol': 540888}, \
        {'amount': 17796.991253268166, 'close': 315.697, 'count': 2957, 'high': 316.081, 'id': 1569124800, 'low': 313.673, 'open': 314.738, 'vol': 560246}, \
        {'amount': 13152.020335745643, 'close': 317.092, 'count': 2361, 'high': 318.04, 'id': 1569128400, 'low': 315.174, 'open': 315.71, 'vol': 416880}, \
        {'amount': 8614.527755853285, 'close': 315.642, 'count': 1422, 'high': 317.356, 'id': 1569132000, 'low': 315.091, 'open': 317.031, 'vol': 272368}, \
        {'amount': 12063.814470932364, 'close': 317.906, 'count': 1993, 'high': 318.482, 'id': 1569135600, 'low': 315.461, 'open': 315.508, 'vol': 383192}]
    g_KlineUpDwnSquence = g_KlineUpDwnSquence
    dataDecodeFromNet(inputdata)

    testCase("g_KlineUpDwnSquence by dataDecodeFromNet",g_KlineUpDwnSquence ,0x6)

    inputdata = [\
        {'amount': 17137.364187577074, 'close': 314.737, 'count': 3028, 'high': 317.259, 'id': 1569121200, 'low': 314.126, 'open': 317.144, 'vol': 540888}, \
        {'amount': 17796.991253268166, 'close': 315.697, 'count': 2957, 'high': 316.081, 'id': 1569124800, 'low': 313.673, 'open': 314.738, 'vol': 560246}, \
        {'amount': 13152.020335745643, 'close': 317.092, 'count': 2361, 'high': 318.04, 'id': 1569128400, 'low': 315.174, 'open': 315.71, 'vol': 416880}, \
        {'amount': 8614.527755853285, 'close': 315.642, 'count': 1422, 'high': 317.356, 'id': 1569132000, 'low': 315.091, 'open': 317.031, 'vol': 272368}, \
        {'amount': 12063.814470932364, 'close': 317.906, 'count': 1993, 'high': 318.482, 'id': 1569135600, 'low': 315.461, 'open': 315.508, 'vol': 383192},\
        {'amount': 12063.814470932364, 'close': 317.906, 'count': 1993, 'high': 318.482, 'id': 1569135600, 'low': 315.461, 'open': 317.906, 'vol': 383192}]
    dataDecodeFromNet(inputdata)
    testCase("g_KlineUpDwnSquence by dataDecodeFromNet",g_KlineUpDwnSquence ,0xD)
