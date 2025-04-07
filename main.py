import pandas as pd
import jsonpickle
import datetime


a = pd.read_excel("aksam.xlsx").to_json()
# convert to turkish encoding
b = a.encode("utf-8").decode("latin-1")
obj = jsonpickle.decode(b)


obj2 = {}
for key in obj:
    if key.startswith("Unnamed: "):
        obj2[int(key.replace("Unnamed: ", ""))] = obj[key]
    else:
        obj2[key] = obj[key]


obj = obj2


clean_obj = {}
for q in obj:
    for z in obj[q]:
        if clean_obj.get(q) is None:
            clean_obj[q] = {}
        if obj[q][z] == None:
            continue
        clean_obj[q][int(z)] = obj[q][z]


days = {}
for x in clean_obj.keys():
    for y in clean_obj[x]:
        if type(clean_obj[x][y]) == int:
            days[
                datetime.datetime.fromtimestamp(int(clean_obj[x][y]) / 1000).strftime(
                    "%d/%m/%Y"
                )
            ] = []
            y1 = y + 1
            try:
                while True:
                    if type(clean_obj[x][y1]) == int:
                        break
                    days[
                        datetime.datetime.fromtimestamp(
                            int(clean_obj[x][y]) / 1000
                        ).strftime("%d/%m/%Y")
                    ].append(clean_obj[x][y1])
                    y1 = y1 + 1
            except KeyError:
                continue


clear_days = jsonpickle.decode(jsonpickle.encode(days).replace("*", ""))

try:
    clear_days.pop("01/01/1970")
except KeyError:
    pass  # remove the key if it exists

del clean_obj, obj, b, a, x, y, y1, key, obj2, days

counter = 0
for y in range(1, 32):
    if len(str(y)) == 1:
        i = "0" + str(y)
    else:
        i = str(y)
    for key in clear_days.keys():
        if key.startswith(f"{i}/"):
            counter += 1
            break


calendar = {}
for key in clear_days.keys():
    calendar[key[:5]] = clear_days[key]

days_in_a_month = {
    "01": 31,
    "02": 28,
    "03": 31,
    "04": 30,
    "05": 31,
    "06": 30,
    "07": 31,
    "08": 31,
    "09": 30,
    "10": 31,
    "11": 30,
    "12": 31,
}

for key in calendar.keys():
    a = days_in_a_month[key[3:]]
    b = len(calendar.keys())

    if a == b:
        print("all days validated")
    else:
        print("not all days validated")

    break

if False:
    for key in calendar.keys():
        print(key, calendar[key])
        print("-------------")

print(calendar["08/04"])

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return calendar


@app.get("/today")
def read_today():
    today = datetime.datetime.now().strftime("%d/%m")
    return calendar[today]


@app.get("/tomorrow")
def read_tomorrow():
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d/%m")
    return calendar[tomorrow]


@app.get("/day/{day}")
def read_day(day: str):
    try:
        return calendar[day]
    except KeyError:
        return {"error": "Day not found"}


uvicorn.run(host="0.0.0.0", port=2000, app=app)
