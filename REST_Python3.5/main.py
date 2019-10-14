#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hbdm_api_demo import *
from dataProcess.dataProcess import *
from dataProcess.mycommondef import *
import time
import threading

TestBign = False

g_BeginPrice = 5


def TestCase():
    testdataDecodeFromNet()


def ContractOrderInfoNew():
    res = 0
    contractPositionInfo = GetContractPositionInfoNew()
    if contractPositionInfo is None or contractPositionInfo["status"] != "ok":
        print(u'ContractOrderInfoNew 查询订单失败 {0}'.format(contractPositionInfo['msg']))
        time.sleep(1)
        return False
    # print(u'ContractOrderInfoNew 查询订单: {0}'.format(contractPositionInfo))
    global g_BuyMaxProfit, g_SellMaxProfit

    if len(contractPositionInfo["data"]) == 0:
        print(u'ContractOrderInfoNew 查询订单无数据')
        g_BuyMaxProfit = 0.0
        g_SellMaxProfit = 0.0
        return False
    contractBuyInfoFlag = 0
    contractSellInfoFlag = 0
    for value in contractPositionInfo["data"]:
        # print(value)
        if value['direction'] == "buy":
            orderPriceThreadLock.acquire()  # 获取线程价格锁
            g_ContractBuyInfo.setValue(value['volume'], value['available'], value['cost_open'], value['profit'])
            orderPriceThreadLock.release()  # 释放线程锁
            contractBuyInfoFlag = 1
            buyProfit = value['profit']
            if buyProfit < 0.0:
                g_BuyMaxProfit = 0
                if buyProfit <= FIXCLOSEPROFIT:
                    g_OrderSellCloseEvent.set()  # 平多
            else:
                if g_BuyMaxProfit == 0.0:
                    g_BuyMaxProfit = buyProfit
                else:
                    if buyProfit > g_BuyMaxProfit:
                        g_BuyMaxProfit = buyProfit
                    elif g_BuyMaxProfit * 0.92 >= buyProfit >= g_BuyMaxProfit * 0.5:
                        g_OrderSellCloseEvent.set()  # 平多
                        logger.info(u'多单利润 -- 需要平多')
            logger.info(u'多单利润A({0}/({1}))'.format(buyProfit, g_BuyMaxProfit))
        if value['direction'] == "sell":
            orderPriceThreadLock.acquire()  # 获取线程价格锁
            # logger.info(u'空单利润A({0})'.format(value['profit']))
            g_ContractSellInfo.setValue(value['volume'], value['available'], value['cost_open'], value['profit'])
            orderPriceThreadLock.release()  # 释放线程锁
            contractSellInfoFlag = 1
            sellProfit = value['profit']

            if sellProfit < 0.0:
                g_SellMaxProfit = 0
                if sellProfit <= FIXCLOSEPROFIT:
                    g_OrderBuyCloseEvent.set()  # 平空
            else:
                if g_SellMaxProfit == 0:
                    g_SellMaxProfit = sellProfit
                else:
                    if sellProfit > g_SellMaxProfit:
                        g_SellMaxProfit = sellProfit
                    elif g_SellMaxProfit * 0.92 >= sellProfit >= g_SellMaxProfit * 0.5:
                        g_OrderBuyCloseEvent.set()  # 平空
                        logger.info(u'空单利润---({0}/{1}) 减小需要平空'.format(sellProfit, g_SellMaxProfit))
                    else:
                        pass
            logger.info(u'空单利润B({0}/{1})'.format(sellProfit, g_SellMaxProfit))
    if contractBuyInfoFlag == 0:
        orderPriceThreadLock.acquire()  # 获取线程价格锁
        # logger.info(u'多单利润({0})'.format(0))
        g_ContractBuyInfo.setValue()
        orderPriceThreadLock.release()  # 释放线程锁
        g_BuyMaxProfit = 0

    if contractSellInfoFlag == 0:
        orderPriceThreadLock.acquire()  # 获取线程价格锁
        # logger.info(u'空单利润({0})'.format(0))
        g_ContractSellInfo.setValue()
        orderPriceThreadLock.release()  # 释放线程锁
        g_SellMaxProfit = 0
    return True


