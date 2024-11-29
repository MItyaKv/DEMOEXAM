from datetime import date
from typing import Annotated, Literal, Optional
from fastapi import Depends, FastAPI
from pydantic import BaseModel

app = FastAPI()

class Order(BaseModel):
    number: int
    dateStart: date = date.today()
    dateComplited: Optional[date] = None
    device: str
    mType: str
    description: Optional[str] = None
    client: str
    telephoneNum: Optional[str] = None
    master: Optional[str] = "Не назначен"
    status: Literal["в ожидании","Готова к выдаче", "В процессе ремонта","Ожидание запчастей", "Завершено"] = "в ожидании"
    comments: Optional[str] = None

repo = [Order(number = 1, device =  "Телефон", mType = "Сгорела матрица", description = "Черное пятно", client = "Роберт")]

massage = ""
m = False

@app.get("/")
def get_orders():
    global massage
    global m
    if m == True:
        buffer = massage
        m = False 
        massage = ""
        return repo, buffer 
    else:
        return repo

@app.get("/search")
def get_search(number: int = None, device: str = None, mType: str = None):
    for i in repo: 
        if i.number == number or i.device == device or i.mType == mType:
            return i
    return "Нет подходящих заявок"

@app.get("/statistic")
def statistic_orders():
    return f"Количество выполненных заявок: {count_orders()}", f"Количество типов неисправностей: {statisticTypes()}", f"Среднее время выполнения заявок в днях: {Time()}"


@app.get("/status")
def get_status(number: int):
    for i in repo:
        if i.number == number:
            return f"Статус заявки №{i.number} - {i.status}"

@app.post('/add')
def add_orders(order: Annotated[Order, Depends()]):
    repo.append(order)
    return "Данные успешно добавлены"

@app.post("/masters")
def add_masters(number: int, master: str):
    for i in repo:
        if i.number == number:
            if i.master == "Не назначен":
                i.master = master
            else:
                i.master = f"{i.master}, {master}"
    return "Мастер успешно добавлен" 
        
@app.post("/comments")
def add_comments(number: int, comments: str):
    for i in repo:
        if i.number == number:
            if i.comments == None:
                i.comments = comments
            else:
                i.comments = f"{i.comments}, {comments}"            
        return f"Комментарий к заявке {i.number} добавлен"

@app.put('/update')
def update_orders(number: int, status: Literal["в ожидании","Готова к выдаче", "В процессе ремонта","Ожидание запчастей", "Завершено"], master: str,
                  description: str):
    global massage
    global m
    for i in repo: 
        if i.number == number:
            if status == "Выполнено":
                i.dateComplited = date.today() 
                massage += f"Заявка №{i.number} Выполнена"
                m = True
                i.status = status
            elif i.status != status:
                massage += f"Статус заявки №{i.number} изменён"
                m = True
                i.status = status
            i.master = master
            i.description = description
    return "Данные успешно обновлены"

def complited_orders():
    return[o for o in repo if o.status == "Выполнено"]

def count_orders():
    return len(complited_orders())

def statisticTypes():
    result = {}
    for i in repo:
        if i.mType in result:
            result[i.mType] += 1
        else:
            result[i.mType] = 1
    return result

def Time():
    srTime = []
    for i in complited_orders():
        srTime.append(i.dateComplited - i.dateStart)
    dayTime = sum([t.days for t in srTime])
    countOrders = count_orders()
    result = dayTime/countOrders
    return result