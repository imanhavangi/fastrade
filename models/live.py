from pydantic import BaseModel
from models.backtest import BackTest
from models.position_value import PositionValue
from . import asset
from .asset import Asset

class Live(BackTest):
    cppi_value: float
    max_cppi_value: float
    riskpreval: float
    floor_value: float
    position_value: PositionValue | None = None
    length: int
    qty: dict
    trades: list
    data: dict
    timelaps: int

    @classmethod
    def from_backtest(cls, backtest: BackTest):
        qtyTemp = {}
        qtyTemp[backtest.safe] = 0
        for asset in backtest.assets:
                qtyTemp[asset.symbol] = 0
        # for asset in backtest.assets:
        #     asset.symbol = asset.symbol + '-USD'
        return cls(
            cash = backtest.cash,
            assets = backtest.assets,
            safe = backtest.safe,
            start = backtest.start,
            end = backtest.end,
            interval = backtest.interval,
            floor_percent = backtest.floor_percent / 100,
            m = backtest.m,
            changes_percent = backtest.changes_percent / 100,
            # Add values for BackData-specific fields, such as:
            cppi_value = backtest.cash,
            max_cppi_value = backtest.cash,
            riskpreval = 0.0,
            floor_value = backtest.cash * backtest.floor_percent / 100,
            position_value = None,
            length = 0,
            qty = qtyTemp,
            trades = [],
            data = {},
            timelaps = 0
        )

    def toJSON(self):
        return self.model_dump()