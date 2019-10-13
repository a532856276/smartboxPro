#!/usr/bin/env python
# -*- coding: utf-8 -*-
#注意:代码模板中的代码将会被复制到任何新创建的文件中，编辑代码模板中的代码，让他;帮你自动增加固定代码吧
#aaa = input("bbb:");
#print(aaa);
from enum import IntEnum

g_PrintFlag = True


class myEnum(IntEnum):
    FALLING=0
    FALLING_HAMMER_DWN=1 # 阴锤
    FALLING_HAMMER_UP = 2
    FALLING_IN_RISING = 3 #阳包阴
    FALLING_HAS_RISING=4 #阴孕阳
    FALLING_ONLY_DWN = 5 #阴秃头
    FALLING_ONLY_UP = 6 #阴光脚
    reserve3 = 7
    reserve4 = 8
    reserve5 = 9
    RISING=10
    RISING_HAMMER_DWN = 11
    RISING_HAMMER_UP = 12 #阳 光脚
    RISING_IN_FALLING = 13
    RISING_HAS_FALLING=14
    RISING_ONLY_DWN =15
    RISING_ONLY_UP = 16
    RISING_EQ_UP=17
    RISING_EQ_EQ = 18
    RISING_EQ_DWN = 19
    RISING_TO_FALLING = 20 #下跌趋势,乌云盖顶
    FALLING_TO_RISING = 21#乌云盖顶的反信号,底部反转
    RISING_TO_FALLING10 = 22 #下跌 10%
    RISING_TO_FALLING20 = 23 #
    RISING_TO_FALLING30 = 24 #
    FALLING_TO_RISING10 = 25
    FALLING_TO_RISING20 = 26
    FALLING_TO_RISING30 = 27
    
    RISING_TO_FALLING70 = 28
    RISING_TO_FALLING80 = 29
    RISING_TO_FALLING90 = 30
