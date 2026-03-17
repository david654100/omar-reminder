"""Zmanim utilities: tzet hakochavim calculation and Shabbat/Yom Tov detection."""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from zmanim.zmanim_calendar import ZmanimCalendar
from zmanim.util.geo_location import GeoLocation

from app import config


def _get_geo_location() -> GeoLocation:
    return GeoLocation(
        config.LOCATION_NAME,
        config.LATITUDE,
        config.LONGITUDE,
        config.TIMEZONE,
        elevation=0,
    )


def get_tzet_hakochavim(for_date: date) -> datetime | None:
    """
    Calculate tzet hakochavim (nightfall — 8.5 degrees below horizon)
    for the given date at the configured location.
    Returns a timezone-aware datetime, or None if it can't be calculated.
    """
    geo = _get_geo_location()
    cal = ZmanimCalendar(geo_location=geo, date=for_date)
    tzet = cal.tzais()
    if tzet is None:
        return None
    tz = ZoneInfo(config.TIMEZONE)
    if tzet.tzinfo is None:
        return tzet.replace(tzinfo=tz)
    return tzet.astimezone(tz)


def is_shabbat(for_date: date) -> bool:
    """Check if the evening of for_date is Shabbat (i.e. for_date is Friday)."""
    return for_date.weekday() == 4


def is_shabbat_morning(for_date: date) -> bool:
    """Check if for_date is a Saturday morning (Shabbat day)."""
    return for_date.weekday() == 5


# Known Yom Tov evenings during/near the Omer period (diaspora).
_YOM_TOV_DATES: dict[int, set[date]] = {
    2025: {
        date(2025, 4, 18), date(2025, 4, 19),
        date(2025, 6, 1), date(2025, 6, 2),
    },
    2026: {
        date(2026, 4, 7), date(2026, 4, 8),
        date(2026, 5, 21), date(2026, 5, 22),
    },
    2027: {
        date(2027, 4, 27), date(2027, 4, 28),
        date(2027, 6, 10), date(2027, 6, 11),
    },
    2028: {
        date(2028, 4, 16), date(2028, 4, 17),
        date(2028, 5, 30), date(2028, 5, 31),
    },
    2029: {
        date(2029, 4, 5), date(2029, 4, 6),
        date(2029, 5, 19), date(2029, 5, 20),
    },
    2030: {
        date(2030, 4, 23), date(2030, 4, 24),
        date(2030, 6, 6), date(2030, 6, 7),
    },
}


def is_yom_tov_evening(for_date: date) -> bool:
    """Check if the evening of for_date is Yom Tov (holiday night)."""
    return for_date in _YOM_TOV_DATES.get(for_date.year, set())


def is_yom_tov_morning(for_date: date) -> bool:
    """Check if the morning of for_date is Yom Tov day."""
    yesterday = for_date - timedelta(days=1)
    return is_yom_tov_evening(yesterday)


def should_skip_evening(for_date: date) -> bool:
    """Return True if we should NOT send the evening reminder on for_date."""
    return is_shabbat(for_date) or is_yom_tov_evening(for_date)


def should_skip_morning(for_date: date) -> bool:
    """Return True if we should NOT send the morning reminder on for_date."""
    return is_shabbat_morning(for_date) or is_yom_tov_morning(for_date)
