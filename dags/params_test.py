from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

dag = DAG(
        dag_id = "sunnytest",
        start_date = datetime(2021,1,31),
        schedule_interval = '@once'
    )

import requests
import logging

# csv 파일을 str로 저장
def _extract(**context):
    url = context["params"]["url"] # params라는 딕셔너리에서 그 딕셔너리의 key값인 url을 가져왔다.
    #print(f"params의 값: {params}")
    print(f"context의 값: {context}")
    print(f"params의 값: {context['params']}")
    print(f"url의 값: {url}")
    logging.info(url)
    f = requests.get(url)
    return (f.text)



exec_extract = PythonOperator(
    task_id = 'extract',
    python_callable = _extract,       
    params={'url': 'https://s3-geospatial.s3-us-west-2.amazonaws.com/name_gender.csv'},
    # provide_context=True,
    dag = dag
    )