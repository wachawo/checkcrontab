#!/usr/bin/env python3
# mypy: ignore-errors

from checkcrontab.checker import check_line


class TestValidSystemCrontab:
    """Test valid system crontab entries"""

    def test_valid_step_values_minutes(self):
        """Test valid step values for minutes"""
        # */13 * * * * root /usr/bin/script.sh
        errors, warnings = check_line("*/13 * * * * root /usr/bin/script.sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

        # */8 * * * * root /usr/bin/script.sh
        errors, warnings = check_line("*/8 * * * * root /usr/bin/script.sh", 2, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

        # */24 * * * * root /usr/bin/script.sh
        errors, warnings = check_line("*/24 * * * * root /usr/bin/script.sh", 3, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

        # */32 * * * * root /usr/bin/script.sh
        errors, warnings = check_line("*/32 * * * * root /usr/bin/script.sh", 4, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

    def test_valid_special_keywords(self):
        """Test valid special keywords with user and command"""
        # @reboot root /usr/bin/script.sh
        errors, warnings = check_line("@reboot root /usr/bin/script.sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

        # @reboot root /usr/bin/script.sh arg1 arg2
        errors, warnings = check_line("@reboot root /usr/bin/script.sh arg1 arg2", 2, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

    def test_valid_regular_crontab_lines(self):
        """Test valid regular crontab lines"""
        # 0 2 * * * root /usr/bin/backup.sh
        errors, warnings = check_line("0 2 * * * root /usr/bin/backup.sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

        # 0 2 * * * root /usr/bin/script.sh && echo "backup completed"
        errors, warnings = check_line('0 2 * * * root /usr/bin/script.sh && echo "backup completed"', 2, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

    def test_valid_system_crontab_with_dash_prefix(self):
        """Test valid system crontab with '-' prefix to suppress syslog logging"""
        # -0 2 * * * root - /usr/bin/backup.sh
        errors, warnings = check_line("-0 2 * * * root - /usr/bin/backup.sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

    def test_valid_environment_variables(self):
        """Test valid environment variables"""
        # SHELL=/bin/sh
        errors, warnings = check_line("SHELL=/bin/sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

        # PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        errors, warnings = check_line("PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", 2, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

        # MAILTO=root
        errors, warnings = check_line("MAILTO=root", 3, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

    def test_multiple_lines(self):
        """Test multiple valid lines"""
        # 15 3 * * * root /usr/bin/daily_task.sh \ && /usr/bin/another_task.sh
        errors, warnings = check_line("15 3 * * * root /usr/bin/daily_task.sh \\\n      && /usr/bin/another_task.sh", 1, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []

        # 15 3 * * * root \ /usr/bin/script.sh
        errors, warnings = check_line("15 3 * * * root \\\n      /usr/bin/script.sh", 2, "test.txt", is_system_crontab=True)
        assert len(errors) == 0
        assert warnings == []
