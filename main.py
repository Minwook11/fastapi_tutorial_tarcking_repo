from enum import Enum
from typing import List, Set, Optional
from datetime import datetime, time, timedelta
from uuid import UUID

from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel, Field, HttpUrl


class ModelEnum(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


# 추가적인 Model을 정의하여 Nested Model을 사용해보는 예제
# 아래 Item 모델에서 지금 정의한 Image 모델을 사용
# int, str, float과 같은 일반적인 타입 뿐만 아니라 특별한 타입의 데이터와 그에 대한 유효성 검사 예제
# 아래에서는 HttpUrl을 예시로 사용함
class Image(BaseModel):
    url: HttpUrl
    name: str


# Data Model을 정의한다. 정의할 때는 이전에 Query Parameters에서와 비슷하게 정의가능
# 기본값 지정 : 필수 데이터, Type Hinting 적극 활용, Optional을 통한 조건부 데이터 지정 가능 등등
## List 및 Set 모듈을 사용하여 Model에 여러 데이터 타입을 사용하는 예제
# 당연히 Dict도 사용 가능하다.
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    # tax: Optional[float] = None
    tax: float = 10.5
    tagL: List[str] = []
    tagS: Set[str] = set()
    image: Optional[Image] = None
    
    ## 사용자 정의 Data Model에 대하여 데이터 값 예시를 지정하는 방법의 예제
    class Config:
        schema_extra= {
            'example' : {
                'name' : 'Example_name',
                'description' : 'Example_description',
                'price' : 1000.0,
                'tax' : 13.4,
                'tagL' : ['tag1', 'tag2'],
            }
        }


## Field 모듈을 사용하는 예제로서 이전의 Path, Query, Body와 유사한 사용법을 보인다.
# Field 모듈은 Pydantic 패키지에 포함되어 있으며 사전정의 데이터 모델에 적용할 수 있다.
# gt, ge등과 같은 값을 기준으로 하는 검사나 길이와 같은 추가적인 유효성 검사를 지정할 수 있다.
# Description과 같은 메타데이터 지정에도 사용할 수 있다.
class User(BaseModel):
    username: str = Field(..., title="User's login account string", max_length=64)
    full_name: Optional[str] = Field(None, description="User's real full name. It's sooooooo long~", max_length=512)
    temp_val: Optional[int] = Field(None, gt=1, description="Temporary slot. Basically this slot is useless")


# Input/Output 에서 사용할 Model 정의
class TestIn(BaseModel):
    credential_data: str
    plain_text: str
    plain_num: int
    option: Optional[int] = None

class TestOut(BaseModel):
    plain_text: str
    plain_num: int
    option: Optional[int] = None
    

app = FastAPI()


@app.get('/')
async def root():
    return {'Message' : 'Basic example of FastAPI'}


## Response 데이터에도 사전 정의 Model을 활용할 수 있는 예제
# Response 데이터에 모델을 지정하면 자동 변환, 유효성 검사, 문서 반영의 이점을 가져갈 수 있다.
# 하지만 무엇보다도 출력 데이터에 제한을 걸어둔다는 것이 더욱 중요한 포인트
@app.post("/items/response_model", response_model=Item)
async def create_item_use_response_model(item: Item):
    return item


# Request에 포함될 데이터를 Input, Response에 포함될 데이터를 Output으로 지정하여 활용하는 예제
@app.post("/test/in_out_model", response_model=TestOut)
async def in_out_model_use_test(item: TestIn):
    return item


# response_model_exclude_unset, response_model_include, response_model_exclude 사용 예제
items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar fighters", "price": 62, "tax": 20.2},
    "baz": {
        "name": "Baz",
        "description": "There goes my baz",
        "price": 50.2,
        "tax": 10.5,
    },
}

# response_model_exclude_unset 옵션은 True/False로 지정하여 사용하며 기본값은 False
# 지정된 모델의 Key중 값이 Set되어 있는 데이터만 사용하고자 할 때 지정 True로 지정
@app.get("/items/{item_id}/exclude_unset", response_model=Item, response_model_exclude_unset=True)
async def read_item_with_exclude_unset(item_id: str):
    return items[item_id]

