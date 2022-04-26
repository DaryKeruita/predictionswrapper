from pydantic import BaseModel


class RoundInfo(BaseModel):
    epoch: int
    start_timestamp: int
    lock_timestamp: int
    close_timestamp: int
    lock_price: int
    close_price: int
    bull_amount: int
    bear_amount: int
    closed: int
    canceled: int