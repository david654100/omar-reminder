"""Omer counting logic: day calculation, Hebrew text, and transliteration for all 49 days."""

from datetime import date

BRACHA_HEBREW = (
    "בָּרוּךְ אַתָּה יְיָ אֱלֹהֵינוּ מֶלֶךְ הָעוֹלָם "
    "אֲשֶׁר קִדְּשָׁנוּ בְּמִצְוֹתָיו וְצִוָּנוּ עַל סְפִירַת הָעוֹמֶר"
)

BRACHA_TRANSLITERATION = (
    "Baruch Atah Adonai Eloheinu Melech ha'olam "
    "asher kid'shanu b'mitzvotav v'tzivanu al sefirat ha'Omer."
)

_ONES_HEB = {
    1: "אֶחָד", 2: "שְׁנֵי", 3: "שְׁלֹשָׁה", 4: "אַרְבָּעָה",
    5: "חֲמִשָּׁה", 6: "שִׁשָּׁה", 7: "שִׁבְעָה", 8: "שְׁמוֹנָה", 9: "תִּשְׁעָה",
}

_TENS_HEB = {10: "עֲשָׂרָה", 20: "עֶשְׂרִים", 30: "שְׁלֹשִׁים", 40: "אַרְבָּעִים"}

_TEENS_HEB = {
    11: "אַחַד עָשָׂר", 12: "שְׁנֵים עָשָׂר", 13: "שְׁלֹשָׁה עָשָׂר",
    14: "אַרְבָּעָה עָשָׂר", 15: "חֲמִשָּׁה עָשָׂר", 16: "שִׁשָּׁה עָשָׂר",
    17: "שִׁבְעָה עָשָׂר", 18: "שְׁמוֹנָה עָשָׂר", 19: "תִּשְׁעָה עָשָׂר",
}

_WEEK_WORDS_HEB = {
    1: "שָׁבוּעַ אֶחָד", 2: "שְׁנֵי שָׁבוּעוֹת", 3: "שְׁלֹשָׁה שָׁבוּעוֹת",
    4: "אַרְבָּעָה שָׁבוּעוֹת", 5: "חֲמִשָּׁה שָׁבוּעוֹת",
    6: "שִׁשָּׁה שָׁבוּעוֹת", 7: "שִׁבְעָה שָׁבוּעוֹת",
}

_AND_DAYS_HEB = {
    1: "וְיוֹם אֶחָד", 2: "וּשְׁנֵי יָמִים", 3: "וּשְׁלֹשָׁה יָמִים",
    4: "וְאַרְבָּעָה יָמִים", 5: "וַחֲמִשָּׁה יָמִים", 6: "וְשִׁשָּׁה יָמִים",
}

_VAV_ONES_HEB = {
    1: "אֶחָד", 2: "שְׁנַיִם", 3: "שְׁלֹשָׁה", 4: "אַרְבָּעָה",
    5: "חֲמִשָּׁה", 6: "שִׁשָּׁה", 7: "שִׁבְעָה", 8: "שְׁמוֹנָה", 9: "תִּשְׁעָה",
}

_VAV_CONNECTOR = {
    1: "וְ", 2: "וּ", 3: "וּ", 4: "וְ", 5: "וַ",
    6: "וְ", 7: "וְ", 8: "וּ", 9: "וְ",
}

# Transliteration lookup tables
_ONES_TR = {
    1: "echad", 2: "shnei", 3: "shlosha", 4: "arba'a",
    5: "chamisha", 6: "shisha", 7: "shiv'a", 8: "shmona", 9: "tish'a",
}
_TEENS_TR = {
    11: "achad asar", 12: "shneim asar", 13: "shlosha asar",
    14: "arba'a asar", 15: "chamisha asar", 16: "shisha asar",
    17: "shiv'a asar", 18: "shmona asar", 19: "tish'a asar",
}
_TENS_TR = {10: "asara", 20: "esrim", 30: "shloshim", 40: "arba'im"}
_WEEK_TR = {
    1: "shavua echad", 2: "shnei shavuot", 3: "shlosha shavuot",
    4: "arba'a shavuot", 5: "chamisha shavuot", 6: "shisha shavuot",
    7: "shiv'a shavuot",
}
_AND_DAYS_TR = {
    1: "v'yom echad", 2: "u'shnei yamim", 3: "u'shlosha yamim",
    4: "v'arba'a yamim", 5: "va'chamisha yamim", 6: "v'shisha yamim",
}
_VAV_ONES_TR = {
    1: "v'echad", 2: "u'shnayim", 3: "u'shlosha", 4: "v'arba'a",
    5: "va'chamisha", 6: "v'shisha", 7: "v'shiv'a", 8: "u'shmona", 9: "v'tish'a",
}


