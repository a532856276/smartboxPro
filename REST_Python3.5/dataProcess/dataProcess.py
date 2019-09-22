#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataProcess.JudgeData import *
from queue import Queue  # LILO????

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
def doNothing():
    pass


# 相当于 getUpDwnSquence
def dataDecodeFromNet(contractKLineLst):
    # {'amount': 50414.6651812045, 'close': 263.537, 'count': 8355, 'high': 265.5, 'id': 1560524400,
    #       'low': 263.2, 'open': 264.461, 'vol': 1332474}
    # 最新数据在list最后
    global maxLine
    global lowLine
    global g_KlineUpDwnSquence
    global g_PrintFlag
    print('begin contractKLineLst:')
    if g_PrintFlag == True:
        print(u'入参：获取到的KLine：{0}'.format(contractKLineLst))
    #getUpDwnSquence(contractKLineLst);

    currentKline = 0
    lastKline = 0

    if len(maxLine) and len(lowLine):
        lastKline = g_KlineUpDwnSquence & 0x1
        currentKline = getUpOrDwn(contractKLineLst[0])
        g_KlineUpDwnSquence = g_KlineUpDwnSquence | currentKline<<idex
        if lastKline > currentKline: # 阳阴
            maxLine.append(contractKLineLst[idex])
        elif lastKline < currentKline: # 阴阳
            lowLine.append(contractKLineLst[idex])
        else: # ͬ保持不变
            pass
        
    else:
        g_KlineUpDwnSquence = 0
        for idex in range(len(contractKLineLst)):
            currentKline = getUpOrDwn(contractKLineLst[idex])
            g_KlineUpDwnSquence = g_KlineUpDwnSquence | currentKline<<idex
            if lastKline > currentKline: # 阳阴
                maxLine.append(contractKLineLst[idex])
            elif lastKline < currentKline: # 阴阳
                lowLine.append(contractKLineLst[idex])
            else: # ͬ保持不变
                pass
            lastKline = currentKline
    
    if g_PrintFlag == True:
        print("g_KlineUpDwnSquence:0x%x"%g_KlineUpDwnSquence)
        print(u'出参：计算后：g_KlineUpDwnSquence{0},maxLine{1}, lowLine{2}'.format(g_KlineUpDwnSquence,maxLine, lowLine))
    print('end KlineQue:')


def testdataDecodeFromNet():
    inputdata = [{'amount': 1501.942292389007, 'close': 322.022, 'count': 603, 'high': 322.527, 'id': 1569096000, 'low': 321.864, 'open': 322.322, 'vol': 48400}, \
        {'amount': 888.0411955957943, 'close': 322.227, 'count': 290, 'high': 322.39, 'id': 1569099600, 'low': 321.8, 'open': 322.123, 'vol': 28608}, \
        {'amount': 3264.078831795959, 'close': 322.24, 'count': 1148, 'high': 322.857, 'id': 1569103200, 'low': 321.073, 'open': 322.353, 'vol': 105126}, \
        {'amount': 4812.538411915699, 'close': 322.693, 'count': 1194, 'high': 323.809, 'id': 1569106800, 'low': 322.206, 'open': 322.376, 'vol': 155538}, \
        {'amount': 8185.894636931124, 'close': 321.235, 'count': 1464, 'high': 323.01, 'id': 1569110400, 'low': 320.96, 'open': 322.694, 'vol': 263242}, \
        {'amount': 76777.80128122136, 'close': 316.449, 'count': 9193, 'high': 321.336, 'id': 1569114000, 'low': 313, 'open': 321.234, 'vol': 2430996}, \
        {'amount': 17193.1389445341, 'close': 317.144, 'count': 2602, 'high': 318.175, 'id': 1569117600, 'low': 314.888, 'open': 316.254, 'vol': 544668}, \
        {'amount': 17137.364187577074, 'close': 314.737, 'count': 3028, 'high': 317.259, 'id': 1569121200, 'low': 314.126, 'open': 317.144, 'vol': 540888}, \
        {'amount': 17796.991253268166, 'close': 315.697, 'count': 2957, 'high': 316.081, 'id': 1569124800, 'low': 313.673, 'open': 314.738, 'vol': 560246}, \
        {'amount': 13152.020335745643, 'close': 317.092, 'count': 2361, 'high': 318.04, 'id': 1569128400, 'low': 315.174, 'open': 315.71, 'vol': 416880}, \
        {'amount': 8614.527755853285, 'close': 315.642, 'count': 1422, 'high': 317.356, 'id': 1569132000, 'low': 315.091, 'open': 317.031, 'vol': 272368}, \
        {'amount': 12063.814470932364, 'close': 317.906, 'count': 1993, 'high': 318.482, 'id': 1569135600, 'low': 315.461, 'open': 315.508, 'vol': 383192}, \
        {'amount': 16373.879613046445, 'close': 317.712, 'count': 2588, 'high': 320, 'id': 1569139200, 'low': 317.5, 'open': 317.915, 'vol': 521812}, \
        {'amount': 6921.5254447599555, 'close': 318.592, 'count': 1634, 'high': 318.592, 'id': 1569142800, 'low': 316.555, 'open': 317.713, 'vol': 219768}, \
        {'amount': 8274.465069808428, 'close': 316.8, 'count': 1470, 'high': 318.799, 'id': 1569146400, 'low': 316.8, 'open': 318.593, 'vol': 262818}, \
        {'amount': 6379.880079680207, 'close': 317.467, 'count': 1344, 'high': 317.898, 'id': 1569150000, 'low': 316.203, 'open': 316.8, 'vol': 202510}, \
        {'amount': 6920.640048450254, 'close': 318.122, 'count': 1443, 'high': 318.85, 'id': 1569153600, 'low': 317.43, 'open': 317.527, 'vol': 220186}, \
        {'amount': 13495.426031742722, 'close': 316.582, 'count': 2235, 'high': 319.198, 'id': 1569157200, 'low': 315.682, 'open': 318.121, 'vol': 427812}, \
        {'amount': 8482.00525511388, 'close': 317.37, 'count': 1764, 'high': 317.512, 'id': 1569160800, 'low': 315.282, 'open': 316.581, 'vol': 268394}, \
        {'amount': 2123.1893200035033, 'close': 317.136, 'count': 401, 'high': 317.5, 'id': 1569164400, 'low': 316.909, 'open': 317.37, 'vol': 67350}]

    dataDecodeFromNet(inputdata)

    global maxLine
    global lowLine
    global g_KlineUpDwnSquence
    global g_PrintFlag

    pass