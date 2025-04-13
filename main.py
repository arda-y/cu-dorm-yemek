import pandas as pd
import jsonpickle
import datetime
from fastapi.responses import HTMLResponse, JSONResponse
import json


def to_calendar(dosya: str) -> dict:
    a = pd.read_excel(dosya).to_json()
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
                    datetime.datetime.fromtimestamp(
                        int(clean_obj[x][y]) / 1000
                    ).strftime("%d.%m.%Y")
                ] = []
                y1 = y + 1
                try:
                    while True:
                        if type(clean_obj[x][y1]) == int:
                            break
                        days[
                            datetime.datetime.fromtimestamp(
                                int(clean_obj[x][y]) / 1000
                            ).strftime("%d.%m.%Y")
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

    return calendar


calendar_sabah = to_calendar("sabah.xlsx")
calendar_aksam = to_calendar("aksam.xlsx")

import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()


def construct_response(
    obj: dict, accept_status: bool, path: str
) -> JSONResponse | HTMLResponse:
    if not accept_status:
        pretty_json = json.dumps(obj, ensure_ascii=False, indent=2)

        links = ""
        if path != "/yarin":
            links += '<a href="https://yemekhane.vercel.app/yarin">Yarının listesi için tıkla gülüm</a><br>'
        if path != "/bugun":
            links += '<a href="https://yemekhane.vercel.app/bugun">Bugünün listesi için tıkla gülüm</a><br>'
        links += "<br><br><br><br>"
        links += (
            '<a href="https://yemekhane.vercel.app/docs">API dökümantasyonu(Geliştiriciler için)</a><br>'
        )

        html_content = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <title>Günün Menüsü</title>
            <style>
            body {{
                font-family: monospace;
                background: #f9f9f9;
                padding: 20px;
            }}
            pre {{
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                white-space: pre-wrap;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            </style>
        </head>
        <body>
            <pre>{pretty_json}</pre>
            {links}
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, media_type="text/html")
    return JSONResponse(content=obj)


@app.get("/")
@app.get("/bugun")
async def get_menu(request: Request):
    today = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m")
    current_path = request.url.path
    try:
        obj = {
            "gun": today,
            "sabah": calendar_sabah[today],
            "aksam": calendar_aksam[today],
        }
    except KeyError:
        obj = {
            "gun": today,
            "sabah": "Yemek bulunamadı",
            "aksam": "Yemek bulunamadı",
        }
    accept_status = request.headers.get("accept") == "text/html"
    return construct_response(obj, accept_status, current_path)


@app.get("/yarin")
def read_tomorrow(request: Request):
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d.%m")
    current_path = request.url.path
    try:
        obj = {
            "gun": tomorrow,
            "sabah": calendar_sabah[tomorrow],
            "aksam": calendar_aksam[tomorrow],
        }
    except KeyError:
        obj = {
            "gun": tomorrow,
            "sabah": "Yemek bulunamadı",
            "aksam": "Yemek bulunamadı",
        }
    accept_status = request.headers.get("accept") == "text/html"
    return construct_response(obj, accept_status, current_path)


@app.get("/bugun/sabah")
def read_today_sabah(request: Request):
    today = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m")
    try:
        obj = {
            "gun": today,
            "sabah": calendar_sabah[today],
        }
    except KeyError:
        obj = {
            "gun": today,
            "sabah": "Yemek bulunamadı",
        }
    accept_status = request.headers.get("accept") == "text/html"
    return construct_response(obj, accept_status)


@app.get("/bugun/aksam")
def read_today_aksam(request: Request):
    today = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d.%m")
    try:
        obj = {
            "gun": today,
            "aksam": calendar_aksam[today],
        }
    except KeyError:
        obj = {
            "gun": today,
            "aksam": "Yemek bulunamadı",
        }
    accept_status = request.headers.get("accept") == "text/html"
    return construct_response(obj, accept_status)


@app.get("/yarin/sabah")
def read_tomorrow_sabah(request: Request):
    tomorrow = (datetime.datetime.now() + datetime.timedelta(hours=3, days=1)).strftime(
        "%d.%m"
    )
    try:
        obj = {
            "gun": tomorrow,
            "aksam": calendar_sabah[tomorrow],
        }
    except KeyError:
        obj = {
            "gun": tomorrow,
            "aksam": "Yemek bulunamadı",
        }
    accept_status = request.headers.get("accept") == "text/html"
    return construct_response(obj, accept_status)


@app.get("/yarin/aksam")
def read_tomorrow_aksam(request: Request):
    tomorrow = (datetime.datetime.now() + datetime.timedelta(hours=3, days=1)).strftime(
        "%d.%m"
    )
    try:
        obj = {
            "gun": tomorrow,
            "aksam": calendar_aksam[tomorrow],
        }
    except KeyError:
        obj = {
            "gun": tomorrow,
            "aksam": "Yemek bulunamadı",
        }
    accept_status = request.headers.get("accept") == "text/html"
    return construct_response(obj, accept_status)


@app.get("/gun/{day}")
def read_day(day: str, request: Request):
    try:
        obj = {
            "gun": day,
            "sabah": calendar_sabah[day],
            "aksam": calendar_aksam[day],
        }
    except KeyError:
        obj = {
            "gun": day,
            "sabah": "Yemek bulunamadı",
            "aksam": "Yemek bulunamadı",
        }
    accept_status = request.headers.get("accept") == "text/html"
    return construct_response(obj, accept_status)


if __name__ == "__main__":
    uvicorn.run(host="0.0.0.0", port=2000, app=app)
