#!/usr/bin/env python3
# mypy: ignore-errors

from checkcrontab.checker import check_line


class TestValidUserCrontab:
    """Test valid user crontab entries"""

    def test_valid_step_values_minutes(self):
        """Test valid step values for minutes"""
        # */15 * * * * /usr/bin/script.sh
        errors, warnings = check_line("*/15 * * * * /usr/bin/script.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # */30 * * * * /usr/bin/script.sh
        errors, warnings = check_line("*/30 * * * * /usr/bin/script.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # */45 * * * * /usr/bin/script.sh
        errors, warnings = check_line("*/45 * * * * /usr/bin/script.sh", 3, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

    def test_valid_special_keywords(self):
        """Test valid special keywords"""
        # @reboot /usr/bin/script.sh
        errors, warnings = check_line("@reboot /usr/bin/script.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # @reboot /usr/bin/script.sh arg1 arg2
        errors, warnings = check_line("@reboot /usr/bin/script.sh arg1 arg2", 2, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # @yearly /usr/bin/script.sh
        errors, warnings = check_line("@yearly /usr/bin/script.sh", 3, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # @monthly /usr/bin/script.sh
        errors, warnings = check_line("@monthly /usr/bin/script.sh", 4, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # @weekly /usr/bin/script.sh
        errors, warnings = check_line("@weekly /usr/bin/script.sh", 5, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # @daily /usr/bin/script.sh
        errors, warnings = check_line("@daily /usr/bin/script.sh", 6, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # @hourly /usr/bin/script.sh
        errors, warnings = check_line("@hourly /usr/bin/script.sh", 7, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

    def test_valid_regular_crontab_lines(self):
        """Test valid regular crontab lines"""
        # 0 2 * * * /usr/bin/backup.sh
        errors, warnings = check_line("0 2 * * * /usr/bin/backup.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # 0 2 * * * /usr/bin/script.sh && echo "backup completed"
        errors, warnings = check_line('0 2 * * * /usr/bin/script.sh && echo "backup completed"', 2, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

    def test_valid_ranges(self):
        """Test valid ranges"""
        # 0 2-4 * * * /usr/bin/nightly_task.sh
        errors, warnings = check_line("0 2-4 * * * /usr/bin/nightly_task.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # 0 8-17 * * 1-5 /usr/bin/business_hours.sh
        errors, warnings = check_line("0 8-17 * * 1-5 /usr/bin/business_hours.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

    def test_valid_lists(self):
        """Test valid lists"""
        # 0 2,4,6,8,10,12,14,16,18,20,22 * * * /usr/bin/even_hours.sh
        errors, warnings = check_line("0 2,4,6,8,10,12,14,16,18,20,22 * * * /usr/bin/even_hours.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # 0 0 1,15 * * /usr/bin/biweekly_task.sh
        errors, warnings = check_line("0 0 1,15 * * /usr/bin/biweekly_task.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

    def test_valid_steps_and_ranges(self):
        """Test valid steps and ranges"""
        # 0 */3 * * * /usr/bin/every_3_hours.sh
        errors, warnings = check_line("0 */3 * * * /usr/bin/every_3_hours.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # 0 0 */2 * * /usr/bin/every_2_days.sh
        errors, warnings = check_line("0 0 */2 * * /usr/bin/every_2_days.sh", 2, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

    def test_valid_environment_variables(self):
        """Test valid environment variables"""
        # SHELL=/bin/bash
        errors, warnings = check_line("SHELL=/bin/bash", 1, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        errors, warnings = check_line("PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", 2, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

        # MAILTO=user@example.com
        errors, warnings = check_line("MAILTO=user@example.com", 3, "test.txt", is_system_crontab=False)
        assert len(errors) == 0

    def test_multiple_lines(self):
        """Test multiple valid lines"""
        # 15 3 * * * /usr/bin/daily_task.sh \ && /usr/bin/another_task.sh
        errors, warnings = check_line("15 3 * * * /usr/bin/daily_task.sh \\\n      && /usr/bin/another_task.sh", 1, "test.txt", is_system_crontab=False)
        assert len(errors) == 0
