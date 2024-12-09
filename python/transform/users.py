import pandera.polars as pa
import polars as pl
from data_models.schemas import Transaction, User
from pandera.typing.polars import LazyFrame


@pa.check_types
def rfm_users(users: LazyFrame, transactions: LazyFrame[Transaction]) -> LazyFrame[User]:
    """Create `rfm` column. RFM is a segment of the client.

    Args:
        users (LazyFrame): dataframe of users
        transactions (LazyFrame[Transaction]): dataframe of transactions

    Returns:
        LazyFrame[User]: dataframe of users with the `rfm` column
    """
    sum_amount_per_users = (
        users
        .rename({"id": "user_id"})
        .join(transactions, on="user_id")
        .group_by("user_id")
        .agg(pl.col("amount").sum())
    )
    rfm_per_users = (
        sum_amount_per_users
        .with_columns(
            pl.when(pl.col("amount") > 1000)
            .then(pl.lit("CHAMPIONS"))
            .otherwise(pl.lit("ROOKIES"))
            .alias("rfm")
        )
    )
    rfm_users_lf = users.join(
        rfm_per_users
        .select(
            [
                pl.col("user_id").alias("id"),
                pl.col("rfm")
            ]
        ), on="id")
    return rfm_users_lf
