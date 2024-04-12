from pydantic import BaseModel
from datetime import datetime
from . import asset


class BackTest(BaseModel):
    cash: float
    assets: list[asset.Asset]
    safe: str
    start: str
    end: str
    interval: str
    floor_percent: float
    m: int
    changes_percent: float

    def toJSON(self):
        return self.model_dump()