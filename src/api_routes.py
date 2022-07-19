import json
from datetime import datetime, timedelta

import redis
from fastapi import APIRouter


router = APIRouter()
REDIS_CONN = redis.Redis(host="localhost", port=6379, password="password")


@router.get("/count/total")
def get_trip_counts_by_period(start: str = None, end: str = None):
    redis_keys = get_required_redis_keys(start, end)
    count_per_key = {key: REDIS_CONN.get(name=key) for key in redis_keys}

    # filter and else None are for managing null counts
    total_count = sum(
        filter(None, map(lambda x: int(x.decode()) if x else None, count_per_key.values()))
    )

    return {
        "total_trip_count": total_count,
        "trip_count_per_day/hour": [{k: int(v)} for k, v in count_per_key.items() if v],
    }


@router.get("/count")
def get_trip_count_by_loc_and_period(
    location: str = None, base: str = None, start: str = None, end: str = None
):
    if not (
        start and end
    ):  # don't execute only if both values are set (default case is past 6 hours)
        current_datetime = datetime.now()
        six_hours_before = current_datetime - timedelta(hours=6)
        start = f"{six_hours_before.day}/{six_hours_before.hour}"
        end = f"{current_datetime.day}/{current_datetime.hour}"

    trips = get_trip_details_by_period(start, end)["trips"]
    flatten_trips = []
    for key_trip in trips:
        values = key_trip.values()
        flatten_trips.extend(*list(values))

    if location:
        lat, lon = location.split(",")

    if location and base:
        filter_func = (
            lambda trip: trip["Lat"] == lat and trip["Lon"] == lon and trip["Base"] == base
        )
    elif location:
        filter_func = lambda trip: trip["Lat"] == lat and trip["Lon"] == lon
    elif base:
        filter_func = lambda trip: trip["Base"] == base
    else:
        return get_trip_counts_by_period(
            start, end
        )  # if no args, then send total count within past 6 hours

    result = list(filter(filter_func, flatten_trips))

    return {"trip_count": len(result), "trips": result}


@router.get("/details")
def get_trip_details_by_period(start: str = None, end: str = None):
    redis_keys = get_required_redis_keys(start, end, details=True)
    trips_per_key = {
        key: list(map(json.loads, REDIS_CONN.lrange(name=key, start=0, end=-1)))
        for key in redis_keys
    }

    return {"trips": [{k: v} for k, v in trips_per_key.items() if v]}


@router.get("/latest/1000")
def get_1000_latest_trips():
    result = REDIS_CONN.lrange("1000_latest_trips", start=0, end=-1)
    return {"1000_latest_trips": list(map(json.loads, result))}


# Helper Functions
def get_required_redis_keys(start: str = None, end: str = None, details: bool = False):
    keys = []
    current_datetime = datetime.now()

    if start and end:
        start_day, start_hour = map(int, start.split("/"))
        end_day, end_hour = map(int, end.split("/"))

        if start_day > end_day:
            keys.extend(
                _calc_keys_for_period(
                    start_day=start_day, start_hour=start_hour, end_day=30, end_hour=23
                )
            )
            keys.extend(
                _calc_keys_for_period(start_day=1, start_hour=0, end_day=end_day, end_hour=end_hour)
            )
        elif start_day == end_day:
            keys.extend(f"{start_day}/{hour}" for hour in range(start_hour, end_hour + 1))
        else:
            keys.extend(_calc_keys_for_period(start_day, start_hour, end_day, end_hour))
    else:
        past_1h_datetime = current_datetime - timedelta(hours=1)
        keys = [
            f"{past_1h_datetime.day}/{past_1h_datetime.hour}",
            f"{current_datetime.day}/{current_datetime.hour}",
        ]

    if details:
        keys = [f"{key}/details" for key in keys]

    return keys


def _calc_keys_for_period(start_day: int, start_hour: int, end_day: int, end_hour: int):
    keys = []
    for day in range(start_day, end_day + 1):
        if day == start_day:
            keys.extend(f"{day}/{hour}" for hour in range(start_hour, 24))
        elif day == end_day + 1:
            keys.extend(f"{day}/{hour}" for hour in range(end_hour + 1))
        else:
            keys.extend(f"{day}/{hour}" for hour in range(24))
    return keys
