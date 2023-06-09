import datetime


def get_months(start_date):
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sept",
        "Oct",
        "Nov",
        "Dec",
    ]
    start = start_date.month
    now = datetime.datetime.now().month

    new_months = [x for i, x in enumerate(months) if start - 1 <= i <= now]

    return new_months
