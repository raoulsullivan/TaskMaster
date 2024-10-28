from datetime import datetime


def fuzzy_datetime_validator(input, raise_if_invalid=True):
    """
    This helper function will attempt to coerce an input into a datetime.
    Accepted input formats are:
    * '%Y-%m-%d %H:%M'
    * '%Y-%m-%d' (will set 00:00 as time)
    * '%m-%d' (will set current year and 00:00 as time)
    """
    date = None
    try:
        date = datetime.strptime(input, '%Y-%m-%d %H:%M')
    except ValueError:
        pass

    # This will assume 00:00 is the time
    try:
        date = datetime.strptime(input, '%Y-%m-%d')
    except ValueError:
        pass

    # This will set the current year and assume 00:00 is the time
    try:
        year = datetime.now().year
        input_with_year = f'{year}-{input}'
        date = datetime.strptime(input_with_year, '%Y-%m-%d')
    except ValueError:
        pass

    if not date and raise_if_invalid:
        raise ValueError(
            f'Provided input {input} cannot be coerced to a datetime')

    return date
