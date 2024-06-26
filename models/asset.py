from pydantic import BaseModel


class Asset(BaseModel):
    symbol: str
    weight: float

    def toJSON(self):
        return self.model_dump()