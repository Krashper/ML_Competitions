from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow import DAG
from datetime import datetime
from scripts.model_retrain import retrain_model
from scripts.metrics_to_db import save_metrics_to_db


with DAG(
    dag_id="RETRAIN_MODEL_DAG_2",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False
) as dag:

    retrain_model_task = PythonOperator(
        task_id='train_model',
        python_callable=retrain_model,
        dag=dag
    )

    save_metrics_task = PythonOperator(
        task_id='save_metrics',
        python_callable=save_metrics_to_db,
        dag=dag
    )

    task_b = BashOperator(
        task_id='task_b',
        bash_command='echo "hello"',
        dag=dag
    )

    retrain_model_task >> save_metrics_task >> task_b