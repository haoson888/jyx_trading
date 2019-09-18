# -*- coding: utf-8 -*-
# @Time    : 2019/9/14 19:19
# @Author  : 蒋越希
# @Email   : jiangyuexi1992@qq.com
# @File    : data_recorder.py
# @Software: PyCharm
import multiprocessing

import logging

from time import sleep
from datetime import datetime, time

from vnpy.event import EventEngine
from vnpy.trader.constant import Exchange

from vnpy.trader.engine import MainEngine

from vnpy.trader.setting import SETTINGS

SETTINGS["log.active"] = True
SETTINGS["log.level"] = logging.INFO
SETTINGS["log.console"] = True


def main():
    """"""
    # 创建 QApplication  对象 并进行初始化

    # 事件引擎
    event_engine = EventEngine()
    # 把事件引擎附加到主引擎里
    main_engine = MainEngine(event_engine)
    main_engine.write_log("主引擎创建成功")

    # log_engine = main_engine.get_engine("log")
    # event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    # main_engine.write_log("注册日志事件监听")


    sleep(2)
    # 获取所有交易通道
    # gateway_names = main_engine.get_all_gateway_names()
    # for name in gateway_names:
    #     # 连接火币平台
    #     connect = ConnectNoDialog(main_engine=main_engine, gateway_name=name)
    #     connect.connect()
    #     sleep(2)
    #
    # sleep(20)

    # for tick in data_recorder_app.tick_recordings.keys():
    #     data_recorder_app.add_tick_recording(tick)
    #
    # for bar in data_recorder_app.bar_recordings.keys():
    #     data_recorder_app.add_bar_recording(bar)

    while True:
        # 一天
        sleep(100000000)


if __name__ == "__main__":
    main()
