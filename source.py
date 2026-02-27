# -*- coding: utf-8 -*-
"""
Created on Thurs Feb 26 2026
@name:   Interactive Brokers Source Objects
@author: Jack Kirby Cook

"""

from ib_insync import IB

from webscraping.websource import WebSource

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ["InteractiveSource"]
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


class InteractiveSource(WebSource):
    def __init__(self, *args, host, port, **kwargs):
        super().__init__(*args, **kwargs)
        self.__host = host
        self.__port = port

    def start(self):
        self.source = IB()
        parameters = dict(host=self.host, port=self.port, clientID=self.count, readonly=True)
        self.source.connect(**parameters)

    def stop(self):
        self.source.disconnect()

    @property
    def host(self): return self.__host
    @property
    def port(self): return self.__port

