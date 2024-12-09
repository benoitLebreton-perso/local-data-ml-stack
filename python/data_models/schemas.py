"""pandera schema to validate the data and typing if the dataframes"""
import os
from datetime import datetime
from enum import Enum

import pandera.polars as pa
import polars as pl
from pandera.engines.polars_engine import DateTime


os.environ["PANDERA_VALIDATION_DEPTH"] = "SCHEMA_AND_DATA"


class RFMSegment(Enum):
    CHAMPIONS = "CHAMPIONS"
    NEW_FANS = "NEW_FANS"
    ROOKIES = "ROOKIES"
    SLEPPING = "SLIPPING"
    WHALES = "WHALES"

RFMPolars = pl.Enum(RFMSegment)

class User(pa.DataFrameModel):
    id: int = pa.Field(unique=True)
    surname: str
    rfm: RFMSegment = pa.Field(isin=[s.value for s in RFMSegment], coerce=True) # type: ignore


class Transaction(pa.DataFrameModel):
    id: int = pa.Field(unique=True)
    user_id: int
    time_stamp: DateTime = pa.Field(gt=datetime(2010,1,1,12,45,0))
    amount: float = pa.Field(gt=0.0)


if __name__ == "__main__":
    users_lf = pl.DataFrame(
        {
            'id': [1,2],
            'surname': ['MITCHELL', 'POLNAREFF'],
            'rfm': [
                'CHAMPIONS',
                'NEW_FANS',
            ],
        }
    )
    users = User.validate(users_lf)
    transactions_lf = pl.DataFrame(
        {
            'id': [1,2],
            'user_id': [1,1],
            'time_stamp': [
                datetime(2000,1,1,12,45,0),
                datetime(2000,1,1,14,55,59),
            ],
            'amount': [-1.4, 1.6]
        }
    )
    transactions = Transaction.validate(transactions_lf, lazy=True)
