from datetime import datetime
import pytz


def is_lecturer(user):
    if user.is_lecturer:
        return True
    return False


def is_student(user):
    if user.is_student:
        return True
    return False


# def get_naive_dt(dt):
#     """
#     Returns a naive datetime object (not timezone aware)
#     in local timezone from given UTC datetime object from
#     django model DatetimeField.
#     Only used for Sri Lanka timezone ('Asia/Colombo')
#     :type dt: datetime object (in UTC)
#     :return:
#     """
#     local_tz = pytz.timezone('Asia/Colombo')
#     local = local_tz.fromutc(dt.replace(tzinfo=None))
#     fmt = '%Y-%b-%d %a %H:%M:%S %p'
#     dt_str = local.strftime(fmt)
#     dt_obj = datetime.strptime(dt_str, fmt)
#     return dt_obj


def local_to_utc_aware(local_dt: datetime):
    """
    Convert local datetime object into UTC format.
    :param local_dt: Local datetime object
    :return:
    """
    fmt = "%Y/%m/%d %H:%M:%S"
    dt_str = str(local_dt.strftime(fmt))
    dt_local = datetime.strptime(dt_str, fmt)
    dt_utc = dt_local.astimezone(pytz.UTC)
    return dt_utc


def local_to_utc_naive(local_dt: datetime):
    aware = local_to_utc_aware(local_dt)
    return aware.replace(tzinfo=None)


def utc_to_local_aware(utc_dt: datetime):
    return utc_dt.astimezone(
        pytz.timezone('Asia/Colombo'))


def utc_to_local_naive(utc_dt: datetime):
    aware = utc_to_local_aware(utc_dt)
    return aware.replace(tzinfo=None)


def get_naive_dt(dt: datetime):
    return dt.replace(tzinfo=None)
