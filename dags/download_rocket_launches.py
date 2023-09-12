import json
import pathlib
import os

import airflow.utils.dates
import requests
import requests.exceptions as requests_exceptions
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG( # 모든 워크플로의 시작점(진입점) # DAG는 꼭 대문자로 써야하는 예약어와, 그걸 as 해서 부를 다른 이름이 필요 (여기선 dag)
    dag_id="download_rocket_launches", # DAG 이름
    description="Download rocket pictures of recently launched rockets.", 
    start_date=airflow.utils.dates.days_ago(14), # DAG 처음 실행 시작 날짜 : 현재 날짜 - 14일 
    schedule_interval="@daily", # DAG 실행 간격. 현재는 하루에 한 번
)

download_launchesAPI_using_bashcommand = BashOperator( # bash command를 실행하는 파이썬 코드
    task_id="download_launchesAPI_using_bashcommand",
    bash_command="curl -o /tmp/launches.json -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'",  # noqa: E501
    dag=dag,
)


def _get_pictures(): # 파이썬 함수는 결괏값을 파싱하고 모든 로켓 사진을 다운로드
    # 경로가 존재하는지 확인
    pathlib.Path("/tmp/images").mkdir(parents=True, exist_ok=True) # parents=True : 중간 경로들 없으면 알아서 생성, exist_ok=True : 이미 존재해도 에러발생 X
    # /tmp/images 였음 원래
     

    # Download all pictures in launches.json
    with open("/tmp/launches.json") as f: # 이전 단계의 태스크 결과 확인
        launches = json.load(f)
        image_urls = [launch["image"] for launch in launches["results"]] # 모든 발사에 대한 'image'의 URL 값 읽기
        for image_url in image_urls:
            try: # 자바의 흔적이 보이는데, 예외처리는 프로그래밍 필수임을 암시
                response = requests.get(image_url) # request는 아까 import했고, 각각의 이미지를 다운받는 코드
                image_filename = image_url.split("/")[-1] # 엄청 복잡하고 긴 경로 빼고, 마지막 파일 이름만 가져온다.
                target_file = f"/tmp/images/{image_filename}" # 타겟 파일 저장 경로 구성
                with open(target_file, "wb") as f: # 타겟 파일 핸들 열기
                    f.write(response.content) # 그 파일 경로에 각각의 이미지 (쓰기)저장
                print(f"Downloaded {image_url} to {target_file}") # Airflow log에 저장하기 위해 출력표시
            except requests_exceptions.MissingSchema:
                print(f"{image_url} appears to be an invalid URL.")
            except requests_exceptions.ConnectionError:
                print(f"Could not connect to {image_url}.")


get_pictures = PythonOperator( # DAG에서 PythonOperator를 사용하여 파이썬 함수를 호출
    task_id="get_pictures", python_callable=_get_pictures, dag=dag # python_callable : 실행할 파이썬 함수 지정
)

notify = BashOperator(
    task_id="notify",
    bash_command='echo "There are now $(ls /tmp/images/ | wc -l) images."',
    dag=dag,
)

download_launchesAPI_using_bashcommand >> get_pictures >> notify # 태스크 실행 순서를 결정하는 부분