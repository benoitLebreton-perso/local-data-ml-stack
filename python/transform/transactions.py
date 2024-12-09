import pandera.polars as pa
import polars as pl
from data_models.schemas import Transaction
from pandera.typing.polars import LazyFrame


@pa.check_types
def clean_transactions(transactions: LazyFrame) -> LazyFrame[Transaction]:
    """Clean the transactions. Handle timezone for Europe (eu) and Asia (as).

    Args:
        transactions (LazyFrame): dataframe of transactions

    Returns:
        LazyFrame[Transaction]: cleaned dataframe of transactions
    """
    transactions = transactions.with_columns(
        [
            pl.col("time_stamp").dt.replace_time_zone("Europe/Brussels").alias("eu_time_stamp"),
            pl.col("time_stamp").dt.replace_time_zone("Asia/Kathmandu").alias("as_time_stamp"),
            pl.col("amount").cast(pl.Float64),
        ]
    )
    return transactions