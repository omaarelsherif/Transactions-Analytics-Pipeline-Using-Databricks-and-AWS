from pyspark import pipelines as dp

@dp.table(
    comment="Raw transactions data ingested from source table"
)
def bronze_transactions():
    return spark.readStream.table("transactions_project.end_to_end.transactions")
