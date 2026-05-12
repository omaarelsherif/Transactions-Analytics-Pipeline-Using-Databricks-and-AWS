from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Cleaned transactions data with standardized product names and quality checks"
)
@dp.expect_or_drop("valid_transaction_id", "transaction_id IS NOT NULL")
@dp.expect_or_drop("valid_amount", "total_amount > 0")
@dp.expect_or_drop("valid_quantity", "quantity > 0")
@dp.expect("valid_customer_id", "customer_id IS NOT NULL")
def silver_transactions():
    return (
        spark.readStream.table("bronze_transactions")
        .withColumn("product_name", F.trim(F.initcap(F.col("product_name"))))
        .withColumn("category", F.trim(F.col("category")))
        .withColumn("store_location", F.trim(F.col("store_location")))
        .withColumn("payment_method", F.trim(F.col("payment_method")))
    )