def GetContraInfoTreadNew(args, kwargs):
    while True:
        # print("GetContraInfoTreadNew...")
        res = ContractOrderInfoNew()
        if res is True:
            time.sleep(1)
        else:
            time.sleep(3)


def CreatOrderThread():
    print("CreatOrderThread")

    # 开 4个线程，对应的触发是 g_xxxEvent 如 g_OrderBuyOpenEvent
    orderBuyOpenThread = threading.Thread(target=OrderBuyOpenTread, args={"OrderBuyOpenTread", 'OBuyOpenTread'})
    orderBuyOpenThread.start()
    orderSellOpenThread = threading.Thread(target=OrderSellOpenTread, args={"OrderSellOpenTread", 'OSellOpenTread'})
    orderSellOpenThread.start()
    orderBuyCloseThread = threading.Thread(target=OrderBuyCloseTread, args={"OrderBuyCloseTread", 'OrderTread1'})
    orderBuyCloseThread.start()
    orderSellCloseThread = threading.Thread(target=OrderSellCloseTread, args={"OrderSellCloseTread", 'OrderTread2'})
    orderSellCloseThread.start()

    # 创建查询订单的任务
    # 使用说明：
    # 在需要查询处 执行 g_GetContraInfoEvent.set, 使用 g_ContractSellInfo 获取 空单信息，g_ContractBuyInfo 获取多单信息
    # GetContraInfoTread = threading.Thread(target=GetContraInfoTread, args={"GetContraInfoTread", 'GetContraInfoTread111'})
    GetContraInfoTread = threading.Thread(target=GetContraInfoTreadNew,
                                          args={"GetContraInfoTread", 'GetContraInfoTread111'})
    GetContraInfoTread.start()


def PriceProcess(newPrice):
    lenKline = len(g_KlineSave)
    state = getType(g_KlineSave[lenAll - 1], newPrice)
    pass


def Process(high, open, close, low):
    upValue = high - close
    if upValue == 0 and (high - low) >= 20:
        upFlag = True
        logger.info(u'上位 by upValue:{0},high({1})close:{2}'.format(upValue, tem['high'], tem['close']))
    if upFlag is True and upValue >= 15:
        upFlag = False
        g_OrderSellCloseEvent.set()  # 平多
        g_OrderSellOpenEvent.set()
        logger.info(u'开空 by upValue:{0},close:{1}'.format(upValue, tem['close']))


