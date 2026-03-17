"""Tests for zmanim calculations and Shabbat/Yom Tov detection."""

from datetime import date

import pytest

from app.zmanim import (
    get_tzet_hakochavim,
    is_shabbat,
    is_shabbat_morning,
    is_yom_tov_evening,
    is_yom_tov_morning,
    should_skip_evening,
    should_skip_morning,
)


class TestIsShabbat:
    def test_friday_is_shabbat_evening(self):
        assert is_shabbat(date(2026, 4, 3)) is True  # Friday

    def test_saturday_is_not_shabbat_evening(self):
        assert is_shabbat(date(2026, 4, 4)) is False

    def test_thursday_is_not_shabbat(self):
        assert is_shabbat(date(2026, 4, 2)) is False


class TestIsShabbatMorning:
    def test_saturday_is_shabbat_morning(self):
        assert is_shabbat_morning(date(2026, 4, 4)) is True

    def test_friday_is_not_shabbat_morning(self):
        assert is_shabbat_morning(date(2026, 4, 3)) is False


class TestIsYomTovEvening:
    def test_last_days_pesach_2026(self):
        assert is_yom_tov_evening(date(2026, 4, 7)) is True
        assert is_yom_tov_evening(date(2026, 4, 8)) is True

    def test_shavuot_2026(self):
        assert is_yom_tov_evening(date(2026, 5, 21)) is True
        assert is_yom_tov_evening(date(2026, 5, 22)) is True

    def test_regular_day_not_yom_tov(self):
        assert is_yom_tov_evening(date(2026, 4, 15)) is False

    def test_unknown_year(self):
        assert is_yom_tov_evening(date(2050, 4, 15)) is False


class TestIsYomTovMorning:
    def test_day_after_yom_tov_evening(self):
        assert is_yom_tov_morning(date(2026, 4, 8)) is True

    def test_regular_day(self):
        assert is_yom_tov_morning(date(2026, 4, 15)) is False


class TestShouldSkipEvening:
    def test_skip_friday(self):
        assert should_skip_evening(date(2026, 4, 3)) is True

    def test_skip_yom_tov(self):
        assert should_skip_evening(date(2026, 4, 7)) is True

    def test_dont_skip_regular_day(self):
        assert should_skip_evening(date(2026, 4, 6)) is False


class TestShouldSkipMorning:
    def test_skip_saturday(self):
        assert should_skip_morning(date(2026, 4, 4)) is True

    def test_skip_yom_tov_morning(self):
        assert should_skip_morning(date(2026, 4, 8)) is True

    def test_dont_skip_regular_morning(self):
        assert should_skip_morning(date(2026, 4, 6)) is False


class TestGetTzetHakochavim:
    def test_returns_datetime_for_minneapolis(self):
        tzet = get_tzet_hakochavim(date(2026, 4, 15))
        assert tzet is not None
        assert tzet.hour >= 19  # should be evening in Minneapolis in April

    def test_timezone_aware(self):
        tzet = get_tzet_hakochavim(date(2026, 4, 15))
        assert tzet is not None
        assert tzet.tzinfo is not None

    def test_later_in_spring_is_later(self):
        early = get_tzet_hakochavim(date(2026, 4, 5))
        late = get_tzet_hakochavim(date(2026, 5, 15))
        assert early is not None and late is not None
        assert late.hour >= early.hour
