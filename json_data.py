from datetime import datetime
import uvicorn
import json
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

json_db_update = {}

 
class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None

class Item_Update(BaseModel):
    title : str
    timestamp : datetime
    description : str | None = None



app = FastAPI()

@app.get("/item_name/{item_id}")
def read_item(item_id : str):
    with open("/mnt/d/work/microservice/fake_dp_update.json",'r') as file:
        key = file.read()
        key_update = json.loads(key)
        print(key_update)
        if item_id in key_update:
            return key_update[item_id]
        return {"data":"not found"}
    
@app.post("/update_item/{update_item}")
def update_item(item_id : str , items : Item_Update):
    with open("/mnt/d/work/projects/fast api/fake_dp_update.json",'r') as file:
        item = file.read()
        items_data = json.loads(item)
        if item_id not in items_data:
            return {"data":"is not exist"}
        items_data[item_id] = jsonable_encoder(items)
        
    dp_update = json.dumps(items_data)
    print(dp_update)
    with open("/mnt/d/work/microservice/fake_dp_update.json", "w") as file:
        file.write(dp_update)
        print(dp_update)






@app.put("/items/{id}")
def _item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    #read file //////////////////////////////-----------
    with open("/mnt/d/work/microservice/fake_dp_update.json",'r')as file:
        data = file.read()
    json_dp_update = json.loads(data)
    json_dp_update[id] = json_compatible_item_data
    print(json_dp_update)
#write file///////////////////////////-----------------------------------
    fake = json.dumps(json_dp_update)
    with open("/mnt/d/work/microservice/fake_dp_update.json", "w") as file:
        file.write(fake)
        print(fake)
        



if __name__=="__main__":
    uvicorn.run("json_data:app",host='0.0.0.0', port=3000, reload=True)