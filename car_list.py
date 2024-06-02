import uvicorn
import json
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import requests
from enum import Enum

class DriveType(str, Enum):

    fwd = "FWD"
    awd = "AWD"



class CarModel(BaseModel):
    brand_name: str                          #| None = None
    car_price: str 
    transmission: str
    type : str
    mileage: str 
    Seating_Capacity : str
    drive_type: DriveType 
    Power : str 
    Torque : str 

app = FastAPI()

def scrape_car_data(url):

    page = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"})
    soup = BeautifulSoup(page.content, "html.parser")

    # Name
    h1 = soup.find("div", class_="gsc_col-xs-12 gsc_col-sm-12 gsc_col-md-7 gsc_col-lg-7 overviewdetail")
    name = h1.find("h1").text.strip()

    # Price
    price = h1.find("div", class_="price").text.replace("*Get On-Road Price*Ex-showroom Price in New Delhi", " ").strip()

    # Features
    data = {}
    my_table = soup.find("table")
    trs = my_table.find_all("tr")
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) >= 2:  
            key = tds[0].text.strip()
            value = tds[1].text.strip()
            data[key] = value  

    
    data["price"] = price
    return data

@app.get("/car_brand/{car_brand}")
def read_car_name(car_brand : str, car_name : str):
    with open ("cars_update.json",'r') as file :
        cars_data = file.read()
        cars_data_dict = json.loads(cars_data)
        if car_brand.title() in cars_data_dict:
            return cars_data_dict[car_brand.title()][car_name.title()]   
        return {"data":"not found"}

@app.put("/update/{car_brand}")
def update_spec(car_brand : str,car_name : str, car_update : CarModel):
    with open ("cars_update.json",'r') as file :
        cars_data = file.read()
        #print(cars_data)
        cars_dict = json.loads(cars_data)
        if car_brand not in cars_dict:
            return{"data":"does not exist"}
        cars_dict[car_brand][car_name] = jsonable_encoder(car_update)    
        cars_dict_update = json.dumps(cars_dict)
        with open("/mnt/d/work/projects/fast api/cars_update.json",'w') as file:
            file.write(cars_dict_update)
        return cars_dict[car_brand][car_name]

@app.post("/add/{car_brand}")
def add_car( car_url: str,  car_brand: str,car_name: str):
    
    car_data = scrape_car_data(car_url)

    if car_data:
        with open("cars_update.json", 'r') as file:
            cars_data = file.read()
            cars_dict = json.loads(cars_data)

        if car_brand not in cars_dict:
            cars_dict[car_brand] = {}
        cars_dict[car_brand][car_name] = car_data

        with open("cars_update.json", 'w') as file:
            file.write(json.dumps(cars_dict))
        return {"message": "Car added successfully"}
    else:
        return {"message": "Failed to scrape car data"}
                
@app.delete("/delete/{car_brand}/{car_name}")
def delete_car(car_brand: str, car_name: str):
    """Deletes a car or all cars from a brand based on provided parameters."""
    with open("cars_update.json", 'r') as file:
        cars_data = file.read()
        cars_dict = json.loads(cars_data)

    if car_name:  # Delete a specific car
        if car_brand not in cars_dict:
            raise HTTPException(status_code=404, detail=f"Car brand '{car_brand}' not found.")
        del cars_dict[car_brand]
        message = f"Car '{car_name}' of brand '{car_brand}' deleted successfully."

    with open("cars_update.json", 'w') as file:
        file.write(json.dumps(cars_dict))

    return {"message": message}

if __name__=="__main__":
    uvicorn.run("myapp:app",host='0.0.0.0', port=5000, reload=True)