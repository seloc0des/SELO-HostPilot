# Sudo Configuration for Tier 2 Tools

This document explains how to configure passwordless sudo for specific commands used by Tier 2 tools (package installs and service management).

## Security Considerations

Tier 2 tools require sudo privileges to perform system-level operations. To use these tools safely:

1. **Sandbox Mode Required**: Tier 2 tools are only enabled when `SANDBOX_MODE` is set to `systemd` or `bwrap`
2. **Explicit Confirmation**: All Tier 2 operations require user confirmation before execution
3. **Limited Scope**: Only specific commands are allowed via sudoers configuration
4. **Audit Logging**: All Tier 2 operations are logged to the audit database

## Sudoers Configuration

To enable Tier 2 tools, add the following to your sudoers file using `sudo visudo`:

```bash
# Ollama ToolChat - Tier 2 System Management Tools
# Replace 'toolchat' with your actual username

# Package management
toolchat ALL=(ALL) NOPASSWD: /usr/bin/apt-get update
toolchat ALL=(ALL) NOPASSWD: /usr/bin/apt-get install -y *

# Service management
toolchat ALL=(ALL) NOPASSWD: /usr/bin/systemctl start *
toolchat ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop *
toolchat ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart *
```

### More Restrictive Configuration (Recommended)

For better security, limit to specific services and packages:

```bash
# Ollama ToolChat - Tier 2 System Management Tools (Restricted)
# Replace 'toolchat' with your actual username

# Only allow specific packages
toolchat ALL=(ALL) NOPASSWD: /usr/bin/apt-get update
toolchat ALL=(ALL) NOPASSWD: /usr/bin/apt-get install -y htop
toolchat ALL=(ALL) NOPASSWD: /usr/bin/apt-get install -y ncdu
toolchat ALL=(ALL) NOPASSWD: /usr/bin/apt-get install -y lm-sensors
toolchat ALL=(ALL) NOPASSWD: /usr/bin/apt-get install -y smartmontools
toolchat ALL=(ALL) NOPASSWD: /usr/bin/apt-get install -y sysstat
toolchat ALL=(ALL) NOPASSWD: /usr/bin/apt-get install -y exiftool

# Only allow specific services
toolchat ALL=(ALL) NOPASSWD: /usr/bin/systemctl start nginx
toolchat ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop nginx
toolchat ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart nginx
toolchat ALL=(ALL) NOPASSWD: /usr/bin/systemctl start docker
toolchat ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop docker
toolchat ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart docker
```

## Testing Sudo Configuration

Test your configuration without running the full application:

```bash
# Test apt commands
sudo -n apt-get update
sudo -n apt-get install -y htop

# Test systemctl commands
sudo -n systemctl status nginx
sudo -n systemctl restart nginx
```

If these commands run without prompting for a password, your configuration is correct.

## Enabling Tier 2 Tools

1. Configure sudoers as described above
2. Set `SANDBOX_MODE=systemd` or `SANDBOX_MODE=bwrap` in your `.env` file
3. Restart the application

The application will log whether Tier 2 tools are enabled:

```
INFO: Registered Tier 2 system management tools (sudo required)
```

Or if disabled:

```
INFO: Tier 2 system tools disabled (enable sandbox_mode to use)
```

## Available Tier 2 Tools

### Package Management
- **apt_install**: Install a package using apt
- **apt_update**: Update apt package lists

### Service Management
- **systemctl_restart**: Restart a systemd service
- **systemctl_start**: Start a systemd service
- **systemctl_stop**: Stop a systemd service

### Read-Only (No Sudo Required)
- **systemctl_status**: Check service status

## Security Best Practices

1. **Run as dedicated user**: Create a `toolchat` user with minimal privileges
2. **Use restrictive sudoers**: Only allow specific packages/services you need
3. **Enable sandbox mode**: Always use systemd or bwrap sandbox
4. **Monitor audit logs**: Regularly review `ollama-toolchat-audit.db`
5. **Limit network access**: Keep `ALLOW_NETWORK=false` unless needed
6. **Review confirmations**: Always review the dry-run output before confirming

## Disabling Tier 2 Tools

To disable Tier 2 tools entirely:

1. Set `SANDBOX_MODE=none` in `.env`
2. Restart the application

This will prevent any sudo commands from being registered, even if sudoers is configured.
