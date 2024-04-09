from pydantic import BaseModel
from datetime import datetime


class Asset(BaseModel):
    symbol: str
    weight: float

    def toJSON(self):
        return self.model_dump()