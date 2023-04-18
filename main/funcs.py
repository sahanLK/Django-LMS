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


def get_naive_dt(dt):
    """
    Returns a naive datetime object (not timezone aware)
    in local timezone from given UTC datetime object from
    django model DatetimeField.
    Only used for Sri Lanka timezone ('Asia/Colombo')
    :type dt: datetime object (in UTC)
    :return:
    """
    local_tz = pytz.timezone('Asia/Colombo')
    local = local_tz.fromutc(dt.replace(tzinfo=None))
    fmt = '%Y-%b-%d %a %H:%M:%S %p'
    dt_str = local.strftime(fmt)
    dt_obj = datetime.strptime(dt_str, fmt)
    return dt_obj
