"""Tests for Omer day calculation and message formatting."""

from datetime import date

import pytest

from app.omer import (
    format_morning_message,
    format_night_message,
    get_count_hebrew,
    get_count_transliteration,
    get_omer_day,
    get_omer_start,
    BRACHA_HEBREW,
)


class TestGetOmerStart:
    def test_known_year_2026(self):
        assert get_omer_start(2026) == date(2026, 4, 2)

    def test_known_year_2025(self):
        assert get_omer_start(2025) == date(2025, 4, 13)

    def test_unknown_year_returns_fallback(self):
        result = get_omer_start(2050)
        assert isinstance(result, date)


class TestGetOmerDay:
    def test_first_night(self):
        assert get_omer_day(date(2026, 4, 2)) == 1

    def test_last_night(self):
        assert get_omer_day(date(2026, 5, 20)) == 49

    def test_middle_day(self):
        assert get_omer_day(date(2026, 4, 15)) == 14

    def test_before_omer_returns_none(self):
        assert get_omer_day(date(2026, 4, 1)) is None

    def test_after_omer_returns_none(self):
        assert get_omer_day(date(2026, 5, 21)) is None

    def test_day_7_is_one_week(self):
        assert get_omer_day(date(2026, 4, 8)) == 7

    def test_day_33_lag_baomer(self):
        assert get_omer_day(date(2026, 5, 4)) == 33


class TestGetCountHebrew:
    def test_day_1(self):
        result = get_count_hebrew(1)
        assert "אֶחָד" in result
        assert "לָעוֹמֶר" in result

    def test_day_7_includes_week(self):
        result = get_count_hebrew(7)
        assert "שָׁבוּעַ אֶחָד" in result
        assert "לָעוֹמֶר" in result

    def test_day_8_includes_week_and_day(self):
        result = get_count_hebrew(8)
        assert "שָׁבוּעַ אֶחָד" in result
        assert "וְיוֹם אֶחָד" in result

    def test_day_14_two_weeks(self):
        result = get_count_hebrew(14)
        assert "שְׁנֵי שָׁבוּעוֹת" in result

    def test_day_49_seven_weeks(self):
        result = get_count_hebrew(49)
        assert "שִׁבְעָה שָׁבוּעוֹת" in result

    def test_all_49_days_produce_output(self):
        for day in range(1, 50):
            result = get_count_hebrew(day)
            assert result.startswith("הַיּוֹם")
            assert result.endswith("לָעוֹמֶר")


class TestGetCountTransliteration:
    def test_day_1(self):
        result = get_count_transliteration(1)
        assert result.startswith("HaYom")
        assert "la'Omer" in result

    def test_day_7_includes_week(self):
        result = get_count_transliteration(7)
        assert "shavua echad" in result

    def test_day_14_two_weeks(self):
        result = get_count_transliteration(14)
        assert "shnei shavuot" in result

    def test_all_49_days_produce_output(self):
        for day in range(1, 50):
            result = get_count_transliteration(day)
            assert result.startswith("HaYom")
            assert result.endswith("la'Omer.")


class TestFormatNightMessage:
    def test_includes_bracha(self):
        msg = format_night_message(1)
        assert BRACHA_HEBREW in msg

    def test_includes_reply_prompt(self):
        msg = format_night_message(10)
        assert "YES" in msg

    def test_includes_night_number(self):
        msg = format_night_message(33)
        assert "33" in msg

    def test_includes_week_breakdown(self):
        msg = format_night_message(15)
        assert "2 weeks" in msg
        assert "1 day" in msg


class TestFormatMorningMessage:
    def test_no_bracha_in_morning(self):
        msg = format_morning_message(5)
        assert BRACHA_HEBREW not in msg

    def test_includes_warning(self):
        msg = format_morning_message(5)
        assert "WITHOUT a bracha" in msg

    def test_includes_count_text(self):
        msg = format_morning_message(10)
        assert "la'Omer" in msg

    def test_includes_reply_prompt(self):
        msg = format_morning_message(10)
        assert "YES" in msg
