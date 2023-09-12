from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from urllib import request
import airflow.utils.dates

dag = DAG(
    dag_id="params_test_with_wikimedia",
    start_date=airflow.utils.dates.days_ago(2),
    schedule_interval="@hourly",
)

import logging

# csv 파일을 str로 저장
# def _extract(**context):
#     url = context["params"]["url"] # params라는 딕셔너리에서 그 딕셔너리의 key값인 url을 가져왔다.
#     #print(f"params의 값: {params}")
#     print(f"context의 값: {context}")
#     print(f"params의 값: {context['params']}")
#     print(f"url의 값: {url}")
#     logging.info(url)
#     f = requests.get(url)
#     return (f.text)



def _get_data(year, month, day, hour, output_path, **_):
    url = (
        "https://dumps.wikimedia.org/other/pageviews/"f"{year}/{year}-{month:0>2}/pageviews-{year}{month:0>2}{day:0>2}-{hour:0>2}0000.gz"
    )
    print(f"현재 전달된 url은 {url} 이다.")
    request.urlretrieve(url, output_path)


get_data = PythonOperator(
    task_id="get_data",
    python_callable=_get_data,
    op_kwargs={
        "year": "{{ prev_execution_date.year }}",
        "month": "{{ prev_execution_date.month }}",
        "day": "{{ prev_execution_date.day }}",
        "hour": "{{ prev_execution_date.hour }}",
        "output_path": "/tmp/wikipageviews.gz",
    },
    dag=dag,
)