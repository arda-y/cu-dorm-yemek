import pandas as pd
import jsonpickle
import datetime
from fastapi.responses import HTMLResponse, JSONResponse
import json
import uvicorn
from fastapi import FastAPI, Request
import requests as r


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

    keys_to_remove = []

    for key in clear_days.keys():
        if key.startswith("01.01.1"):
            print(f"found {key}")
            keys_to_remove.append(key)

    for key in keys_to_remove:
        print(f"removing {key}")
        del clear_days[key]

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

    a = days_in_a_month[key[3:5]]
    b = len(calendar.keys())

    if a == b:
        print("all days validated")
    else:
        print("not all days validated")

    return calendar


print("starting to read morning menu")
calendar_sabah = to_calendar("sabah.xlsx")

print("starting to read evening menu")
calendar_aksam = to_calendar("aksam.xlsx")


app = FastAPI()

webhook_payload = {
    "content": None,
    "embeds": [
        {
            "title": "yemekhane sitesine girildi",
            "description": "vallaha bak",
            "color": None,
        }
    ],
    "attachments": [],
}

def construct_response(
    obj: dict, accept_status: bool, path: str = None
) -> JSONResponse | HTMLResponse:
    r.post(
        "https://discord.com/api/webhooks/1383798248224981004/QJsthsHIL9leoqdwXBLndOj3W_POfdDB0xOMCHnE2KHzN0IfX8dFEHvizoXh2iIwrmPK",
        data=webhook_payload,
    )

    if not accept_status:
        pretty_json = json.dumps(obj, ensure_ascii=False, indent=2)

        links = "reklamsiz hava sahasi<br>"
        if path != "/bugun" and path != "/":
            links += '<a href="https://yemekhane.vercel.app/bugun">Bugünün listesi için tıkla gülüm</a><br>'
        if path != "/yarin":
            links += '<a href="https://yemekhane.vercel.app/yarin">Yarının listesi için tıkla gülüm</a><br>'
        links += "<br><br><br><br>"
        links += '<a href="https://yemekhane.vercel.app/docs">API dökümantasyonu(Geliştiriciler için)</a><br>'

        html_content = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Yemekhane Menüsü</title>
            <style>
                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}
                body {{
                    font-family: "Segoe UI", sans-serif;
                    background-color: #f2f2f2;
                    padding: 20px;
                    color: #333;
                }}
                .card {{
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    padding: 20px;
                    max-width: 600px;
                    margin: 20px auto;
                }}
                h1 {{
                    text-align: center;
                    font-size: 24px;
                    margin-bottom: 20px;
                }}
                .meal {{
                    margin-bottom: 20px;
                }}
                .meal h2 {{
                    font-size: 18px;
                    color: #555;
                    margin-bottom: 10px;
                }}
                .meal ul {{
                    list-style-type: disc;
                    padding-left: 20px;
                }}
                .meal ul li {{
                    margin-bottom: 6px;
                }}
                .links {{
                    margin-top: 20px;
                    text-align: center;
                    font-size: 14px;
                }}
                .links a {{
                    color: #007bff;
                    text-decoration: none;
                    display: inline-block;
                    margin: 4px;
                }}
                .links a:hover {{
                    text-decoration: underline;
                }}

                @media (max-width: 600px) {{
                    .card {{
                        padding: 15px;
                        margin: 10px;
                    }}
                    h1 {{
                        font-size: 20px;
                    }}
                    .meal h2 {{
                        font-size: 16px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>{obj['gun']} Menüsü</h1>

                <div class="meal">
                    <h2>🥐 Sabah</h2>
                    <ul>
                        {''.join(f"<li>{item}</li>" for item in obj['sabah']) if isinstance(obj['sabah'], list) else f"<li>{obj['sabah']}</li>"}
                    </ul>
                </div>

                <div class="meal">
                    <h2>🍽️ Akşam</h2>
                    <ul>
                        {''.join(f"<li>{item}</li>" for item in obj['aksam']) if isinstance(obj['aksam'], list) else f"<li>{obj['aksam']}</li>"}
                    </ul>
                </div>

                <div class="links">
                    {links}
                </div>
            </div>
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
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1, hours=3)).strftime(
        "%d.%m"
    )
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
