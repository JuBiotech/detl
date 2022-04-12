import datetime


def dwtimestamp_to_utc(dwtimestamp: str) -> datetime.datetime:
    dt = datetime.datetime.strptime(dwtimestamp, "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)
