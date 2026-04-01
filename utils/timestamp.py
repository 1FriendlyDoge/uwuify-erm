def td_format(td_object):
    seconds = int(td_object.total_seconds())

    if seconds == 0:
        return "0 secownds uwu~"

    if seconds < 0:
        new_seconds = abs(seconds)
        periods = [
            ("yeaw", 60 * 60 * 24 * 365),
            ("monf", 60 * 60 * 24 * 30),
            ("dway", 60 * 60 * 24),
            ("houww", 60 * 60),
            ("minuwte", 60),
            ("secownd", 1),
        ]

        strings = []
        for period_name, period_seconds in periods:
            if new_seconds >= period_seconds:
                period_value, new_seconds = divmod(new_seconds, period_seconds)
                has_s = "s" if period_value > 1 else ""
                strings.append("%s %s%s" % (period_value, period_name, has_s))
        if strings is not []:
            stri = ", ".join(strings)
            stri = "-" + stri
            return stri
        else:
            raise ValueError("Time dewta is too smaww owo~")

    periods = [
        ("yeaw", 60 * 60 * 24 * 365),
        ("monf", 60 * 60 * 24 * 30),
        ("dway", 60 * 60 * 24),
        ("houww", 60 * 60),
        ("minuwte", 60),
        ("secownd", 1),
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = "s" if period_value > 1 else ""
            strings.append("%s %s%s" % (period_value, period_name, has_s))
    if strings is not []:
        return ", ".join(strings)
    else:
        raise ValueError("Time dewta is too smaww owo~")