if __name__ == "__main__":

    if TestBign is True:
        TestCase()
    else:
        CreatOrderThread()
        g_QueryKline = MyTimer(GetContractKline, 15, True)
        # 启动定时任务，定时时间由入参决定
        g_QueryKline.start();

        if GetContractInfo(contractType=g_ContractType):  # this_week(当周) next_week(下周) quarter(季度)
            print(g_ContractCode)
            GetContractIndex(symbol=g_symbol)  # 获取合约指数，暂时不知何用

        upFlag = False
        dwnFlag = False
        maxLineIndex = 1
        lowLineIndex = 1
        lastKlineOpen = 0
        runcnt = 0
        lastBuyOpen = 0
        lastSellOpen = 0
        ContractOrderInfo()
        msgErrorCnt = 0
        global g_OrderBuyOpenPrice, g_OrderSellOpenPrice
        global g_OrderBuyOpenFlag, g_OrderSellOpenFlag
        buyMaxValue = 0
        sellMaxValue = 0
        GetContractKline()
        while True:
            runcnt = runcnt + 1
            print("main process {0}".format(runcnt))
            time.sleep(3)
            # continue

            # maxLen = len(maxLine)
            # lowLen = len(lowLine)
            # marketToOrder = GetContractMarketMerged()
            # print("{0}".format(marketToOrder))
            marketToOrder = GetContractKlineTime()
            if marketToOrder['status'] is 'fail':
                msgErrorCnt = msgErrorCnt + 1
                if msgErrorCnt >= 5:
                    time.sleep(1)
                print("main process getMsgErrorCnt {0}".format(msgErrorCnt))
                continue

            msgErrorCnt = 0

            if marketToOrder is not None and marketToOrder['status'] == "ok":
                if len(marketToOrder['data']) == 0:
                    print("main process data is NULL")
                    continue

                tem = marketToOrder['data'][0]

                g_halfOfLastKline = getHalf()
                if g_halfOfLastKline != 0.0:
                    if tem['open'] > g_halfOfLastKline:
                        if tem['close'] <= g_halfOfLastKline and g_OrderSellOpenFlag is False:
                            g_OrderSellOpenEvent.set()
                            logger.info(
                                u'开空 by g_halfOfLastKline:{0}>=close:{1}'.format(g_halfOfLastKline, tem['close']))
                    elif tem['open'] < g_halfOfLastKline:
                        if tem['close'] >= g_halfOfLastKline and g_OrderBuyOpenFlag is False:
                            g_OrderBuyOpenEvent.set()
                            logger.info(
                                u'开多  by g_halfOfLastKline:{0}<=close:{1}'.format(g_halfOfLastKline, tem['close']))

                # continue
                # 此处注意刚开盘时，数据量比较小，怎么判断最高和最低？？
                upValue = tem['high'] - tem['close']
                if upValue == 0 and tem['high'] - tem['low'] >= 20:
                    upFlag = True
                    logger.info(u'上顶 by upValue:{0},high({1})close:{2}'.format(upValue, tem['high'], tem['close']))
                if upFlag is True and upValue >= g_BeginPrice:
                    upFlag = False
                    g_OrderSellOpenEvent.set()
                    logger.info(u'开空 by upValue:{0},close:{1}'.format(upValue, tem['close']))
                    continue

                dwnValue = tem['close'] - tem['low']
                if dwnValue == 0 and tem['high'] - tem['low'] >= 20:
                    logger.info(u'下底 by tem_low:{0},dwnValue{1} close:{2}'.format(tem['low'], dwnValue, tem['close']))
                    dwnFlag = True
                if dwnFlag is True and dwnValue >= g_BeginPrice:
                    dwnFlag = False
                    g_OrderBuyOpenEvent.set()  # 买入开仓
                    logger.info(u'开多 by dwnValue:{0},close:{1}'.format(dwnValue, tem['close']))
                    continue

                # if maxLen != 0 and tem['close'] >= maxLine[maxLen - maxLineIndex]['close'] and maxLen != maxLineIndex:
                #    print("Kline will buy: close{0} >= maxLine[{0}]".format(tem['close'], maxLine[maxLen - maxLineIndex]['close']))
                #    g_OrderBuyOpenEvent.set() # 买入开仓
                #    maxLineIndex = maxLineIndex + 1
                #    if maxLineIndex >= maxLen:
                #        maxLineIndex = maxLen
                #    continue
                # if lowLen != 0 and tem['close'] <= lowLine[lowLen - lowLineIndex]['close'] and lowLineIndex != lowLen:
                #    print("Kline will Sell: close{0} <= lowLine[{1}] -->lowLen:{2} lowLineIndex:{3}".format(tem['close'], lowLine[lowLen - lowLineIndex]['close'], lowLen, lowLineIndex))
                #    g_OrderSellOpenEvent.set() # 卖出开仓
                #    lowLineIndex = lowLineIndex + 1
                #    if lowLineIndex >= lowLen:
                #        lowLineIndex = lowLen
                #    continue

                # lenKline = len(g_KlineSave)
                # if lenKline != 0:
                #    pass
                # state = getType(g_KlineSave[lenKline-1], newPrice)
                # if state ==0 or state == 3:
                #    pass
                # else:
                #    if state == 1:
                #        PriceProcess(positionRes)
            else:
                print(u'main: GetContractMarketMerged is error marketToOrder({0})'.format(marketToOrder))

            # OrderByMarket(positionRes)

            # time.sleep(3)
