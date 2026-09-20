
import asyncio

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, ConfigDict, field_validator, Field, model_validator
from fastapi.responses import StreamingResponse

app = FastAPI()

def write_log(message: str):
    with open("user_log.txt", 'a') as file:
        file.write(message +"\n")

class CreateUser(BaseModel):
    id: int
    name: str
    email: str
    phno: str
    age : int = Field(ge=18,le=100, description="Age must be between 18 and 100")
    password : str = Field(min_length =8, max_length=18)
    confirm_password : str
   

    @model_validator(mode='after')
    def check_passwords(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords are not matching")

        return self

    @field_validator("name")
    @classmethod
    def validate_name(cls,value):
        if not value.isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        return value

class PublicUser(BaseModel):
    # model_config = ConfigDict(
    #     validate_by_alias = True,
    #     validate_by_name = True
    # )
    id: int 
    name :str 
    email_id : str = Field(alias="email")

users = [
    {"id": 1, "name": "Divya", "email": "divya@gmail.com", "phno": "9014763396", "age": 25, "password": "password123456789", "confirm_password": "password123456789"},
    {"id": 2, "name": "Karthika", "email": "karthika@gmail.com", "phno": "9014763397", "age": 30, "password": "password123456789", "confirm_password": "password123456789"}
]


@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI application!"}


@app.get("/hello")
def hello():
    return {"message": "Hello, World!"}

#Get Users
@app.get("/users", response_model=list[PublicUser], response_model_by_alias=False) #using response model
def get_users(name: str = None, limit: int = None):
    return [PublicUser(**user) for user in users]

#Read User
@app.get("/user/{id}", response_model=PublicUser)
def get_user(id: int):
    for user in users:
        if user["id"] == id:
            return PublicUser(**user) #unpacking the dictionary into the PublicUser model

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )

#Create User
@app.post("/user/{id}", status_code=201)
def create_user(id: int, name: str, email: str, 
                phno: str, age: int, 
                password: str, confirm_password: str,
                background_tasks: BackgroundTasks):
    
    user = CreateUser(id=id, name=name, 
                      email=email, phno=phno, 
                      age=age, password=password, 
                      confirm_password=confirm_password)
    
    users.append(user.model_dump()) #unpacking the dictionary into the CreateUser model

    background_tasks.add_task(
        write_log,
        f'User {name} with id {id} created successfully'
    )
    return {"message": "User created successfully!"}

#Update User
@app.put("/user/{id}")
def update_user(id: int, field: str, val):
    for user in users:
        if field not in user:
            raise HTTPException(status_code=400,
                                detail= f"Invalid {field}")
        if user["id"]==id:
            user[field] = val

            return user

    raise HTTPException(status_code=404,
                        detail= "User not Found")

#Delete User
@app.delete("/user/{id}")
def delete_user(id:int):
    for i in range(len(users)):
        if users[i]["id"] == id:
            return users.pop(i)     
    
    raise HTTPException(status_code = 404,
                        detail = "User not Found")

    
