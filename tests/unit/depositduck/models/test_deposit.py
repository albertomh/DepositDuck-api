"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from depositduck.models.sql.deposit import Tenancy


class TestTenancy:
    days_since_tenancy_start = 400
    tenancy_duration_in_days = 390
    start_date = date.today() - timedelta(days=days_since_tenancy_start)
    end_date = start_date + timedelta(days=tenancy_duration_in_days)
    dispute_window_in_days = 60
    dispute_window_end = end_date + timedelta(days=dispute_window_in_days)

    def test_deposit_in_gbp(self):
        tenancy = Tenancy(
            deposit_in_p=12345,
            start_date=self.start_date,
            end_date=self.end_date,
            dispute_window_end=self.dispute_window_end,
        )
        assert tenancy.deposit_in_gbp == 123

    def test_invalid_deposit_in_p(self):
        negative_int = -12345
        with pytest.raises(ValidationError):
            Tenancy(
                deposit_in_p=negative_int,
                end_date=self.end_date,
                dispute_window_end=self.dispute_window_end,
            )

    def test_missing_start_date(self):
        tenancy = Tenancy(
            deposit_in_p=12345,
            end_date=self.end_date,
            dispute_window_end=self.dispute_window_end,
        )
        assert tenancy.start_date is None

    def test_days_until_dispute_window_end(self):
        tenancy = Tenancy(
            deposit_in_p=12345,
            end_date=self.end_date,
            dispute_window_end=self.dispute_window_end,
        )
        days_since_tenancy_end = (
            self.days_since_tenancy_start - self.tenancy_duration_in_days
        )
        expected_days_until_window_end = (
            self.dispute_window_in_days - days_since_tenancy_end
        )
        assert tenancy.days_until_dispute_window_end == expected_days_until_window_end

    def test_days_until_dispute_window_end_in_past(self):
        # 'dwe' = deposit window end
        tenancy_end_to_dwe_in_days = 1
        dwe_in_past = self.end_date + timedelta(days=tenancy_end_to_dwe_in_days)
        days_since_tenancy_end = (
            self.days_since_tenancy_start - self.tenancy_duration_in_days
        )
        expected_days_until_dwe = 0 - days_since_tenancy_end + tenancy_end_to_dwe_in_days
        tenancy = Tenancy(
            deposit_in_p=12345,
            end_date=self.end_date,
            dispute_window_end=dwe_in_past,
        )
        assert tenancy.days_until_dispute_window_end == expected_days_until_dwe
