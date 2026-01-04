# Contributing to Route 23

Thank you for your interest in contributing to Route 23! This document provides guidelines for contributing to this automated torrent seeding project.

## Table of Contents

- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When reporting a bug, include:

- **Clear title** describing the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Environment details**:
  - OS and version
  - Docker version (`docker --version`)
  - Docker Compose version (`docker compose version`)
  - Hardware (especially for Raspberry Pi issues)
- **Relevant logs**:
  ```bash
  docker logs route23-rotator
  docker logs route23-vpn
  docker logs route23-rutorrent
  ```
- **Configuration** (sanitized `.env` file with secrets removed)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement:

- Use a clear, descriptive title
- Provide detailed description of the proposed functionality
- Explain why this would be useful to Route 23 users
- Include examples or mockups if applicable

### Good First Issues

Look for issues labeled:

- `good first issue` - Simple issues for newcomers
- `help wanted` - Issues where we need community help
- `documentation` - Documentation improvements
- `raspberry-pi` - Optimization for low-power devices

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Git
- Text editor or IDE
- (Optional) Python 3.11+ for local testing of rotation script
- (Optional) Raspberry Pi or similar low-power device for testing

### Local Setup

1. **Fork and clone the repository**:

```bash
git clone https://github.com/YOUR_USERNAME/route23.git
cd route23
```

2. **Create your `.env` file**:

```bash
cp .env.example .env
# Edit .env with your credentials
```

If `.env.example` doesn't exist, see the README for required variables.

3. **Start the development environment**:

```bash
# Start all services
docker compose up -d nginx

# View logs
docker compose logs -f
```

4. **Make your changes** and test them

5. **Clean up**:

```bash
docker compose down
docker compose down -v  # Also remove volumes
```

### Project Structure

```
route23/
├── src/
│   └── main.py                     # Core rotation logic (Python 3.11)
├── docker-compose.yaml             # Service orchestration
├── Dockerfile                      # Rotator service image
├── nginx/
│   └── nginx.conf                  # Reverse proxy configuration
├── rutorrent/
│   ├── data/
│   │   ├── rtorrent/.rtorrent.rc  # rTorrent settings
│   │   └── scripts/notification_agent.py  # Email notifications
│   └── torrents/                   # Test .torrent files
└── exe/
    ├── mvmovie                     # Bash utility scripts
    ├── monitor.sh
    └── backup.sh
```

## Coding Standards

### Python Style (src/main.py)

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines:

- **Line length**: 100 characters
- **Formatting**: Use `black` for automatic formatting
- **Type hints**: Use type annotations for function signatures
- **Docstrings**: Use clear, concise docstrings for functions

```python
# Good
def load_state_file(state_path: str) -> dict:
    """Load rotation state from JSON file.

    Args:
        state_path: Path to state JSON file

    Returns:
        Dictionary containing rotation state
    """
    with open(state_path, 'r') as f:
        return json.load(f)

# Bad
def load(p):
    return json.load(open(p))
```

### Shell Scripts (exe/*)

For Bash scripts:

- Use `#!/bin/bash` shebang
- Quote variables: `"$variable"` not `$variable`
- Check exit codes: `if [ $? -ne 0 ]; then`
- Add comments for complex logic
- Use descriptive variable names

```bash
# Good
backup_dir="/path/to/backup"
if [ ! -d "$backup_dir" ]; then
    echo "Error: Backup directory does not exist"
    exit 1
fi

# Bad
d=/path/to/backup
[ ! -d $d ] && exit 1
```

### Docker Configuration

- Keep images minimal (use Alpine where possible)
- Use multi-stage builds for efficiency
- Pin specific versions in `FROM` statements
- Document all `ENV` variables
- Use `.dockerignore` to exclude unnecessary files

### Configuration Files

- **docker-compose.yaml**: Maintain consistent formatting, document new services
- **nginx.conf**: Add comments for custom configurations
- **.rtorrent.rc**: Document any performance tuning changes

### Code Quality

Before committing, ensure your code:

- Follows the style guidelines above
- Includes appropriate error handling
- Has no hardcoded credentials or paths
- Works on both x86_64 and ARM architectures (Raspberry Pi)

