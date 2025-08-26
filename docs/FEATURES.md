# Checkcrontab Features Documentation

## Purpose & Overview

Checkcrontab is a cross-platform Python tool designed to validate crontab file syntax and detect common configuration errors. It supports both system crontab files (with user fields) and user crontab files, providing comprehensive validation across Linux, macOS, and Windows platforms.

### Intended Use Cases

- **CI/CD Pipeline Integration**: Validate crontab configurations before deployment
- **Configuration Management**: Ensure crontab files comply with proper syntax
- **System Administration**: Detect dangerous commands and invalid schedules
- **Development**: Validate cron jobs during development and testing

## Supported Syntax

### Time Field Format

Crontab entries use five time fields followed by a command:

```
minute hour day month weekday command
```

For system crontab files, a user field is required:

```
minute hour day month weekday user command
```

### Wildcards

- `*` - Matches any value in the field
- Examples: `* * * * * /usr/bin/script.sh` (every minute)

### Ranges

- `A-B` - Specifies a range from A to B (inclusive)
- Examples:
  - `0 9-17 * * * /usr/bin/work_hours.sh` (9 AM to 5 PM)
  - `0 0 1-15 * * /usr/bin/first_half.sh` (first half of month)

### Lists

- `A,B,C` - Comma-separated list of values
- Examples:
  - `0 0 * * 1,3,5 /usr/bin/mwf.sh` (Monday, Wednesday, Friday)
  - `0 6,12,18 * * * /usr/bin/3times.sh` (6 AM, noon, 6 PM)

### Steps

- `*/N` - Every N units
- `A-B/N` - Every N units within range A-B
- Examples:
  - `*/15 * * * * /usr/bin/quarter.sh` (every 15 minutes)
  - `0 9-17/2 * * * /usr/bin/work.sh` (every 2 hours from 9 AM to 5 PM)

### Special Keywords

Special scheduling keywords can replace the five time fields:

- `@reboot` - Run once at startup
- `@yearly` or `@annually` - Run once a year (0 0 1 1 *)
- `@monthly` - Run once a month (0 0 1 * *)
- `@weekly` - Run once a week (0 0 * * 0)
- `@daily` or `@midnight` - Run once a day (0 0 * * *)
- `@hourly` - Run once an hour (0 * * * *)

Examples:
```bash
@reboot /usr/bin/startup.sh
@daily /usr/bin/backup.sh
@weekly /usr/bin/maintenance.sh
```

### Environment Variables

Crontab files can set environment variables:

```bash
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
MAILTO=admin@example.com
```

### Multi-line Commands

Commands can span multiple lines using backslash continuation:

```bash
0 2 * * * /usr/bin/backup.sh \
    --verbose \
    --destination /backup/dir
```

### System Crontab Specifics

- **User Field**: Required between weekday and command
- **Dash Prefix**: Optional `-` prefix to suppress syslog logging
- **File Permissions**: Should have 644 permissions

### Comments

Lines starting with `#` are treated as comments and ignored.

## Valid Values

### Time Field Ranges

| Field | Range | Alternative Names |
|-------|-------|-------------------|
| Minute | 0-59 | None |
| Hour | 0-23 | None |
| Day of Month | 1-31 | None |
| Month | 1-12 | jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec |
| Day of Week | 0-7 | sun, mon, tue, wed, thu, fri, sat (0 and 7 = Sunday) |

### Edge Cases and Boundary Values

- **Minute**: 0 (top of hour), 59 (last minute)
- **Hour**: 0 (midnight), 23 (11 PM)
- **Day**: 1 (first of month), 31 (last day - validated per month)
- **Month**: 1 (January), 12 (December)
- **Weekday**: 0 or 7 (Sunday), 6 (Saturday)

### Step Value Constraints

- Step values must be positive integers
- Step values cannot exceed the maximum value for the field
- Examples: `*/60` is invalid for minutes (max 59), `*/25` is invalid for hours (max 23)

## Examples

### Valid Examples

1. **Daily backup at 2 AM**
   ```bash
   0 2 * * * /usr/bin/backup.sh
   ```
   *Runs every day at 2:00 AM*

2. **Weekday business hours check**
   ```bash
   0 9-17 * * 1-5 /usr/bin/check_services.sh
   ```
   *Runs hourly from 9 AM to 5 PM, Monday through Friday*

