#!/usr/bin/env python3
# mypy: ignore-errors

from checkcrontab.checker import check_line


class TestInvalidUserCrontab:
    """Test invalid user crontab entries"""

    def test_insufficient_fields(self):
        """Test insufficient fields"""
        # Only 5 fields (missing command)
        errors, warnings = check_line("0 2 * * *", 1, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Only 4 fields
        errors, warnings = check_line("0 2 * * /usr/bin/backup.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Only 3 fields
        errors, warnings = check_line("0 2 * /usr/bin/backup.sh", 3, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Only 2 fields
        errors, warnings = check_line("0 2 /usr/bin/backup.sh", 4, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Only 1 field
        errors, warnings = check_line("0 /usr/bin/backup.sh", 5, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Empty line (no fields)
        errors, warnings = check_line("/usr/bin/backup.sh", 6, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

    def test_invalid_time_values(self):
        """Test invalid time values"""
        # Invalid minutes (60)
        errors, warnings = check_line("60 * * * * /usr/bin/script.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Invalid hours (24)
        errors, warnings = check_line("* 24 * * * /usr/bin/script.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Invalid day of month (32)
        errors, warnings = check_line("* * 32 * * /usr/bin/script.sh", 3, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Invalid month (13)
        errors, warnings = check_line("* * * 13 * /usr/bin/script.sh", 4, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Invalid day of week (8)
        errors, warnings = check_line("* * * * 8 /usr/bin/script.sh", 5, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

    def test_negative_values(self):
        """Test negative values"""
        # Negative values
        errors, warnings = check_line("-1 * * * * /usr/bin/script.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* -1 * * * /usr/bin/script.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * -1 * * /usr/bin/script.sh", 3, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * * -1 * /usr/bin/script.sh", 4, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * * * -1 /usr/bin/script.sh", 5, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

    def test_non_numeric_values(self):
        """Test non-numeric values"""
        # Non-numeric values
        errors, warnings = check_line("abc * * * * /usr/bin/script.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* abc * * * /usr/bin/script.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * abc * * /usr/bin/script.sh", 3, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * * abc * /usr/bin/script.sh", 4, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * * * abc /usr/bin/script.sh", 5, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

    def test_empty_values(self):
        """Test empty values"""
        # Empty values
        errors, warnings = check_line(" * * * * /usr/bin/script.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("*  * * * /usr/bin/script.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* *  * * /usr/bin/script.sh", 3, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * *  * /usr/bin/script.sh", 4, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * * *  /usr/bin/script.sh", 5, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

    def test_values_with_letters(self):
        """Test values with letters"""
        # Values with letters
        errors, warnings = check_line("1a * * * * /usr/bin/script.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* 1a * * * /usr/bin/script.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * 1a * * /usr/bin/script.sh", 3, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * * 1a * /usr/bin/script.sh", 4, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * * * 1a /usr/bin/script.sh", 5, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

    def test_values_with_symbols(self):
        """Test values with symbols"""
        # Values with symbols
        errors, warnings = check_line("1@ * * * * /usr/bin/script.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* 1@ * * * /usr/bin/script.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * 1@ * * /usr/bin/script.sh", 3, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * * 1@ * /usr/bin/script.sh", 4, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("* * * * 1@ /usr/bin/script.sh", 5, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

    def test_invalid_special_keywords(self):
        """Test invalid special keywords"""
        # Invalid special keyword
        errors, warnings = check_line("@invalid /usr/bin/script.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Case sensitive (should be lowercase)
        errors, warnings = check_line("@Reboot /usr/bin/script.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        errors, warnings = check_line("@REBOOT /usr/bin/script.sh", 3, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Invalid special keyword with extra text
        errors, warnings = check_line("@reboot_extra /usr/bin/script.sh", 4, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Missing command for special keyword
        errors, warnings = check_line("@reboot", 5, "test.txt", is_system_crontab=False)
        assert len(errors) > 0

        # Just @ symbol
        errors, warnings = check_line("@", 6, "test.txt", is_system_crontab=False)
        assert len(errors) > 0
