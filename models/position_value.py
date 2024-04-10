from pydantic import BaseModel


class PositionValue(BaseModel):
    totalValue: float
    s_value: float

    def toJSON(self):
        return self.model_dump()