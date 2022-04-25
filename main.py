from enum import Enum
from typing import Optional

from fastapi import FastAPI

class ModelEnum(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

@app.get('/')
async def root():
    return {'Message' : 'Basic example of FastAPI'}


# 간단한 Path Parameters 예제
# FastAPI에서는 Type Hinting을 적극적으로 활용하며, 유효성 검사에도 적용한다.
# Type Hinting이 없을 때, item_id 값은 문자열 데이터로 입력됨, 있으면 지정한 Type의 데이터로 변환
# @app.get('/items/{item_id}')
# async def read_item(item_id: int):
#     return {'item_id' : item_id}


# 정의된 API 코드에는 순서가 적용된다. 아래와 같은 예시로 구성한 후 <~/users/me> 로 API를 Call하면 확인할 수 있는
# 결과는 {'user_id' : 'Me!'} 뿐이다.
# 따라서 고정된 URI를 구성할 때에는 잘 "생각"하고 구성해야 한다.
@app.get('/users/me')
async def read_user_me():
    return {'user_id' : 'Me!'}
@app.get('/users/{user_id}')
async def read_user(user_id: str):
    return {'user_id' : user_id}


# Enum 객체를 통해서 사전에 정의된 값을 Path Parameters에 활용할 수 있다.
@app.get('/models/{model_name}')
async def get_model(model_name: ModelEnum):
    if model_name == ModelEnum.alexnet:
        return {'model_name' : model_name, 'Message' : 'Deep Learning FTW!'}

    if model_name.value == 'lenet':
        return {'model_name' : model_name, 'Message' : 'LeCNN all the images'}
    
    return {'model_name' : model_name, 'Message' : 'Have some residuals'}


# Path Parameters에 Path 자체가 포함될 경우 다음의 예제와 같은 :path 키워드 지정을 통해서 Path의 형태를 그대로 활용할 수 있다.
@app.get('/files/{file_path:path}')
async def read_file(file_path: str):
    return {'file_path' : file_path}


fake_item_db = [{'item_name' : 'Item_01'}, {'item_name' : 'Item_02'}, {'item_name' : 'Item_03'}]


# Query Parameters를 적용하는 예제. Query String과 동일한 형태 및 활용 방식을 보이고 있다.
# Query Parameters의 값은 기본적으로는 문자열 데이터이나 Type Hinting을 적용하여 변환 가능함
# Type Hinting의 형태에 더해서 기본 값을 지정해줄 수 있다.
@app.get('/items/')
async def read_item(skip: int = 0, limit: int = 10):
    return fake_item_db[skip : skip + limit]


# Optional Parameters를 적용하는 예제. Python 3.10 이상에서는 문법이 변경되는 점 참고해야 함
# Parameter를 Optional로 지정한 후 Type을 값을 지정해준다. 이후 로직단에서 조건부 동작을 정의
# Boolean 타입을 사용할 경우 Parameter에 입력된 값을 자동으로 변환해준다.
#   True : True, true, 1, yes, on
#   False: False, false, 0, no, off
@app.get('/read_item_opt/{item_id}')
async def read_item_opt(item_id: str, q: Optional[str] = None, short: bool = False):
    item = {'item_id' : item_id}
    if q:
        item.update({'q' : q})
    if not short:
        item.update(
            {'Description' : 'This is an amazing item that has a long description'}
        )
    return item


# Required Query Parameters 예제. 필수적인 Parameters에 대해 정의하는 예제
# Path Parameters가 아닌 Parameter를 사용할 때, 기본 값을 정의하면 이는 Not Required하다.
# 따라서 Required한 Parameter를 정의하려면 기본 값을 정의하지 않으면 된다.
# 다만 기본값을 None으로 정의한다면, 위의 Optional Parameters와 유사하게 사용할 수 있다.
# 그리고 당연히 필수/조건부 Parameter를 혼합해서 사용할 수 있다.
@app.get('/read_user_item/{item_id}')
async def read_user_item(item_id: str, needy: str, skip: int = 0, limit: Optional[int] = None):
    item = {'item_id' : item_id, 'needy' : needy, 'skip' : skip, 'limit' : limit}
    return item