3. **Monthly report on first day**
   ```bash
   0 0 1 * * /usr/bin/monthly_report.sh
   ```
   *Runs at midnight on the first day of every month*

4. **Every 15 minutes during peak hours**
   ```bash
   */15 9-17 * * * /usr/bin/monitor.sh
   ```
   *Runs every 15 minutes from 9 AM to 5 PM*

5. **Weekend maintenance**
   ```bash
   0 3 * * 0,6 /usr/bin/maintenance.sh
   ```
   *Runs at 3 AM on Saturdays and Sundays*

6. **System crontab with user field**
   ```bash
   0 2 * * * root /usr/bin/system_backup.sh
   ```
   *System crontab: runs as root at 2 AM daily*

### Invalid Examples

1. **Invalid minute value**
   ```bash
   60 * * * * /usr/bin/script.sh
   ```
   *Error: Minute must be 0-59*

2. **Missing required fields**
   ```bash
   0 2 * * /usr/bin/backup.sh
   ```
   *Error: User crontab requires 6 fields minimum*

3. **Invalid range order**
   ```bash
   0 17-9 * * * /usr/bin/script.sh
   ```
   *Error: Range start cannot be greater than end*

4. **Invalid step value**
   ```bash
   */60 * * * * /usr/bin/script.sh
   ```
   *Error: Step value 60 exceeds maximum 59 for minutes*

5. **Empty command**
   ```bash
   0 2 * * *
   ```
   *Error: Command field is required*

## Error Messages Reference

| Error Message | Trigger Condition | Example Input | Suggested Fix |
|---------------|-------------------|---------------|---------------|
| `insufficient fields (minimum X required for Y crontab, found Z)` | Wrong number of fields | `0 2 * *` | Add missing time fields or command |
| `value X out of bounds (min-max) for field: 'value'` | Field value outside valid range | `60 * * * *` | Use value within valid range (0-59 for minutes) |
| `invalid field format: 'value'` | Non-numeric or malformed field | `abc * * * *` | Use numeric values or valid patterns |
| `invalid special keyword: '@value'` | Unknown special keyword | `@invalid command` | Use valid keywords (@reboot, @daily, etc.) |
| `dangerous command: 'command'` | Potentially harmful command detected | `rm -rf /` | Review command for safety |
| `empty value in field list: 'value'` | Empty element in comma list | `1,,3 * * * *` | Remove empty commas or add values |
| `step value X exceeds maximum Y for field: 'value'` | Step larger than field maximum | `*/60 * * * *` | Use step value ≤ field maximum |
| `invalid range X-Y in field: start > end` | Range start greater than end | `5-3 * * * *` | Ensure range start ≤ end |
| `duplicate value 'X' in field list: 'value'` | Repeated value in comma list | `1,1,2 * * * *` | Remove duplicate values |
| `invalid user field format: 'value'` | Malformed user field (system crontab) | `"root user" command` | Use simple username without quotes/spaces |
| `insufficient fields for system crontab special keyword (minimum 3 required)` | Missing user/command in system special | `@reboot command` | Add user field: `@reboot root command` |
| `user field not allowed in user crontab special keyword: 'user'` | User field in user crontab special | `@reboot root command` | Remove user field: `@reboot command` |
| `File should end with newline` | File doesn't end with newline | (file without final \n) | Add newline at end of file |
| `step value must be positive in field: 'value'` | Zero or negative step value | `*/-1 * * * *` | Use positive step values only |

### Common Error Patterns

- **Field Validation**: Each time field is validated against its specific range and format
- **Structural Validation**: Proper number of fields for crontab type (user vs system)
- **Semantic Validation**: Logical consistency (range order, step values)
- **Security Validation**: Detection of potentially dangerous commands
- **Format Validation**: Proper syntax for ranges, lists, and steps

### Platform-Specific Considerations

- **Linux/macOS**: User existence validation for system crontabs
- **Windows**: Limited cron daemon detection capabilities
- **Cross-platform**: File permission checks adapted per platform

## Integration Examples

### CI/CD Usage

```bash
# Validate all crontab files in project
checkcrontab cron/*.cron

# Validate with debug output
checkcrontab --debug production.cron

# Check multiple users
checkcrontab -u www-data -u backup
```

### Development Workflow

```bash
# Quick syntax check
checkcrontab my-crontab.txt

# Validate system crontab format
checkcrontab -S system-crontab.txt

# Check with explicit type flags
checkcrontab -S sys.cron -U user.cron
```