#!/usr/bin/env python
# -*- coding:  utf-8 -*-
# author: albert  time:$(DATA)

class OrderInfo:
    def __init__(self, volume=0, available=0, cost_open=0, profit=0):
        self.volume = volume  # 持仓量
        self.available = available  # 可平仓数量
        self.cost_open = cost_open  # 开仓均价
        self.profit = profit  # 收益

    def setValue(self, volume=0, available=0, cost_open=0, profit=0):
        self.volume = volume  # 持仓量
        self.available = available  # 可平仓数量
        self.cost_open = cost_open  # 开仓均价
        self.profit = profit  # 收益

    def GetVolNum(self):
        return self.volume

    def GetAvailable(self):
        return self.available

    def SetAvailable(self, available=0):
        self.available = 0 if available < 0 else available

    def GetCost_open(self):
        return self.cost_open

    def GetProfit(self):
        return self.profit
