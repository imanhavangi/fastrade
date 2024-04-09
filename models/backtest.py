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

    created_user_id: str | None = None
    assign_user_ids: list[str]
    priority: int | None = None
    urgency: int | None = None
    status: int | None = None
    # TODO: delete datetime.now() from this model
    created_time: str = str(datetime.now())
    doing_time: str = str(datetime.now())
    doing_count: int = 0

    def toJSON(self):
        return self.model_dump()