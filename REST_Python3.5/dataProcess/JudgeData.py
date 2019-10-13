#!/usr/bin/env python
# -*- coding: utf-8 -*-

#注意:代码模板中的代码将会被复制到任何新创建的文件中，编辑代码模板中的代码，让他;帮你自动增加固定代码吧
#aaa = input("bbb:");
#print(aaa);
from dataProcess.myenum import *

data = [{"open":12345.67,"close":12357.66,"high":15555.67,"low":12356.66},{"open":12357.66,"close":12347.67,"high":15555.67,"low":12356.66},{"open":12347.67,"close":12337.66,"high":15500,"low":12300},{"open":12337.66,"close":12357.66,"high":15555.67,"low":12356.66}]

def risingHasFalling(high, close):
    if high - close >= 10:
        return myEnum.RISING_TO_FALLING10
    elif high - close >= 20:
        return myEnum.RISING_TO_FALLING20
    else:
        return myEnum.RISING_TO_FALLING30

def fallingHasRising(low, close):
    if close - low >= 10:
        return myEnum.FALLING_TO_RISING10
    elif close - low >= 20:
        return myEnun.FALLING_TO_RISING20
    else:
        return myEnum.FALLING_TO_RISING30

def ishammer(inputdata):
    #是否为锤子线
    upline = 0
    dwnline = 0
    modline = 0
    if inputdata['close'] > inputdata['open']:
        upline = inputdata['high']- inputdata['close']
        dwnline = inputdata['open'] - inputdata['low']
        modline = inputdata['close'] - inputdata['open']
    else:
        upline = inputdata['high'] - inputdata['open']
        dwnline = inputdata['close'] - inputdata['low']
        modline = inputdata['open'] - inputdata['close']
        
    print("para:up:{0},dwn:{1},mod:{2}".format(upline, dwnline, modline))
            
    if upline < 2 and (dwnline > modline or dwnline < modline/2):
        return myEnum.RISING_ONLY_DWN
    elif dwnline < 2 and (upline > modline or upline < modline/2):
        return myEnum.RISING_ONLY_UP
    elif upline < dwnline and dwnline > modline * 2:
        #判定为阳-锤子
        return myEnum.RISING_HAMMER_DWN.value
    elif upline > dwnline and upline > modline * 2:
        #判定为阳-倒锤子
        return myEnum.RISING_HAMMER_UP.value
    elif modline == 0 and upline > dwnline:
        return myEnum.RISING_EQ_UP
    elif modline == 0 and upline == dwnline:
        return myEnum.RISING_EQ_EQ
    elif modline == 0 and upline < dwnline:
        return myEnum.RISING_EQ_DWN
    else:
        return None
    #else:
    #    upline = inputdata['high'] - inputdata['open']
    #    dwnline = inputdata['close'] - inputdata['low']
    #    modline = inputdata['open'] - inputdata['close']
    #    
    #    if upline == 0 and dwnline < modline/2:
    #        return myEnum.FALLING_ONLY_DWN
    #    elif dwnline == 0 and upline < modline/2:
    #        return myEnum.FALLING_ONLY_UP
    #    elif upline < dwnline and modline != 0 and dwnline > modline * 2:
    #        return myEnum.FALLING_HAMMER_DWN.value
    #    elif upline > dwnline and modline != 0 and upline > modline * 2:
    #        return myEnum.FALLING_HAMMER_UP.value
    #    elif modline == 0 and upline > dwnline:
    #        return myEnum.RISING_EQ_UP
    #    elif modline == 0 and upline == dwnline:
    #        return myEnum.RISING_EQ_EQ
    #    elif modline == 0 and upline < dwnline:
    #        return myEnum.RISING_EQ_DWN
    #    else:
    #        return None
    
def getUpOrDwn(inputdata):
    if inputdata['close']> inputdata['open']:
        return 1
    else:
        return 0
        

def getHalfOfKline(inputdata):
    if inputdata['close'] < inputdata['open']:
        return (inputdata['open'] -  inputdata['close'] ) / 2 + inputdata['close'] 
    else:
        return (inputdata['close'] - inputdata['open']) / 2 + inputdata['open']


def getType(inputdata1, inputdata2):
    if getUpOrDwn(inputdata1) > getUpOrDwn(inputdata2):
        halfValue = (inputdata1['open'] + inputdata1['close']) / 2
        tempValue = inputdata1['close']
        
        if inputdata1['open'] <= inputdata2['close'] and inputdata1['close'] >= inputdata2['open']:
            # 阳 孕阴
            return myEnum.RISING_HAS_FALLING
        if inputdata1['open'] >= inputdata2['close'] and inputdata1['close'] <= inputdata2['open']:
            # 阴包阳
            return myEnum.RISING_IN_FALLING
        
        if inputdata2['close'] >= 0.99 * tempValue:
            return myEnum.RISING_TO_FALLING10

        if halfValue >= inputdata2['close']:
            return myEnum.RISING_TO_FALLING
    elif getUpOrDwn(inputdata1) < getUpOrDwn(inputdata2):
        halfValue = (inputdata1['open'] + inputdata1['close']) / 2
        
        if inputdata1['open'] >= inputdata2['close'] and inputdata1['close'] <= inputdata2['open']:
            #阴孕阳
            return myEnum.FALLING_HAS_RISING
        if inputdata1['open'] <= inputdata2['close'] and inputdata1['close'] >= inputdata2['open']:
            # 阳包阴
            return myEnum.FALLING_IN_RISING
        
        #if inputdata2['close'] >= 0.99 * tempValue:
            #return myEnum.RISING_TO_FALLING10

        if halfValue <= inputdata2['close']:
            return myEnum.FALLING_TO_RISING
    elif getUpOrDwn(inputdata1) == getUpOrDwn(inputdata2):
        return ishammer(inputdata2)

        #return None
        
