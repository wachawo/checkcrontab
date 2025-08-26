#!/usr/bin/env python3
# mypy: ignore-errors

from checkcrontab.checker import check_line


class TestInvalidSystemCrontab:
    """Test invalid system crontab entries"""

    def test_insufficient_fields(self):
        """Test insufficient fields"""
        # Missing user field (only 6 fields instead of 7)
        errors = check_line("0 2 * * * /usr/bin/backup.sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Missing command (only 6 fields)
        errors = check_line("0 2 * * * root", 2, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Only 5 fields
        errors = check_line("0 2 * * * /usr/bin/backup.sh", 3, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Only 4 fields
        errors = check_line("0 2 * * /usr/bin/backup.sh", 4, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Only 3 fields
        errors = check_line("0 2 * /usr/bin/backup.sh", 5, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Only 2 fields
        errors = check_line("0 2 /usr/bin/backup.sh", 6, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Only 1 field
        errors = check_line("0 /usr/bin/backup.sh", 7, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

    def test_invalid_time_values(self):
        """Test invalid time values"""
        # Invalid minutes (60)
        errors = check_line("60 * * * * root /usr/bin/script.sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Invalid hours (24)
        errors = check_line("* 24 * * * root /usr/bin/script.sh", 2, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Invalid day of month (32)
        errors = check_line("* * 32 * * root /usr/bin/script.sh", 3, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Invalid month (13)
        errors = check_line("* * * 13 * root /usr/bin/script.sh", 4, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Invalid day of week (8)
        errors = check_line("* * * * 8 root /usr/bin/script.sh", 5, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

    def test_negative_values(self):
        """Test negative values"""
        # Negative values
        errors = check_line("* -1 * * * root /usr/bin/script.sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        errors = check_line("* * -1 * * * root /usr/bin/script.sh", 2, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        errors = check_line("* * * -1 * * root /usr/bin/script.sh", 3, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        errors = check_line("* * * * -1 root /usr/bin/script.sh", 4, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

    def test_non_numeric_values(self):
        """Test non-numeric values"""
        # Non-numeric values
        errors = check_line("abc * * * * root /usr/bin/script.sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        errors = check_line("* abc * * * root /usr/bin/script.sh", 2, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        errors = check_line("* * abc * * * root /usr/bin/script.sh", 3, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        errors = check_line("* * * abc * * root /usr/bin/script.sh", 4, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        errors = check_line("* * * * abc root /usr/bin/script.sh", 5, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

    def test_invalid_special_keywords(self):
        """Test invalid special keywords"""
        # Invalid special keyword
        errors = check_line("@invalid root /usr/bin/script.sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Case sensitive (should be lowercase)
        errors = check_line("@Reboot root /usr/bin/script.sh", 2, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        errors = check_line("@REBOOT root /usr/bin/script.sh", 3, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Invalid special keyword with extra text
        errors = check_line("@reboot_extra root /usr/bin/script.sh", 4, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Missing command for special keyword
        errors = check_line("@reboot root", 5, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Missing user for special keyword
        errors = check_line("@reboot /usr/bin/script.sh", 6, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

    def test_invalid_ranges(self):
        """Test invalid ranges"""
        # Range with incorrect order (start > end)
        errors = check_line("0 5-3 * * * root /usr/bin/script.sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Range with non-numeric values
        errors = check_line("0 a-z * * * root /usr/bin/script.sh", 2, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Range with empty values
        errors = check_line("0 - * * * root /usr/bin/script.sh", 3, "test.txt", is_system_crontab=True)
        assert len(errors) > 0

        # Range with symbols
        errors = check_line("0 1-@ * * * root /usr/bin/script.sh", 4, "test.txt", is_system_crontab=True)
        assert len(errors) > 0
