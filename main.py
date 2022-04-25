from enum import Enum

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
@app.get('/items/{item_id}')
async def read_item(item_id: int):
    return {'item_id' : item_id}


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