def _hebrew_number(n: int) -> str:
    if n <= 9:
        return _ONES_HEB[n]
    if n == 10:
        return _TENS_HEB[10]
    if 11 <= n <= 19:
        return _TEENS_HEB[n]
    if n in (20, 30, 40):
        return _TENS_HEB[n]
    tens = (n // 10) * 10
    ones = n % 10
    return f"{_VAV_CONNECTOR[ones]}{_VAV_ONES_HEB[ones]} {_TENS_HEB[tens]}"


def _translit_number(n: int) -> str:
    if n <= 9:
        return _ONES_TR[n]
    if n == 10:
        return _TENS_TR[10]
    if 11 <= n <= 19:
        return _TEENS_TR[n]
    if n in (20, 30, 40):
        return _TENS_TR[n]
    tens = (n // 10) * 10
    ones = n % 10
    return f"{_VAV_ONES_TR[ones]} {_TENS_TR[tens]}"


def _day_noun_heb(n: int) -> str:
    if n == 1:
        return "יוֹם"
    if 2 <= n <= 10:
        return "יָמִים"
    return "יוֹם"


def _day_noun_tr(n: int) -> str:
    if n == 1:
        return "yom"
    if 2 <= n <= 10:
        return "yamim"
    return "yom"


def get_count_hebrew(day: int) -> str:
    """Build the Hebrew counting text for the given Omer day (1-49)."""
    num = _hebrew_number(day)
    noun = _day_noun_heb(day)
    weeks = day // 7
    remainder = day % 7

    if day < 7:
        return f"הַיּוֹם {num} {noun} לָעוֹמֶר"

    week_part = _WEEK_WORDS_HEB[weeks]
    if remainder == 0:
        return f"הַיּוֹם {num} {noun} שֶׁהֵם {week_part} לָעוֹמֶר"

    day_part = _AND_DAYS_HEB[remainder]
    return f"הַיּוֹם {num} {noun} שֶׁהֵם {week_part} {day_part} לָעוֹמֶר"


def get_count_transliteration(day: int) -> str:
    """Build the transliterated counting text for the given Omer day (1-49)."""
    num = _translit_number(day)
    noun = _day_noun_tr(day)
    weeks = day // 7
    remainder = day % 7

    if day < 7:
        return f"HaYom {num} {noun} la'Omer."

    week_part = _WEEK_TR[weeks]
    if remainder == 0:
        return f"HaYom {num} {noun} shehem {week_part} la'Omer."

    day_part = _AND_DAYS_TR[remainder]
    return f"HaYom {num} {noun} shehem {week_part} {day_part} la'Omer."


# Omer start dates: the Gregorian date on whose evening we count day 1 (16 Nisan)
_OMER_STARTS = {
    2025: date(2025, 4, 13),
    2026: date(2026, 4, 2),
    2027: date(2027, 4, 22),
    2028: date(2028, 4, 11),
    2029: date(2029, 3, 31),
    2030: date(2030, 4, 18),
}


def get_omer_start(year: int) -> date:
    return _OMER_STARTS.get(year, date(year, 4, 10))


def get_omer_day(today: date) -> int | None:
    """
    Return the Omer day number (1-49) for the given date's evening, or None
    if outside the Omer period.
    """
    start = get_omer_start(today.year)
    day = (today - start).days + 1
    return day if 1 <= day <= 49 else None


def format_night_message(day: int) -> str:
    """Format the full nightly WhatsApp reminder with bracha and count."""
    weeks, remainder = divmod(day, 7)
    if weeks == 0:
        summary = f"Night {day} of the Omer"
    elif remainder == 0:
        weeks = day // 7
        summary = f"Night {day} of the Omer ({weeks} week{'s' if weeks > 1 else ''})"
    else:
        summary = (
            f"Night {day} of the Omer "
            f"({weeks} week{'s' if weeks > 1 else ''} and "
            f"{remainder} day{'s' if remainder > 1 else ''})"
        )

    return (
        f"✨ *{summary}*\n\n"
        f"*Bracha:*\n{BRACHA_HEBREW}\n\n"
        f"_{BRACHA_TRANSLITERATION}_\n\n"
        f"*Count:*\n{get_count_hebrew(day)}\n\n"
        f"_{get_count_transliteration(day)}_\n\n"
        f"Reply *YES* when you've counted."
    )


def format_morning_message(day: int) -> str:
    """Format the morning follow-up (no bracha) for a missed night."""
    weeks, remainder = divmod(day, 7)
    if weeks == 0:
        summary = f"Day {day} of the Omer"
    elif remainder == 0:
        weeks = day // 7
        summary = f"Day {day} of the Omer ({weeks} week{'s' if weeks > 1 else ''})"
    else:
        summary = (
            f"Day {day} of the Omer "
            f"({weeks} week{'s' if weeks > 1 else ''} and "
            f"{remainder} day{'s' if remainder > 1 else ''})"
        )

    return (
        f"⏰ *You missed last night — count now WITHOUT a bracha*\n\n"
        f"*{summary}*\n\n"
        f"*Count (no bracha):*\n{get_count_hebrew(day)}\n\n"
        f"_{get_count_transliteration(day)}_\n\n"
        f"Reply *YES* when you've counted."
    )
