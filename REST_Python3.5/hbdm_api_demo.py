#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 15:48:13 2018

@author: zhaobo
"""
import time
# import datetime
# import json
import threading
from HuobiDMService import HuobiDM
from pprint import pprint
from OrderInfo import OrderInfo
import csv
from queue import Queue  # LILO队列
import math  # 先导入math模块
from dataProcess.dataProcess import *
from dataProcess.mycommondef import *

g_RebootFlag = True

FIXOPENPROFIT = 0.0005  # 持仓利润
FIXCLOSEPROFIT = -0.0001  # 持仓利润
# a1 = 3.4
# a2 = 3.6
# a1 = math.ceil(a1)
# a2 = math.ceil(a2)
# print(a1)
# print(a2)
# 输出：
# 4
# 4
# 向上取整

# 加入日志
#import logging
#logger = logging.getLogger(__name__)
#logger.setLevel(level = logging.INFO)
#handler = logging.FileHandler("log20190928135728.txt")
#handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s %(name)s:[%(levelname)s]%(message)s')
#formatter = logging.Formatter('%(asctime)s [%(levelname)s]%(message)s')
#handler.setFormatter(formatter)
#logger.addHandler(handler)

# logger.info("Start print log")
# logger.debug("Do something")
# logger.warning("Something maybe fail.")
# logger.info("Finish")


# 创建一定时器，定时查询k线
from MyTimer import MyTimer


# q = Queue() #创建队列对象
# q.put(0)    #在队列尾部插入元素
# q.put(1)
# q.put(2)
# print('LILO队列',q.queue)  #查看队列中的所有元素
# print(q.get())  #返回并删除队列头部元素
# print(q.queue)

KlineQueue = Queue()
#### input huobi dm url
##"https://api.hbdm.com"如果无法访问请使用："https://api.btcgateway.pro"。
urlList = ['https://api.hbdm.com', 'https://api.btcgateway.pro']
URL = urlList[1]
#URL = 'https://api.hbdm.com'

PROCEEMODE = 1 # 0 - AI; 1 - process By User
####  input your access_key and secret_key below:
# ACCESS_KEY = '0409a0a7-a07c0d0a-frbghq7rnm-f4a63'
# SECRET_KEY = 'f29359de-332fad6e-d1221b3d-aa55c'
ACCESS_KEY = '299beddf-ur2fg6h2gf-47175577-46461'
SECRET_KEY = '0f7f9c71-6fdbd114-e57f58ce-6d9a5'
g_symbol = "BTC"
# this_week(当周) next_week(下周) quarter(季度)
g_ContractType = "quarter"
g_ContractCode = ""

dm = HuobiDM(URL, ACCESS_KEY, SECRET_KEY)
g_UpDownDir = 0
# 订单id，自己维护发送给火币
g_OrderId = 0
g_ContractOpt = 0  # 合约操作方法
g_ContractOrderVolume = 0  # 交易量，几个任务都是顺序执行，暂不需要线程同步，以后考虑同步问题

lineQueue = Queue()  # 存储最近10次的变换方向

g_ContractBuyInfo = OrderInfo()  # 多头订单信息
g_ContractSellInfo = OrderInfo()  # 空头订单信息

g_ContractProcessPercent = [0, 1, 2, 3, 3, 6, 8, 8, 9, 9, 10]  # 不同的数字是需要处理不同的百分比




#### another account:
# dm2 = HuobiDM(URL, "ANOTHER ACCOUNT's ACCESS_KEY", "ANOTHER ACCOUNT's SECRET_KEY")


# %%  market data api ===============

def PrintTime(timeStamp):
    timeArray = time.localtime(float(timeStamp / 1000))
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    print(otherStyleTime)


def GetContractInfo(contractType=g_ContractType):
    '''
    :param contractType: this_week(当周) next_week(下周) quarter(季度)
    :return:
        Ture -- 可以进行交易
        False -- 暂停交易
    '''
    print(u' 获取合约信息 ')
    res = dm.get_contract_info(symbol=g_symbol, contract_type=contractType)
    statues = res["status"]
    if statues != "ok":
        return False

    timeStamp = res['ts']
    data = res['data']
    deadData = data[0]["delivery_date"]
    timeArray = time.localtime(float(timeStamp / 1000))
    otherStyleTime = time.strftime("%Y%m%d", timeArray)
    global g_ContractCode
    g_ContractCode = data[0]["contract_code"]
    print("今天日期为：", otherStyleTime)
    print("交割日期为：", deadData)
    if int(deadData) == int(otherStyleTime):
        # 交割日暂时不交易
        return False
    else:
        print("未到交割日期：", deadData)
        return True

    # dt1 = datetime.datetime.fromtimestamp(float(ts))
    # print(type(dt1), dt1)
    # pprint (dm.get_contract_info(contract_code="BTC181228"))


def GetContractIndex(symbol=g_symbol):
    print(u' 获取合约指数信息 ')
    pprint(dm.get_contract_index(symbol))


def GetContractPriceLimit(contractType='quarter'):
    print(u' 获取合约最高限价和最低限价 ')
    pprint(dm.get_contract_price_limit(symbol=g_symbol, contract_type=contractType))
    # pprint (dm.get_contract_price_limit(contract_code='BTC181228'))


def GetTotalVolume(contractType="quarter"):
    print(u' 获取当前可用合约总持仓量 ')
    pprint(dm.get_contract_open_interest(symbol=g_symbol, contract_type=contractType))
    # pprint (dm.get_contract_open_interest(contract_code='BTC181228'))


def GetComtractDepth(symbol='%s%s' % (g_symbol, "_CQ"), type='step0'):
    print(u' 获取行情深度数据 ')
    print("如\"BTC_CW\"表示BTC当周合约，\"BTC_NW\"表示BTC次周合约，\"BTC_CQ\表示BTC季度合约")
    print(symbol)
    print(type)
    pprint(dm.get_contract_depth(symbol=symbol, type=type))


g_LastKlinOpenPrice = 0

def GetContractKlineTime(symbol='%s%s' % (g_symbol, "_CQ"), timeLine="15min"):
    #print(u' 获取K线数据 ')
    # pprint (dm.get_contract_kline(symbol=symbol, period=timeLine, size=20))
    getSize = 1
    return dm.get_contract_kline(symbol=symbol, period=timeLine, size=getSize)


def GetContractKline(symbol='%s%s' % (g_symbol, "_CQ"), timeLine="15min"):
    print(u' 获取K线数据 ')
    getSize = 20
    global g_RebootFlag
    if g_RebootFlag is True:
        getSize = 20
        g_RebootFlag = False
    else:
        getSize = 2
    res = dm.get_contract_kline(symbol=symbol, period=timeLine, size=getSize)

    if getSize == 20:
        print(res)

    if res['status'] is 'fail':
        print("get Kline Error")
        g_RebootFlag = True
        return False
    if PROCEEMODE == 1:
        dataDecodeFromNet(res["data"])
    else:
        DataDecode(res["data"])
    return True
    


def GetContractMarketMerged(symbol='%s%s' % (g_symbol, "_CQ")):
    print(u'GetContractMarketMerged 获取聚合行情\r\n')
    return dm.get_contract_market_merged(symbol)
    # pprint(dm.get_contract_market_merged(symbol))


def GetContractTradeLast(symbol='%s%s' % (g_symbol, "_CQ")):
    print(u' 获取市场最近成交记录 ')
    print(symbol)
    pprint(dm.get_contract_trade(symbol))


def GetContractBatchTradeLast(symbol='%s%s' % (g_symbol, "_CQ")):
    print(u' 批量获取最近的交易记录 ')
    print(symbol)
    pprint(dm.get_contract_batch_trade(symbol=symbol, size=3))


# %% trade / account api  ===============

def GetContractAccountInfo(symbol=g_symbol):
    print(u' 获取用户账户信息 ')
    # pprint (dm.get_contract_account_info())
    pprint(dm.get_contract_account_info(symbol))


def GetContractPositionInfo(symbol=g_symbol):
    print(u' 获取用户持仓信息 ')
    # pprint (dm.get_contract_position_info())
    return dm.get_contract_position_info(symbol=symbol)


def GetContractPositionInfoNew(symbol=g_symbol):
    print(u' 获取用户持仓信息New ')
    return dm.get_contract_position_info(symbol=symbol)

# 开平方向
# 开多：买入开多(direction用buy、offset用open)
# 平多：卖出平多(direction用sell、offset用close)
# 开空：卖出开空(direction用sell、offset用open)
# 平空：买入平空(direction用buy、offset用close)
def SendContractOrder(symbol=g_symbol, contract_type=g_ContractType, contract_code=g_ContractCode,
                      client_order_id=g_OrderId, price=282, volume=1, direction='sell',
                      offset='open', lever_rate=20, order_price_type='limit'):
    """
            :symbol: "BTC","ETH"..
            :contract_type: "this_week", "next_week", "quarter"
            :contract_code: "BTC181228"
            :client_order_id: 客户自己填写和维护，这次一定要大于上一次
            :price             必填   价格
            :volume            必填  委托数量（张）
            :direction         必填  "buy" "sell"
            :offset            必填   "open", "close"
            :lever_rate        必填  杠杆倍数
            :order_price_type  必填   "limit"限价， "opponent" 对手价
            备注：如果contract_code填了值，那就按照contract_code去下单，如果contract_code没有填值，则按照symbol+contract_type去下单。
            :
            """
    print(u' 合约下单:direction:{0} offset:{1} volume:{2}'.format(direction, offset, volume))
    return dm.send_contract_order(symbol=symbol, contract_type=contract_type, contract_code=contract_code,
                                  client_order_id=client_order_id, price=price, volume=volume, direction=direction,
                                  offset=offset, lever_rate=lever_rate, order_price_type=order_price_type)


# print (u' 合约批量下单 ')
# orders_data = {'orders_data': [
#                {'symbol': 'BTC', 'contract_type': 'quarter',
#                 'contract_code':'BTC181228',  'client_order_id':'',
#                 'price':10000, 'volume':1, 'direction':'sell', 'offset':'open',
#                 'leverRate':5, 'orderPriceType':'limit'},
#                {'symbol': 'BTC','contract_type': 'quarter',
#                 'contract_code':'BTC181228', 'client_order_id':'',
#                 'price':20000, 'volume':2, 'direction':'sell', 'offset':'open',
#                 'leverRate':5, 'orderPriceType':'limit'}]}
# pprint(dm.send_contract_batchorder(orders_data))

# print (u' 撤销订单 ')
# pprint(dm.cancel_contract_order(symbol='BTC', order_id='42652161'))
#
def Cancel_All_Contract_order():
    print(u' 全部撤单 ')
    pprint(dm.cancel_all_contract_order(symbol=g_symbol))
#
# print (u' 获取合约订单信息 ')
# pprint(dm.get_contract_order_info(symbol='BTC', order_id='42652161'))
#
# print (u' 获取合约订单明细信息 ')
# pprint(dm.get_contract_order_detail(symbol='BTC', order_id='42652161', order_type=1, created_at=1542097630215))
#
# print (u' 获取合约当前未成交委托 ')
# pprint(dm.get_contract_open_orders(symbol='BTC'))
#
# print (u' 获取合约历史委托 ')
# pprint (dm.get_contract_history_orders(symbol='BTC', trade_type=0, type=1, status=0, create_date=7))
g_csvFileOpen = False


def DataDecode(contractKLineLst):
    # {'amount': 50414.6651812045, 'close': 263.537, 'count': 8355, 'high': 265.5, 'id': 1560524400,
    #       'low': 263.2, 'open': 264.461, 'vol': 1332474}
    # lst 的遍历方法如下
    # 方法2
    # for i in range(len(list)):
    #     print("序号：%s   值：%s" % (i + 1, list[i]))
    # # 方法3
    # print'\n遍历列表方法3：'
    # for i, val in enumerate(list):
    #     print("序号：%s   值：%s" % (i + 1, val))
    outFile = open('Price.csv','a+',newline='')
    csv_writer = csv.writer(outFile,dialect='excel')
    global g_csvFileOpen
    if not g_csvFileOpen:
        csv_Title = ['amount', 'High','Low','Open', 'Close','count','vol','id']
        csv_writer.writerow(csv_Title)
        g_csvFileOpen = True

    tmpLst = []
    for i, temp in enumerate(contractKLineLst):
        tmpLst.clear()
        tmpLst.append(temp['amount'])
        tmpLst.append(temp['high'])
        tmpLst.append(temp['low'])
        tmpLst.append(temp['open'])
        tmpLst.append(temp['close'])
        tmpLst.append(temp['count'])
        tmpLst.append(temp['vol'])
        tmpLst.append(temp['id'])
        csv_writer.writerow(tmpLst)
        print(tmpLst)
        # low = temp['low']
        # print(low)
        # openPrice = float(temp['open'])
        # global g_LastKlinOpenPrice
        # g_LastKlinOpenPrice = openPrice
        # closePrice = float(temp['close'])
        # if openPrice >= closePrice:
        #     KlineQueue.put(-1 * (openPrice - closePrice))  # 阴
        # else:
        #     KlineQueue.put(1 * (closePrice - openPrice))  # 阳

    outFile.close()
    print('KlineQue:')
    # print(KlineQueue.get())
    # print(KlineQueue.queue)
    print('end KlineQue:')


g_lastPrice = 0
g_HiPrice = 0
# q = Queue() #创建队列对象
# q.put(0)    #在队列尾部插入元素
# q.put(1)
# q.put(2)
# print('LILO队列',q.queue)  #查看队列中的所有元素
# print(q.get())  #返回并删除队列头部元素
# print(q.queue)
lineQueueThree = Queue()
g_ContractOptThree = 0
g_maxBuyPrice = 0
g_maxSellPrice = 0


def LineQueueThree(newStatus):
    contract_opt_temp = 0
    multiple = 1
    if lineQueueThree.empty() is not True:
        print(lineQueueThree.queue)

    if lineQueueThree.qsize() == 3:
        # print(lineQueueThree.queue)
        sellDir = newStatus - lineQueueThree.get()
        if sellDir >= 3 or sellDir <= -3:
            # 清除队列中的数据，防止二次命令
            lineQueueThree.get()
            lineQueueThree.get()
            contract_opt_temp = sellDir * multiple
            # print(u'买入方向：{0} {1}'.format(sellDir, contract_opt_temp))

    lineQueueThree.put(newStatus)

    orderOptThreadLock.acquire()  # 获取线程价格锁
    global g_ContractOptThree
    g_ContractOptThree = g_ContractOptThree + contract_opt_temp
    orderOptThreadLock.release()  # 释放线程锁
    g_OrderProcessByOptEvent.set()
    if contract_opt_temp:
        print(u'操作方法：LineQueueThree -- {0}'.format(contract_opt_temp))
    return contract_opt_temp


def LineQueueTen(newStatus, LineQueueThreeStatus):
    if LineQueueThreeStatus:
        lineQueue.get()  # 取走一个数
        lineQueue.put(newStatus)  # 放入一个数据
        return

    contract_opt_temp = 0
    if lineQueue.qsize() == 10:
        print(lineQueue.queue)
        sell_dir = newStatus - lineQueue.get()
        if sell_dir >= 5 or sell_dir <= -5:  # 如果是5 快速变换
            # 如果价格跳动比较大，则大于10，买入开仓，小于-10 卖出开仓
            lineQueue.get()  # 拿到两个数据，防止连操作
            lineQueue.get()  # 拿到两个数据，防止连操作
            contract_opt_temp = sell_dir

    lineQueue.put(newStatus)
    orderOptThreadLock.acquire()  # 获取线程价格锁
    global g_ContractOpt
    g_ContractOpt = g_ContractOpt + contract_opt_temp
    orderOptThreadLock.release()  # 释放线程锁
    g_OrderProcessByOptEvent.set()

    if contract_opt_temp:
        print(u'操作方法：LineQueueTen -- {0}'.format(contract_opt_temp))


g_ContractBuyProfit = 0
g_ContractSellProfit = 0


# 前后两次的价差，如果价差太小则不进行平空或者平多
g_diffPrice = 0.2
g_diffPrice2 = -0.2
g_diffPriceMax = 0.6
g_diffPriceMin = -0.6
g_UpCnt= 0
g_DuwCnt= 0


def OrderOperateByUpDown(diffPrice):
    global g_UpCnt, g_DuwCnt,g_ContractBuyProfit, g_ContractSellProfit
    if g_UpCnt >= 4 or diffPrice >= g_diffPriceMax:
        if g_ContractBuyProfit > 0.0002:
            g_OrderSellCloseEvent.set()  # 平多
        g_OrderSellOpenEvent.set()  # 开空
        g_UpCnt = 0
    elif diffPrice >= g_diffPrice:
        g_OrderBuyOpenEvent.set()  # 开多


    if g_DuwCnt >= 4 or diffPrice <= g_diffPriceMin:
        if g_ContractSellProfit > 0.0002:
            g_OrderBuyCloseEvent.set()  # 平空
        g_OrderBuyOpenEvent.set()  # 开多
        g_DuwCnt = 0
    elif diffPrice <= g_diffPrice2:
        g_OrderSellOpenEvent.set()  # 开空


# 价格比较是， 传入最新价格
def OrderByMarket(nowPrice):
    new_price = float(nowPrice)
    global g_lastPrice, g_UpDownDir,g_UpCnt,g_DuwCnt
    global g_ContractBuyProfit, g_ContractSellProfit
    if g_lastPrice == 0:
        g_lastPrice = new_price

    try:
        if new_price > g_lastPrice:
            diff = new_price - g_lastPrice
            g_UpDownDir = g_UpDownDir + 1
            logger.info(u'new_price({0}) > g_lastPrice({1}) '
                        u'dff {2} > ({3})g_UpDownDir ({4}) g_ContractBuyProfit({5})'.format(new_price,
                                                                                            g_lastPrice,
                                                                                            diff,
                                                                                            g_diffPrice,
                                                                                            g_UpDownDir,
                                                                                            g_ContractBuyProfit))
            # if diff >= g_diffPrice and g_ContractBuyProfit >= 0:
            #     # g_OrderBuyCloseEvent.set()  # 平空
            #     g_OrderBuyOpenEvent.set()  # 开多

            OrderOperateByUpDown(diff)
            g_DuwCnt = 0
            g_UpCnt = g_UpCnt + 1

        elif new_price < g_lastPrice:
            g_UpDownDir = g_UpDownDir - 1
            diff = new_price - g_lastPrice
            logger.info(u'new_price({0}) < g_lastPrice({1}) dff {2} g_diffPrice({3}) '
                        u'g_UpDownDir ({4}) g_ContractSellProfit({5})'.format(new_price,
                                                                              g_lastPrice,
                                                                              diff,
                                                                              g_diffPrice,
                                                                              g_UpDownDir,
                                                                              g_ContractSellProfit))
            # if diff >= g_diffPrice and g_ContractSellProfit >= 0:
            #     # g_OrderSellCloseEvent.set()  # 平多
            #     g_OrderSellOpenEvent.set()  # 开空

            OrderOperateByUpDown(diff)
            g_UpCnt = 0
            g_DuwCnt = g_DuwCnt + 1
        else:
            print(u'价格没有变化')
        # res = LineQueueThree(new_price, g_UpDownDir, contract_buy_price, contract_sell_price)
        # res = LineQueueThree(g_UpDownDir)
        # LineQueueTen(g_UpDownDir, res)
        g_lastPrice = new_price
        # print(u'LatPrice {0} 成交量:{1}'.format(g_lastPrice, float(nowMarket['amount'])))
    except ZeroDivisionError as e:
        print(e.message)

def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    # print(time_stamp)
    stamp = ("".join(time_stamp.split()[0].split("-")) + "".join(time_stamp.split()[1].split(":"))).replace('.', '')
    print(stamp)


# g_ContractOpt 说明： 正负号代表买卖方向， 正： 买入   负： 卖出
#                      数值代表开平仓       1： 开仓    2 ：平仓
#                      组合方式如下：      2    买入平仓
#                                          1    买入开仓
#                                          -1   卖出开仓
#                                          -2   卖出平仓
# 查询订单信息
def ContractOrderInfo():
    res = 0
    contractPositionInfo = GetContractPositionInfo()
    if contractPositionInfo is None or contractPositionInfo["status"] != "ok":
        print(u'ContractOrderInfo 查询订单失败 {0}'.format(contractPositionInfo))
        return res
    print(u'ContractOrderInfo 查询订单: {0}'.format(contractPositionInfo))

    global g_ContractBuyInfo, g_ContractSellInfo,g_ContractBuyProfit, g_ContractSellProfit
    global g_OrderBuyOpenPrice, g_OrderSellOpenPrice

    contractBuyInfoFlag= 0
    contractSellInfoFlag = 0
    for value in contractPositionInfo["data"]:
        # print(value)
        if value['direction'] == "buy":
            orderPriceThreadLock.acquire()  # 获取线程价格锁
            g_ContractBuyInfo.setValue(value['volume'], value['available'], value['cost_open'], value['profit'])
            g_OrderBuyOpenPrice = value['cost_open']
            orderPriceThreadLock.release()  # 释放线程锁
            contractBuyInfoFlag = 1
            g_ContractBuyProfit = value['profit']
            if g_ContractBuyProfit >= FIXOPENPROFIT or g_ContractBuyProfit <= FIXCLOSEPROFIT:
                g_OrderSellCloseEvent.set()  # 平多
                logger.info(u'多单利润B({0})'.format(g_ContractBuyProfit))
            # logger.info(u'多单利润A({0})'.format(value['profit']))
        if value['direction'] == "sell":
            orderPriceThreadLock.acquire()  # 获取线程价格锁
            # logger.info(u'空单利润A({0})'.format(value['profit']))
            g_ContractSellInfo.setValue(value['volume'], value['available'], value['cost_open'], value['profit'])
            g_OrderSellOpenPrice = value['cost_open']
            orderPriceThreadLock.release()  # 释放线程锁
            contractSellInfoFlag = 1
            g_ContractSellProfit = value['profit']
            # 空单利润
            if g_ContractSellProfit >= FIXOPENPROFIT or g_ContractSellProfit <= FIXCLOSEPROFIT:
                g_OrderBuyCloseEvent.set()  # 平空
                # logger.info(u'空单利润B({0})'.format(g_ContractSellProfit))

        res = value['last_price']

    if contractBuyInfoFlag == 0:
        orderPriceThreadLock.acquire()  # 获取线程价格锁
        # logger.info(u'多单利润({0})'.format(0))
        g_ContractBuyInfo.setValue()
        g_OrderBuyOpenPrice = 0
        orderPriceThreadLock.release()  # 释放线程锁
        g_ContractBuyProfit = 0

    if contractSellInfoFlag == 0:
        orderPriceThreadLock.acquire()  # 获取线程价格锁
        # logger.info(u'空单利润({0})'.format(0))
        g_ContractSellInfo.setValue()
        g_OrderSellOpenPrice = 0
        orderPriceThreadLock.release()  # 释放线程锁
        g_ContractSellProfit = 0

    return res




def OrderSetVolume(direction, volnumByPercent):
    global g_ContractOrderVolume, g_ContractSellInfo, g_ContractBuyInfo
    getProfit = 0
    if direction == u'平空':
        orderPriceThreadLock.acquire()  # 获取线程价格锁
        tempSellVolume = g_ContractSellInfo.GetAvailable()
        profit = g_ContractSellInfo.GetProfit()
        if profit >= FIXOPENPROFIT or profit <= FIXCLOSEPROFIT:
            getProfit = 1
            logger.info(u'平空获利 profit({0}[{1},{2}])'.format(profit, FIXCLOSEPROFIT, FIXOPENPROFIT))
        orderPriceThreadLock.release()  # 获取线程价格锁
        if getProfit == 1:
            tampVolume = tempSellVolume
        else:
            tampVolume = math.ceil(tempSellVolume * volnumByPercent / 100)  # 向上取整
        print(u'平空配置 数量：({0}/{1} profit{2})'.format(tampVolume, tempSellVolume, profit))
        logger.info(u'平空仓量 数量：({0}/{1} profit{2})'.format(tampVolume, tempSellVolume, profit))
    elif direction == u'平多':
        orderPriceThreadLock.acquire()  # 获取线程价格锁
        tempBuyVolmue = g_ContractBuyInfo.GetAvailable()
        profit = g_ContractBuyInfo.GetProfit()
        if profit >= FIXOPENPROFIT or profit <= FIXCLOSEPROFIT:
            getProfit = 1
            logger.info(u'平多获利 profit({0}[{1},{2}])'.format(profit, FIXCLOSEPROFIT, FIXOPENPROFIT))
        orderPriceThreadLock.release()  # 释放线程价格锁

        if getProfit == 1:
            tampVolume = tempBuyVolmue
        else:
            tampVolume = math.ceil(tempBuyVolmue * volnumByPercent / 100)  # 向上取整
        print(u'平多配置 数量：({0}/{1}:profit{2})'.format(tampVolume, tempBuyVolmue,profit))
        logger.info(u'平多仓量 数量：({0}/{1} profit{2})'.format(tampVolume, tempBuyVolmue, profit))
    # else:
    #     tampVolume = 0
    #
    # tampVolume = 1
    orderVolnumeThreadLock.acquire()
    g_ContractOrderVolume = tampVolume
    orderVolnumeThreadLock.release()
    return tampVolume


def OrderGetVolume():
    global g_ContractOrderVolume
    orderVolnumeThreadLock.acquire()
    temp = g_ContractOrderVolume
    orderVolnumeThreadLock.release()
    return temp


# 卖出开仓 -- 开空
def OrderSellOpenTread(args, kwargs):
    print(u'OrderBuyCloseTread 开空-交易线程 启动({0}-- {1})'.format(args, kwargs))
    OrderSellOpenTread.last = 0
    while 1:
        g_OrderSellOpenEvent.wait()
        g_OrderSellOpenEvent.clear()

        volume = 1
        if volume > 0:
            print(u'OrderSellOpenTread 开空命令：{0}'.format(volume))
            # logger.info(u'开空 执行成功！！！volume({0})price({1})'.format(volume, g_lastPrice))
            optResult = SendContractOrder(volume=volume, direction="sell", offset="open", order_price_type="opponent")
            if optResult is not None and optResult['status'] == "ok":
                print(u'开空命令：{0} 成功:optResult::{1}'.format(volume, optResult))
                logger.info(u'开空 执行成功！！！volume({0})volume({1})'.format(volume, volume))
                setOrderSellOpenFlag(True)
            else:
                print(u'开空命令：{0} 失败 optResult:({1})'.format(volume, optResult))
                logger.error(u'开空 执行失败！！！volume({0}), error message:{1}'.format(volume, optResult))
                setOrderSellOpenFlag(False)
        # 撤销未成交的订单
        # Cancel_All_Contract_order()


# 开多进程
def OrderBuyOpenTread(args, kwargs):
    print(u'OrderBuyCloseTread 开多-交易线程 启动 {0}, {1}'.format(args, kwargs))
    OrderBuyOpenTread.last = 0
    while 1:
        g_OrderBuyOpenEvent.wait()
        g_OrderBuyOpenEvent.clear()
        volume = 1
        if volume > 0:
            print(u'OrderSellOpenTread 开多命令：{0}'.format(volume))
            # logger.info(u'开多 执行成功！！！volume({0})price({1})'.format(volume, g_lastPrice))
            optResult = SendContractOrder(volume=volume, direction="buy", offset="open", order_price_type="opponent")
            if optResult is not None and optResult['status'] == "ok":
                setOrderBuyOpenFlag(True)
                print(u'开多命令：{0} 成功:{1}'.format(volume, optResult))
                logger.info(u'开多 执行成功！！！volume({0})volume({1})optResult({2})'.format(volume, volume, optResult))
            else:
                setOrderBuyOpenFlag(False)
                print(u'开多命令：({0})-- 失败 optResult:({1})'.format(volume, optResult))
                logger.error(u'开多 执行失败！！！volume({0}), error message:{1}'.format(volume, optResult))


def OrderSellCloseTread(args, kwargs):
    print(u'OrderSellCloseTread 平多-交易线程 启动')
    while 1:
        g_OrderSellCloseEvent.wait()
        g_OrderSellCloseEvent.clear()
        OrderSetVolume(u"平多", 100)  # 平多 30 %
        # print(u'OrderSellCloseTread 进入平多-交易线程')

        volume = int(OrderGetVolume())
        if volume > 0:
            opt_result = SendContractOrder(volume=volume, direction="sell",
                                           offset="close", order_price_type="opponent")
            if opt_result is not None and opt_result['status'] == "ok":
                setOrderBuyOpenFlag(False)
                print(u'OrderSellCloseTread 平多交易执行成功！！！volume({0})msg({1})'.format(volume, opt_result))
                logger.info(u'平多交易线程 执行成功！！！volume({0})optResult({1})'.format(volume, opt_result))
            else:
                opt_result = SendContractOrder(volume=volume, direction="sell",
                                           offset="close", order_price_type="opponent")
                logger.error(u'平多交易线程 执行失败！！！volume({0}), error message:{1}'.format(volume, opt_result))
        print(u'OrderSellCloseTread 退出平多-交易线程一次循环')

def sendBuyCloseCmd(volume):
    opt_result = SendContractOrder(volume=volume, direction="buy",
                                    offset="close", order_price_type="opponent")
    if opt_result is not None and opt_result['status'] == "ok":
        setOrderSellOpenFlag(False)
        print(u'OrderBuyCloseTread 平空交易线程 执行成功！！！volume({0})'.format(OrderGetVolume()))
        logger.info(u'平空交易线程 执行成功！！！volume({0})optResult({1})'.format(volume, opt_result))
        return True
    else:
        print(u'OrderBuyCloseTread 平空交易线程 执行失败！失败！！'
                u'失败！！！volume({0}) opt_result({1})'.format(OrderGetVolume(), opt_result))
        logger.error(u'平空交易线程 执行失败！！！volume({0}) error message:{1}'.format(volume, opt_result))
        return False
def OrderBuyCloseTread(args, kwargs):
    print(u'OrderBuyCloseTread 平空-交易线程 启动')
    while 1:
        g_OrderBuyCloseEvent.wait()
        g_OrderBuyCloseEvent.clear()
        OrderSetVolume(u"平空", 100)  # 平仓 30 %
        # print(u'OrderBuyCloseTread 进入平空--交易线程')
        volume = int(OrderGetVolume())
        if volume > 0 and sendBuyCloseCmd(volume) == False:
            sendBuyCloseCmd(volume)
        print(u'OrderBuyCloseTread 退出平空--交易线程一次循环')

def GetContraInfoTread(args, kwargs):
    while True:
        print(u'GetContraInfoTread 查询订单信息')
        g_GetContraInfoEvent.wait()
        g_GetContraInfoEvent.clear()
        OrderSetVolume(u"平空", 30)  # 平仓 30 %
        # print(u'OrderBuyCloseTread 进入平空--交易线程')
        ContractOrderInfo()
        print(u'OrderBuyCloseTread 退出平空--交易线程一次循环')

#if __name__ == "__main__":
def test():
    # print("hello world")
    # logger.info(u'交易开始！！！')
    print(u"启动定时器查询k线")
    g_QueryKline = MyTimer(GetContractKline, 5, 1)

    if GetContractInfo(contractType=g_ContractType):  # this_week(当周) next_week(下周) quarter(季度)
        print(g_ContractCode)
        GetContractIndex(symbol=g_symbol)  # 获取合约指数，暂时不知何用
        # 获取市场最近成交记录
        GetComtractDepth(type="step4")
        # GetComtractDepth(type = "step5")
        # GetContractKline()

    #     count = 0
    #     tLast = 0
    #    orderPriceThreadLock = threading.Lock()  # 创建订单价格线程锁
    #    orderOptThreadLock = threading.Lock()  # 创建订单操作线程锁
    #    orderVolnumeThreadLock = threading.Lock()  # 创建订单操作线程锁
    #     # 开 4个线程，对应的触发是 g_xxxEvent 如 g_OrderBuyOpenEvent
    #     orderBuyOpenThread = threading.Thread(target=OrderBuyOpenTread, args={"OrderBuyOpenTread", 'OBuyOpenTread'})
    #     orderBuyOpenThread.start()
    #     orderSellOpenThread = threading.Thread(target=OrderSellOpenTread, args={"OrderSellOpenTread", 'OSellOpenTread'})
    #     orderSellOpenThread.start()
    #     orderBuyCloseThread = threading.Thread(target=OrderBuyCloseTread, args={"OrderBuyCloseTread", 'OrderTread1'})
    #     orderBuyCloseThread.start()
    #     orderSellCloseThread = threading.Thread(target=OrderSellCloseTread, args={"OrderSellCloseTread", 'OrderTread2'})
    #     orderSellCloseThread.start()
    #
    #     while 1:
    #         count = count + 1
    #         if count % 20 == 0:
    #             # 撤销未成交的订单
    #             Cancel_All_Contract_order()
    #
    #         t = time.time() * 1000
    #         print(u'采样时间差：{0}ms'.format(int(t - tLast)))
    #         tLast = t
    #
    #         positionRes = ContractOrderInfo()
    #         if positionRes == 0 or positionRes is None: # 表示没有订单
    #             marketToOrder = GetContractMarketMerged()  # 获取行情信息
    #             if marketToOrder is not None and marketToOrder['status'] == "ok":
    #                 tem = marketToOrder['tick']
    #                 positionRes = tem['close']
    #                 print(u'获取行情信息tem({0})'.format(tem))
    #                 print(u'获取行情信息positionRes({0})'.format(positionRes))
    #             else:
    #                 print(u'main: GetContractMarketMerged is error marketToOrder({0})'.format(marketToOrder))
    #
    #         OrderByMarket(positionRes)
    #
    # else:
    #     print("今天暂时不交易")

    print("end world")