# response_model_include는 지정한 Key값과 Data만 사용할 때 사용
@app.get(
    "/items/{item_id}/name/include",
    response_model=Item,
    response_model_include=["name", "description"],
)
async def read_item_name_with_include(item_id: str):
    return items[item_id]

# response_model_exclude는 지정한 Key값과 Data를 제외할 때 사용
# 정의된 전체 Model Key중 지정한 Key만 제외하고 전부 표현됨
@app.get("/items/{item_id}/public/exclude", response_model=Item, response_model_exclude=["tax"])
async def read_item_public_data_with_exclude(item_id: str):
    return items[item_id]


## 일반적인 데이터 타입이 아닌 다양한 데이터 타입을 사용하는 예제
# 사용가능한 데이터 타입의 종류에 대한 정확한 확인은 https://pydantic-docs.helpmanual.io/usage/types/
@app.put("/read_item_with_extra_dtype/{item_id}")
async def read_items_with_extra_dtype(
    item_id: UUID,
    start_datetime: Optional[datetime] = Body(None),
    end_datetime: Optional[datetime] = Body(None),
    repeat_at: Optional[time] = Body(None),
    process_after: Optional[timedelta] = Body(None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


# Nested Model의 형태를 확인해보기 위한 테스트 API
# API 자체에 케이스 별로 관리 가능한 데이터 셈플을 추가하는 방법 예제
# 케이스 별로 관리가 가능하고 자세한 설명 함께 기록해 놓을 수 있다.
@app.put('/nested_model/{item_id}')
async def nested_model(
    item_id: int, 
    item: Item = Body(
        ...,
        examples = {
            'norma'"normal": {
                "summary": "A normal example",
                "description": "A **normal** item works correctly.",
                "value": {
                    "url": "https://Foo",
                    "name": "A very nice Item"
                },
            },
            "converted": {
                "summary": "An example with converted data",
                "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                "value": {
                    "url": "https://Bar",
                    "name": "35.4",
                },
            },
            "invalid": {
                "summary": "Invalid data is rejected with an error",
                "value": {
                    "url": "http://Baz",
                    "name": "thirty five point four",
                },
            },
        }
    )):
    results = {'item_id' : item_id, 'item' : item}
    return results


## 이전 Query, Path와 비슷한 Body 모듈에 대한 예제
# Body 모듈의 사용법은 이전의 Query, Path와 거의 동일하다.
# 지정한 변수명과 같은 Key를 Request의 Body에서 찾은 후 데이터를 읽어온다.
# 즉, Body를 지정하는 변수명은 Request Body내부의 Key와 동일해야 한다. Type Hinting에 맞는 데이터 타입도 따질 것
@app.put('/items/body/{item_id}')
async def update_item_use_body(item_id: int, item: Item, user: User, importance: List[str] = Body(...)):
    results = {'item_id' : item_id, 'item' : item, 'user' : user, 'importance' : importance}
    return results


# Request Body가 단일 모델에 대해서 구성되어 있다면 해당 모델의 이름은 표현되지 않는다.
# 일관적인 데이터 형상 관리를 위해서 단일 모델 데이터를 다루는 경우에도 이름을 표시해줄 수 있는 옵션이 있다.
#   - embed 옵션을 True로 지정하여 이용 가능하다.
#   - 정확하게 어떻게 형태가 바뀌는 지는 https://fastapi.tiangolo.com/tutorial/body-multiple-params/
#   - 위 링크 가장 아래쪽 확인 바람
@app.put('/items/body/embed/{item_id}')
async def use_body_embed_opt(item_id: int, item: Item = Body(..., embed=True)):
    results = {'item_id' : item_id, 'item' : item}
    return results


## 이전 튜토리얼과 비슷하게 이번에는 Path Parameters에 대해서 다양한 유효성 검사를 추가하는 예제
# Path라는 모듈을 이용한다. 기본적인 형태는 다음과 같고, Path parameters는 사용할 경우에는 필수 데이터이므로
# Path(<...>)의 방법으로 필수 데이터임을 명시한다.
# Path parameters에 적용하는 validation은 숫자와 관련된 것을 적용할 수 있으며 키워드는 다음과 같다.
#   - gt : 'g'reater 't'han
#   - ge : 'g'reater than or 'e'qual
#   - lt : 'l'ess 't'han
#   - le : 'l'ess than or 'e'qual
#   * Integer뿐만 아니라 Float 데이터에도 사용 가능하다.
#   * Query는 문자열만, Path는 숫자만 유효성 검사를 담당하는 것은 아니다. 양쪽 모두 같은 방법으로 각각의 유효성 검사 가능함
@app.get('/items_with_path/{item_id}')
async def read_items_path(
    item_id: int = Path(..., title='The Id of the item to get', gt=0, le=1000),
    q: Optional[str] = Query(None, alias='item-query'),
    size: float = Query(..., gt=0, lt=10.5)
):
    results = {'item_id' : item_id}
    if q:
        results.update({'q' : q})    
    return results


## Query parameters에 다양한 유효섬검사를 추가하는 예제
# Query 모듈을 사용하여 입력받는 parameter에 최소/최대길이 검사 또는 정규표현식을 유효성 검사 항목으로 추가
# Query를 사용하여 기본값을 지정할 때에는 Query의 첫번째 인수로 str 데이터를 지정한다.
#   - 기본값은 List와 같은 데이터도 지정 가능하다.
@app.get('/read_items_with_valid')
async def read_items_with_valid(q: Optional[str] = Query(None, min_length=3, max_length=50, regex="^fixedquery$")):
    results = [{'item_id' : 'Item01'}, {'item_id' : 'Item02'}]
    if q:
        results.update({'q' : q})
    return results


# List/Multiple values to Path Parameters 예제
# 동일한 Key를 통해서 여러 값을 입력받는 방법
#   - <API_URI> + ? + ( <KEY_NAME> = <VALUE> & ... ) 의 형태로 API를 콜한다.
#   - 그러면 아래 코드 기준으로 q 변수에는 입력된 여러 값이 List의 형태로 저장된다.
@app.get('/items_with_multiple_vals')
async def read_items_with_multiple_val(q: Optional[List[str]] = Query(None)):
    query_items = {'q' : q}
    return query_items


# Metadata 정의 예제
# Metadata는 입력되는 Parameters에 대한 정보를 가지고 기능적인 부분으로 동작하지 않고 OpenAPI와 문서화와 관련된
# 사용자 인터페이스나 외부 도구를 통해서 문서에 포함된다.
@app.get('/items/metadata')
async def read_items_metadata(
        q: Optional[str] = Query(
            None,
            title = 'Qeury String',
            description = 'Query string for Metadata. It can check into documents interface',
            min_length = 3,
        )
    ):
        results = {'items' : [{'item_id' : 'Foo'}, {'item_id' : 'Bar'}]}
        if q:
            results.update({'q' : q})
        return results
    
    
## POST Method API의 예제
# 사전 정의한 Data Model을 Input data로 지정하여 Request의 Body부분의 Data와 Model을 비교하여 유효성 검사 진행
# 이후 지정한 변수로 입력된 데이터를 활용 가능함(예제에서는 <item> 변수)
# DRF와 같이 유효성 검사 전/후 데이터가 나뉘지는 않고 입력 유효성 검사를 통과한 이후 객체에 대해서도 데이터 수정이 가능
#   - DRF는 데이터 직접 접근을 막는 편 (확실하게 확인할 필요는 있음)
@app.post('/items/')
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({'price with tax' : price_with_tax})
    return item_dict


# PUT Method를 사용한 Path parameters와 Query parameters, Request Body를 함께 활용하는 예제
# 이 경우 구분 기준은 다음과 같다.
#   - API URI에 포함된 경우, Path parameters로 구분한다.
#   - int/float/str/bool과 같은 Singular 타입의 경우, Qeury parameter로 구분한다.
#   - Pydantic Model로 정의 되었을 경우, Request의 Body 데이터로 구분한다.
@app.put('/items/{item_id}')
async def create_item(item_id: int, item: Item, q: Optional[str] = None):
    result = {"item_id" : item_id, **item.dict()}
    if q:
        result.update({'q' : q})
    return result


fake_item_db = [{'item_name' : 'Item_01'}, {'item_name' : 'Item_02'}, {'item_name' : 'Item_03'}]


## Query Parameters를 적용하는 예제. Query String과 동일한 형태 및 활용 방식을 보이고 있다.
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


## 간단한 Path Parameters 예제
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