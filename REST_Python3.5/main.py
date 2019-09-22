#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hbdm_api_demo import *
import time
import threading

TestBign = True

def TestCase():
    testdataDecodeFromNet()


if __name__ == "__main__":
	g_QueryKline = MyTimer(GetContractKline, 5, True)
	
	if GetContractInfo(contractType=g_ContractType):  # this_week(当周) next_week(下周) quarter(季度)
		print(g_ContractCode)
		GetContractIndex(symbol=g_symbol)  # 获取合约指数，暂时不知何用
	#启动定时任务，定时时间由入参决定
	g_QueryKline.start();
	while True:
		print("main process")
		time.sleep(10)
