# Crontab Syntax Features

## Exit Codes

The `checkcrontab` command returns the following exit codes:

- **0** - Success: No errors found in any checked files
- **1** - Errors found: One or more syntax errors detected in crontab files
- **2** - System error: File access issues, permission problems, or other system-level errors

### Examples

```bash
# Success - no errors
checkcrontab examples/user_valid.txt
echo $?  # Returns 0

# Errors found
checkcrontab examples/user_incorrect.txt
echo $?  # Returns 1

# System error (file not found)
checkcrontab nonexistent_file.txt
echo $?  # Returns 2

# JSON output
checkcrontab --json examples/user_valid.txt
```

### JSON Output Format

When using `--json` flag, the output is structured as follows:

```json
{
  "success": boolean,
  "total_files": number,
  "total_rows": number,
  "total_rows_errors": number,
  "total_errors": number,
  "files": [
    {
      "file": "string",
      "is_system_crontab": boolean,
      "rows": number,
      "rows_errors": number,
      "errors_count": number,
      "errors": ["string"],
      "success": boolean
    }
  ]
}
```

## Platform Support

### Linux/macOS (Full Support)
- System crontab validation (`/etc/crontab`)
- User crontab validation (via `crontab -l -u username`)
- User existence validation
- Daemon/service checks via systemctl
- All crontab syntax features

### Windows (Limited Support)
- File-based crontab syntax validation
- No user existence checks
- No system crontab access
- No daemon/service checks
- All crontab syntax features supported

### Cross-Platform Features
- Syntax validation for all time fields
- Special keyword validation
- Dangerous command detection
- Environment variable validation
- Multi-line command support

## Supported Crontab Syntax

### Basic Format

**User Crontab:**
```
minute hour day month weekday command
```

**System Crontab:**
```
minute hour day month weekday user command
```

### Time Fields

#### Minutes (0-59)
- Single value: `30`
- Range: `0-30`
- List: `0,15,30,45`
- Step: `*/15` (every 15 minutes)
- All: `*`

#### Hours (0-23)
- Single value: `14`
- Range: `9-17`
- List: `0,6,12,18`
- Step: `*/3` (every 3 hours)
- All: `*`

#### Day of Month (1-31)
- Single value: `15`
- Range: `1-15`
- List: `1,15,30`
- Step: `*/2` (every 2 days)
- All: `*`

#### Month (1-12)
- Single value: `6`
- Range: `1-6`
- List: `1,6,12`
- Step: `*/3` (every 3 months)
- All: `*`

#### Day of Week (0-7, where 0 and 7 are Sunday)
- Single value: `1` (Monday)
- Range: `1-5` (Monday to Friday)
- List: `1,3,5` (Monday, Wednesday, Friday)
- Step: `*/2` (every 2 days)
- All: `*`

### Special Keywords

#### User Crontab
```
@reboot    command
@yearly    command
@annually  command
@monthly   command
@weekly    command
@daily     command
@hourly    command
```

#### System Crontab
```
@reboot    user command
@yearly    user command
@annually  user command
@monthly   user command
@weekly    user command
@daily     user command
@hourly    user command
```

### Environment Variables
```
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAILTO=user@example.com
HOME=/home/user
```

### Multi-line Commands
```
0 2 * * * /usr/bin/script.sh \
    && /usr/bin/another_script.sh \
    || echo "Error occurred"
```

### System Crontab Specific Features

#### Dash Prefix (Syslog Suppression)
```
-0 2 * * * root /usr/bin/backup.sh
```
The `-` prefix before the minute field suppresses syslog logging.

#### User Field Validation
- Must be a valid system user
- Cannot contain spaces, quotes, or special characters
- On Linux/macOS: User must exist in the system

## Validation Rules

### Time Field Validation
- Values must be within valid ranges
- Negative values are not allowed
- Non-numeric values are not allowed
- Ranges must be in ascending order (e.g., `1-5`, not `5-1`)
- Steps must be positive integers

### Command Field Validation
- Command field is required
- Dangerous commands are detected and flagged
- Multi-line commands are supported with `\` continuation

### User Field Validation (System Crontab)
- User field is required
- User must be a valid username format
- On Linux/macOS: User existence is verified
- On Windows: User existence checks are skipped

### Special Keyword Validation
- Keywords are case-sensitive (must be lowercase)
- Command is required after keyword
- User field is required for system crontab
- Extra arguments are allowed as part of the command

## Error Messages

### Time Field Errors
- `Invalid minutes value: X` - Value outside 0-59 range
- `Invalid hours value: X` - Value outside 0-23 range
- `Invalid day of month value: X` - Value outside 1-31 range
- `Invalid month value: X` - Value outside 1-12 range
- `Invalid day of week value: X` - Value outside 0-7 range

### Structure Errors
- `Insufficient fields for user crontab` - Less than 6 fields
- `Insufficient fields for system crontab` - Less than 7 fields
- `Too many fields for user crontab` - More than 6 fields
- `Too many fields for system crontab` - More than 7 fields

### User Field Errors
- `Invalid user field format` - Contains invalid characters
- `User does not exist: username` - User not found (Linux/macOS only)

### Command Field Errors
- `Missing command field` - No command specified
- `Dangerous command detected: command` - Potentially harmful command

### Special Keyword Errors
- `Invalid special keyword: @keyword` - Unknown keyword
- `Missing command for special keyword` - No command after keyword
- `Missing user field for system crontab special keyword` - No user specified

## Examples

### Valid User Crontab Entries
```
# Basic entry
0 2 * * * /usr/bin/backup.sh

# With step values
*/15 * * * * /usr/bin/monitor.sh

# With ranges
0 8-17 * * 1-5 /usr/bin/business_hours.sh

# Special keyword
@reboot /usr/bin/startup.sh

# Environment variable
SHELL=/bin/bash
```

### Valid System Crontab Entries
```
# Basic entry
0 2 * * * root /usr/bin/backup.sh

# With dash prefix
-0 2 * * * root /usr/bin/backup.sh

# Special keyword
@reboot root /usr/bin/startup.sh

# Environment variable
SHELL=/bin/sh
```

### Invalid Entries
```
# Invalid minutes
60 * * * * /usr/bin/script.sh

# Missing command
0 2 * * *

# Invalid special keyword
@invalid /usr/bin/script.sh

# Invalid user (system crontab)
0 2 * * * invalid_user /usr/bin/script.sh
```
