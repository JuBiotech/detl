import datetime


def dwtimestamp_to_utc(dwtimestamp:str, timeshift_to_utc_in_min:float) -> datetime.datetime:
    dt = datetime.datetime.strptime(dwtimestamp, '%Y-%m-%d %H:%M:%S')
    dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(minutes=-timeshift_to_utc_in_min)))
    return dt.astimezone(datetime.timezone.utc)
