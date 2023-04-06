from datetime import datetime


def is_lecturer(user):
    if user.is_lecturer:
        return True
    return False


def is_student(user):
    if user.is_student:
        return True
    return False


def d_t(dt):
    """
    Get a correct datetime object.
    If a datetime object is given, returns it after proper formatting.
    Otherwise, get the current datetime
    :param now: If True current datetime is taken for evaluation
    :type dt: datetime object
    :return:
    """
    year, month, day = dt.year, dt.month, dt.day
    h, m, s = dt.hour, dt.minute, dt.second
    datetime_str = f"{year}/{month}/{day} {h}:{m}:{s}"
    datetime_obj = datetime.strptime(
        datetime_str, '%Y/%m/%d %H:%M:%S')
    return datetime_obj