## Pull Request Process

### Before Submitting

1. **Update your fork**:

```bash
git fetch upstream
git rebase upstream/master
```

2. **Test your changes**:

```bash
# Rebuild containers
docker compose build

# Start services
docker compose up -d nginx

# Run rotation to test
docker compose run --rm -e SHOW_STATUS=true app

# Check logs for errors
docker compose logs
```

3. **Check for common issues**:

- Do containers start successfully?
- Does the VPN connect properly?
- Does ruTorrent web UI load?
- Does rotation work as expected?
- Are there any permission errors?

4. **Update documentation** if needed

### PR Description Template

```markdown
## Summary
Brief description of what this PR does

## Motivation
Why is this change needed? What problem does it solve?

## Changes
- List of specific changes made
- Another change
- Third change

## Testing
How was this tested?
- Tested on x86_64 / Raspberry Pi / both
- Verified VPN connection works
- Checked rotation completes successfully
- etc.

## Screenshots
(If applicable, e.g., UI changes)

## Related Issues
Closes #123
```

### Review Process

1. Automated checks must pass (if CI/CD is configured)
2. Code review by maintainer(s)
3. Address feedback and update PR
4. Once approved, PR will be merged

## Testing Guidelines

### Manual Testing Checklist

When making changes, verify:

- [ ] All containers start without errors
- [ ] VPN connection establishes successfully
- [ ] ruTorrent web UI is accessible and functional
- [ ] Authentication works correctly
- [ ] Rotation script completes without errors
- [ ] Email notifications are sent (if configured)
- [ ] State is persisted correctly across restarts
- [ ] No permission issues with volumes
- [ ] Works on target hardware (Raspberry Pi if applicable)

### Testing Rotation Logic

```bash
# Test with small batch and short rotation period
docker compose run --rm \
  -e BATCH_SIZE=2 \
  -e ROTATION_DAYS=0.001 \
  -e FORCE_ROTATION=true \
  app

# Check status
docker compose run --rm -e SHOW_STATUS=true app

# Verify state file
cat data/rotation_state.json
```

### Testing on Raspberry Pi

If making performance-related changes:

- Test on actual Raspberry Pi hardware when possible
- Monitor system load during rotation
- Verify that `MAX_LOAD` throttling works
- Check memory usage with `docker stats`

### Log Inspection

```bash
# View specific service logs
docker logs route23-rotator
docker logs route23-vpn
docker logs route23-rutorrent

# Follow logs in real-time
docker compose logs -f rotator

# Check for errors
docker compose logs | grep -i error
```

## Documentation

### What to Document

Update documentation when you:

- Add new features or services
- Change configuration options
- Modify environment variables
- Add new utility scripts
- Change installation steps
- Update dependencies

### Files to Update

- **README.md** - User-facing documentation, installation, usage
- **CONTRIBUTING.md** - This file (contributor guidelines)
- **Code comments** - Explain complex logic in source files
- **docker-compose.yaml** - Comment new services or configurations

### Commit Messages

Use clear, descriptive commit messages following this format:

```
<type>: <subject>

<optional body>

<optional footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style/formatting changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build, etc.)

**Examples:**

```
feat: add support for qBittorrent as alternative client

fix: resolve VPN connection timeout on Raspberry Pi

docs: update README with Raspberry Pi 5 instructions

perf: reduce memory usage in rotation script
```

## Environment Variables

When adding new environment variables:

1. Document them in the README
2. Add sensible defaults in the code
3. Include them in `.env.example` (if it exists)
4. Note in PR description if they're required vs optional

## Security Considerations

- Never commit credentials, tokens, or private keys
- Sanitize logs before sharing publicly
- Be cautious with volume mounts (avoid mounting host root)
- Document any security implications of changes
- Use secrets management for sensitive data where possible

## Questions or Help

- Open an issue with the `question` label
- Check existing issues and discussions
- Review the README and documentation thoroughly first

## Recognition

Contributors will be recognized in:
- The project README (for significant contributions)
- Release notes
- Git commit history

## License

By contributing to Route 23, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Route 23!
