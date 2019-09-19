# -*- coding: utf-8 -*-
# @Time    : 2019/9/17 17:30
# @Author  : 蒋越希
# @Email   : jiangyuexi1992@qq.com
# @File    : okex_gateway.py
# @Software: PyCharm

import ccxt

from vnpy.event import EventEngine
from vnpy.trader.constant import Exchange
from vnpy.trader.database import database_manager
from vnpy.trader.gateway import BaseGateway
from vnpy.trader.object import SubscribeRequest, OrderRequest, CancelRequest, HistoryRequest, TickData
from copy import copy
from datetime import datetime, timedelta

class OkexfGateway(BaseGateway):
    """
    OKEX 期货 接口
    """
    default_setting = {
        "API Key": "",
        "Secret Key": "",
        "Passphrase": "",
        "Leverage": 10,
        "会话数": 3,
        "代理地址": "",
        "代理端口": "",
    }

    # Exchanges supported in the gateway.
    exchanges = [Exchange.OKEX]

    def __init__(self, event_engine: EventEngine):
        """
        
        :param event_engine: 事件引擎
        :param gateway_name: 交易接口名
        """
        super().__init__(event_engine, "OKEX")
        self.gateway = None
        # 数据库对象
        self.database_manager = database_manager

        # 所有的交易对list
        self.symbols = []

    def connect(self, setting: dict):
        """
        Start gateway connection.
        :param setting: 
        :return: 
        """
        key = setting["API Key"]
        secret = setting["Secret Key"]
        self.gateway = ccxt.okex()
        self.gateway.apiKey = key
        self.gateway.secret = secret
        # 填充 交易对
        self.__get_symbols()

    def close(self):
        """
        close gateway connection.
        :return: 
        """

    def subscribe(self, req: SubscribeRequest):
        """
        Subscribe tick data update.
        """
        ticker = self.__fetch_ticker(req.symbol)
        depth = self.__fetch_depth(req.symbol)
        # 把ticker的信息填充到TickData数据结构里
        tickdata_obj = self.on_ticker(ticker)
        # 把行情深度的信息填充到TickData数据结构里
        tickdata_obj = self.add_depth(depth, tickdata_obj)

        # 把数据插入数据库
        self.database_manager.save_tick_data([tickdata_obj])

    def on_ticker(self, ticker):
        """
        处理tick数据
        :param ticker: 
        :return: tick对象
        """
        if not ticker:
            return
        symbol = ticker["symbol"]
        dt = utc_to_local(ticker["datetime"])
        tick = TickData(symbol=symbol, exchange=Exchange.OKEX, datetime=dt, gateway_name="OKEX")
        tick.name = symbol

        tick.last_price = float(ticker["last"])
        tick.high_price = float(ticker["high"])
        tick.low_price = float(ticker["low"])
        tick.volume = float(ticker["info"]["vol"])

        return tick

    def add_depth(self, depth, tickdata: "TickData"):
        """
        tickdata 对象里完善行情深度信息
        :param depth: 行情深度信息
        :return: 返回TickData数据结构
        """

        if not depth:
            return
        # 买
        bids = depth["bids"]
        # 卖
        asks = depth["asks"]
        # 买
        for n, buf in enumerate(bids):
            price, volume = buf
            tickdata.__setattr__("bid_price_%s" % (n + 1), price)
            tickdata.__setattr__("bid_volume_%s" % (n + 1), volume)
            if n >= 4:
                break
        # 卖
        for n, buf in enumerate(asks):
            price, volume = buf
            tickdata.__setattr__("ask_price_%s" % (n + 1), price)
            tickdata.__setattr__("ask_volume_%s" % (n + 1), volume)
            if n >= 4:
                break

        return tickdata

    def send_order(self, req: OrderRequest) -> str:
        """
        Send a new order to server.

        implementation should finish the tasks blow:
        * create an OrderData from req using OrderRequest.create_order_data
        * assign a unique(gateway instance scope) id to OrderData.orderid
        * send request to server
            * if request is sent, OrderData.status should be set to Status.SUBMITTING
            * if request is failed to sent, OrderData.status should be set to Status.REJECTED
        * response on_order:
        * return OrderData.vt_orderid

        :return str vt_orderid for created OrderData
        """
        pass

    def cancel_order(self, req: CancelRequest):
        """
        Cancel an existing order.
        implementation should finish the tasks blow:
        * send request to server
        """
        pass

    def query_account(self):
        """
        Query account balance.
        """
        pass

    def query_history(self, req: HistoryRequest):
        """
        Query bar history data.
        """
        self.__fetch_bar(symbol=req.symbol, timeframe=req.interval)

    def query_position(self):
        """
        Query holding positions.
        """
        pass

    def __fetch_ticker(self, symbol):
        """
        获取tick数据
        :param symbol: 交易对符号
        :return: 返回一条tick数据
        """
        ret = self.gateway.fetch_ticker(symbol)
        return ret

    def __fetch_depth(self, symbol, limit=5):
        """
        获取市场深度
        :return: 
        """
        depth = self.gateway.fetch_order_book(symbol, limit)
        return depth

    def __fetch_bar(self, symbol, timeframe='1m'):
        """
        获取 bar数据
        :param symbol: 交易对
        :param timeframe: 时间间隔
        :param limit: 数量
        :return: 
        """
        ret = self.gateway.fetch_ohlcv(symbol, timeframe=timeframe, since=None, limit=None, params={})
        return ret

    def __get_symbols(self):
        """
        获取所有的交易对
        :return: list 交易对
        """
        self.symbols = list(self.gateway.load_markets().keys())
        return self.symbols


def get_timestamp():
    """"""
    now = datetime.utcnow()
    timestamp = now.isoformat("T", "milliseconds")
    return timestamp + "Z"


def utc_to_local(timestamp):
    """
    字符串格式的时间戳转化成datetime格式
    :param timestamp: 字符串
    :return: datetime
    """
    time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_time = time + timedelta(hours=8)
    return utc_time


