import requests, time
from tinydb import TinyDB, Query


def user_exists(user_id: str, db: TinyDB, query: Query) -> bool:
    user = db.get(query["user_id"] == user_id)
    return bool(user)


def get_refresh_token(client_id: str, client_secret: str, code: str) -> str:
    url = "https://www.strava.com/api/v3/oauth/token"
    params = {
        "client_id": f"{client_id}",
        "client_secret": f"{client_secret}",
        "grant_type": "authorization_code",
        "code": f"{code}",
    }
    response = requests.post(url, params=params)
    response_data = response.json()
    refresh_token = str(response_data["refresh_token"])
    return refresh_token


async def get_access_token(user_id: str, client_id: str, client_secret: str, refresh_token: str, db: TinyDB, query: Query) -> str:
    url = "https://www.strava.com/api/v3/oauth/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post(url, params=params)
    response_data = response.json()
    refresh_token = str(response_data["refresh_token"])
    db.update({"refresh_token": str(refresh_token)}, query["user_id"] == user_id)
    access_token = str(response_data["access_token"])
    return access_token


async def post_activity(access_token: str, name: str, data_type: str, file: bytes) -> str:
    url = "https://www.strava.com/api/v3/uploads"
    params = {
        key: value
        for key, value in (
            ("name", name),
            ("description", "t.me/StravaUploadActivityBot"),
            ("data_type", data_type),
        )
        if value is not None
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    files = {"file": file}
    response = requests.post(url, params=params, headers=headers, files=files)
    response_data = response.json()
    upload_id = str(response_data["id_str"])
    return upload_id


async def get_upload(upload_id: str, access_token: str):
    url = f"https://www.strava.com/api/v3/uploads/{upload_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    delay = 1
    while True:
        response = requests.get(url, headers=headers)
        upload = response.json()
        if upload["activity_id"] or upload["error"]:
            return upload

        time.sleep(delay)
        delay *= 2


async def get_activity(access_token: str, activity_id: str) -> dict:
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response_data = response.json()

    moving_time_seconds = response_data["moving_time"]
    distance_meters = response_data["distance"]

    moving_time = time.strftime("%H:%M:%S", time.gmtime(moving_time_seconds))
    distance = round(distance_meters / 1000, 3)

    normalized_activity = {
        "id": str(response_data["id"]),
        "name": str(response_data["name"]),
        "sport_type": str(response_data["sport_type"]),
        "moving_time": moving_time,
        "distance": distance,
        "description": str(response_data["description"]),
        "gear": response_data["gear_id"],
    }
    if normalized_activity["gear"]:
        normalized_activity["gear"] = str(response_data["gear"]["name"])
    return normalized_activity


async def get_activities(access_token: str, per_page: int) -> list:
    url = "https://www.strava.com/api/v3/athlete/activities"
    params = {
        "per_page": per_page,
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, params=params, headers=headers)
    response_data = response.json()

    activity_list = []
    for activity in response_data:
        date = time.strftime("%a %d.%m.%y %H:%M", (time.strptime(activity["start_date_local"], "%Y-%m-%dT%H:%M:%SZ")))
        normalized_activity = {
            "id": activity["id"],
            "name": activity["name"],
            "date": date,
        }
        activity_list.append(normalized_activity)
    return activity_list


async def get_gear(access_token: str) -> list:
    url = "https://www.strava.com/api/v3/athlete"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response_data = response.json()

    gear_list = []
    shoes = response_data["shoes"]
    bikes = response_data["bikes"]
    for gear in shoes:
        gear["type"] = "👟"
        gear_list.append(gear)
    for gear in bikes:
        gear["type"] = "🚲"
        gear_list.append(gear)
    return gear_list


async def update_activity(access_token: str, activity_id: str, description: str = None, name: str = None, sport_type: str = None, gear_id: str = None) -> dict:
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    params = {
        key: value
        for key, value in (
            ("description", description),
            ("name", name),
            ("sport_type", sport_type),
            ("gear_id", gear_id),
        )
        if value is not None
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.put(url, params=params, headers=headers)
    return response


async def deauthorize(access_token: str):
    url = "https://www.strava.com/oauth/deauthorize"
    headers = {"Authorization": f"Bearer {access_token}"}
    requests.post(url, headers=headers)
