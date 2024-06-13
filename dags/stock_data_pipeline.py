from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Default args for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'stock_data_pipeline',
    default_args=default_args,
    description='A pipeline to fetch and process stock data',
    schedule_interval=timedelta(days=1),  # Adjust as needed
    start_date=days_ago(1),
    catchup=False,
)

# Task to fetch data and send to Kafka
fetch_and_send_task = BashOperator(
    task_id='fetch_and_send_data',
    bash_command='python /usr/local/airflow/scripts/fetch_and_send_stock_data.py',
    dag=dag,
)

# Task to process data with Spark
process_data_task = BashOperator(
    task_id='process_data',
    bash_command='spark-submit --master local /usr/local/airflow/scripts/spark_job.py',
    dag=dag,
)

# Define task dependencies
fetch_and_send_task >> process_data_task
