# -*- coding: utf-8 -*-
"""
Created on Thurs Mar 5 2026
@name:   Interactive Order Objects
@author: Jack Kirby Cook

"""

import numpy as np
import pandas as pd
import ib_insync as ibkr
from abc import ABC
from types import SimpleNamespace

from interactive.source import InteractiveDataset
from finance.concepts import Querys, Concepts, Securities
from webscraping.webpages import WebATTRPage, WebUploader
from support.mixins import Naming

__author__ = "Jack Kirby Cook"
__all__ = ["InteractiveOrderUploader"]
__copyright__ = "Copyright 2026, Jack Kirby Cook"
__license__ = "MIT License"


option_formatter = lambda security: ibkr.Option(str(security.ticker), str(security.expire.strftime("%Y$m%d")), float(security.strike), str(security.option.upper())[0], "SMART", "USD")
stock_formatter = lambda security: ibkr.Stock(str(security.ticker), "SMART", "USD")
action_formatter = lambda position: {Concepts.Securities.Position.LONG: "BUY", Concepts.Securities.Position.SHORT: "SELL"}[position]
tenure_formatter = lambda order: {Concepts.Markets.Tenure.DAY: "DAY", Concepts.Markets.Tenure.FILLKILL: "FOK"}[order.tenure]
limit_formatter = lambda order: ibkr.LimitOrder(order.position, int(order.quantity), float(order.limit), tif=tenure_formatter(order))
market_formatter = lambda order: ibkr.MarketOrder(order.position, int(order.quantity), tif=tenure_formatter(order))
order_formatters = {Concepts.Markets.Term.MARKET: lambda order: market_formatter(order), Concepts.Markets.Term.LIMIT: lambda order: limit_formatter(order)}


class InteractiveSecurity(Naming, ABC, fields=["ticker", "instrument", "position", "quantity"]): pass
class InteractiveOption(InteractiveSecurity, fields=["option", "expire", "strike"]): pass
class InteractiveStock(InteractiveSecurity): pass
class InteractiveOrder(Naming, fields=["term", "tenure", "limit", "stop", "ticker", "quantity", "options", "stocks"]): pass
class InteractiveValuation(Naming, fields=["npv"]):
    def __str__(self): return f"${self.npv:.0f}"


class InteractiveOrderPage(WebATTRPage):
    def execute(self, *args, order, **kwargs):
        securities = self.securities(order, **kwargs)
        products = ibkr.Contract(str(order.ticker), "BAG", "SMART", "USD")
        products.comboLegs = securities
        order = order_formatters[order.term](order)
        self.load(InteractiveDataset.ORDER, *args, order=order, products=products, **kwargs)

    @staticmethod
    def securities(order, /, **kwargs):
        options = [SimpleNamespace(security=option_formatter(option), quantity=option.quantity, action=option.position) for option in order.options]
        stocks = [SimpleNamespace(security=stock_formatter(stock), quantity=stock.quantity, position=stock.position) for stock in order.stocks]
        products = options + stocks
        ibkr.quantifyContracts(*[product.security for product in products])
        securities = [ibkr.ComboLeg(product.security.conId, ratio=product.quantity, action=action_formatter(product.action), exchange="SMART") for product in products]
        return securities


class InteractiveOrderUploader(WebUploader, page=InteractiveOrderPage):
    def execute(self, prospects, /, **kwargs):
        assert isinstance(prospects, pd.DataFrame)
        if self.empty(prospects): return
        for order, valuation in self.calculator(prospects, **kwargs):
            self.upload(order, **kwargs)
            securities = ", ".join(list(map(str, order.securities)))
            self.console(f"{str(securities)}[{order.quantity:.0f}] @ {str(valuation)}")

    def upload(self, order, /, **kwargs):
        assert order.term in (Concepts.Markets.Term.MARKET, Concepts.Markets.Term.LIMIT)
        self.page(order=order, **kwargs)

    @staticmethod
    def calculator(prospects, /, term, tenure, **kwargs):
        assert term in (Concepts.Markets.Term.MARKET, Concepts.Markets.Term.LIMIT)
        for index, prospect in prospects.iterrows():
            strategy, quantity = prospect[["strategy", "quantity"]].values
            spot, breakeven = prospect[["spot", "breakeven"]].values
            settlement = prospect[list(Querys.Settlement)].to_dict()
            options = prospect[list(map(str, Securities.Options))].to_dict()
            options = {Securities.Options[option]: strike for option, strike in options.items() if not np.isnan(strike)}
            stocks = [Securities.Stocks(stock) for stock in strategy.stocks]
            assert spot >= breakeven and quantity >= 1
            options = [InteractiveOption(strike=strike, quantity=1, **dict(security), **settlement) for security, strike in options.items()]
            stocks = [InteractiveStock(quantity=100, **dict(security), **settlement) for security in stocks]
            order = InteractiveOrder(options=options, stocks=stocks, term=term, tenure=tenure, limit=-breakeven, stop=None, quantity=quantity, **settlement)
            valuation = InteractiveValuation(npv=prospect["npv"])
            yield order, valuation




