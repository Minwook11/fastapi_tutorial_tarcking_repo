from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def root():
    return {'Message' : 'Basic example of FastAPI'}