def testCase(testName, testValue, testTarget):
    if testValue == testTarget:
        print(u"test Case : Ok-->", testName)
    else:
        print(u"test Case :Fail-->", testName)
        print(testValue, testTarget)

upDwnSquence = 0
def getUpDwnSquence(inputdata):
    global upDwnSquence
    for idex in range(len(inputdata)):
        upDwnSquence = upDwnSquence | getUpOrDwn(inputdata[idex])<<idex
        
    print("res:0x%x"%upDwnSquence)

#def main():
#    print ("hello world")
#    print(data)
#    getUpDwnSquence(data)

#if __name__== "__main__":
#    main()
#    print(myEnum.FALLING.name)
#    print(myEnum.FALLING.value)

def testBegin():
    #test begin
    #case 01 倒锤子_阳
    inputdata = {'open':12345.67,'close':12357.66,'high':15555.67,'low':12340}
    inputdata1 = {'open':12345.67,'close':12357.66,'high':15555.67,'low':12340}
    inputdata2 = {'open':12345.67,'close':12357.66,'high':15555.67,'low':12340}
    testCase("RISING_HAMMER_UP", ishammer(inputdata), myEnum.RISING_HAMMER_UP.value)
    #case 02 倒锤子_阴
    inputdata['open'] = inputdata['close']
    inputdata['close'] = 12345.67
    testCase("FALLING_HAMMER_UP", ishammer(inputdata), myEnum.FALLING_HAMMER_UP.value)
    
    #case 03 锤子_阴
    inputdata['low'] = 9000
    testCase("FALLING_HAMMER_DWN", ishammer(inputdata), myEnum.FALLING_HAMMER_DWN)
    
    #case 04 锤子_阳 或 上吊线
    inputdata['open'] = inputdata['close']
    inputdata['close'] = 12357.66
    testCase("RISING_HAMMER_DWN", ishammer(inputdata), myEnum.RISING_HAMMER_DWN.value)
    
    # case 05 十字星
    inputdata['close'] = inputdata['open']
    testCase("RISING_EQ_DWN", ishammer(inputdata), myEnum.RISING_EQ_DWN.value)
    
    inputdata['low'] = 12340
    testCase("RISING_EQ_UP", ishammer(inputdata), myEnum.RISING_EQ_UP.value)
    
    inputdata['high'] = 11000
    inputdata['low'] = 9000
    inputdata['open'] = 10000
    inputdata['close'] = inputdata['open']
    testCase("RISING_EQ_EQ", ishammer(inputdata), myEnum.RISING_EQ_EQ.value)

    #case 06 秃头
    inputdata['high'] = 11000
    inputdata['low'] = 9000
    inputdata['open'] = 11000
    inputdata['close'] = 9900
    testCase("FALLING_ONLY_DWN", ishammer(inputdata), myEnum.FALLING_ONLY_DWN.value)
    # 光脚
    inputdata['high'] = 12000
    inputdata['low'] = 11000
    inputdata['open'] = 11000
    inputdata['close'] = 11990
    testCase("RISING_ONLY_UP", ishammer(inputdata), myEnum.RISING_ONLY_UP.value)
    
    #阴包阳 看跌: 1-阳,2-阴
    inputdata1['high'] = 12000
    inputdata1['low'] = 11000
    inputdata1['open'] = 11000
    inputdata1['close'] = 11990
    inputdata2['high'] = 12000
    inputdata2['low'] = 9000
    inputdata2['open'] = 11990
    inputdata2['close'] = 10000
    testCase("RISING_IN_FALLING", getType(inputdata1, inputdata2), myEnum.RISING_IN_FALLING.value)
    #阳包阴 看涨:1-阴,2-阳
    inputdata1['high'] = 12000
    inputdata1['low'] = 10000
    inputdata1['open'] = 11500
    inputdata1['close'] = 11200
    inputdata2['high'] = 13000
    inputdata2['low'] = 9000
    inputdata2['open'] = 11200
    inputdata2['close'] = 11990
    testCase("FALLING_IN_RISING", getType(inputdata1, inputdata2), myEnum.FALLING_IN_RISING.value)
    
    #阴孕阳 看涨:1-阴,2-阳
    inputdata1['high'] = 12000
    inputdata1['low'] = 9000
    inputdata1['open'] = 11000
    inputdata1['close'] = 10000
    inputdata2['high'] = 12009
    inputdata2['low'] = 9000
    inputdata2['open'] = 10000
    inputdata2['close'] = 10900
    testCase("FALLING_HAS_RISING", getType(inputdata1, inputdata2), myEnum.FALLING_HAS_RISING.value)
    
    #阳孕阴 看跌: 1-阳,2-阴, 阴超过阳50%报RISING_TO_FALLING
    inputdata1['high'] = 12000
    inputdata1['low'] = 11000
    inputdata1['open'] = 11000
    inputdata1['close'] = 11990
    inputdata2['high'] = 12000
    inputdata2['low'] = 9000
    inputdata2['open'] = 11990
    inputdata2['close'] = 11200
    testCase("RISING_TO_FALLING", getType(inputdata1, inputdata2), myEnum.RISING_TO_FALLING.value)
    inputdata2['close'] = 11800
    testCase("RISING_HAS_FALLING", getType(inputdata1, inputdata2), myEnum.RISING_HAS_FALLING.value)
    
    
    
    