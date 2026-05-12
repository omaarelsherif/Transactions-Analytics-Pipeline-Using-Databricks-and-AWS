from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.materialized_view(
    comment="Daily transaction metrics aggregated from silver layer",
    cluster_by=["transaction_date"]
)
def gold_daily_transactions():
    return (
        spark.read.table("silver_transactions")
        .withColumn("transaction_date", F.to_date(F.col("transaction_date")))
        .groupBy("transaction_date")
        .agg(
            F.count("*").alias("total_transactions"),
            F.sum("total_amount").alias("total_revenue"),
            F.sum("quantity").alias("total_quantity_sold"),
            F.avg("total_amount").alias("avg_transaction_value")
        )
        .orderBy("transaction_date")
    )
