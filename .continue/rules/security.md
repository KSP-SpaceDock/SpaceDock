# SpaceDock Security Guidelines

This document provides detailed security guidelines for the SpaceDock project, covering authentication, input validation, secure coding practices, handling sensitive data, and security testing procedures.

## Authentication and Authorization Best Practices

### Authentication

1. **Multi-Factor Authentication (MFA)**: Encourage users to enable MFA for their accounts.

2. **Password Policies**: Enforce strong password policies:
   - Minimum length of 12 characters
   - Require a mix of uppercase, lowercase, numbers, and special characters
   - Prevent common passwords

3. **Session Management**:
   - Implement secure, HttpOnly, and SameSite cookies for sessions
   - Set appropriate session timeouts
   - Invalidate sessions on password changes or suspicious activity

4. **Authentication Methods**:
   - Use OAuth 2.0 for third-party integrations
   - Implement JWT for API authentication where appropriate
   - Use Flask-Login for session management

### Authorization

1. **Role-Based Access Control (RBAC)**: Implement RBAC to manage user permissions.
   - Define roles (e.g., user, moderator, admin)
   - Assign permissions based on roles

2. **Permission Checks**:
   - Perform permission checks on both client and server sides
   - Use decorators for route-level permission checks
   ```python
   from functools import wraps
   from flask import abort
   from flask_login import current_user
   
   def admin_required(f):
       @wraps(f)
       def decorated_function(*args, **kwargs):
           if not current_user.is_admin:
               abort(403)
           return f(*args, **kwargs)
       return decorated_function
   ```

3. **Principle of Least Privilege**: Grant users the minimum permissions necessary to perform their tasks.

## Input Validation and Sanitization

### Input Validation

1. **Server-Side Validation**: Always validate input on the server side, even if client-side validation is present.

2. **Validation Rules**:
   - Validate data types (e.g., integers, strings, dates)
   - Check for required fields
   - Validate data formats (e.g., email addresses, URLs)
   - Enforce length constraints

3. **Use Validation Libraries**: Utilize libraries like WTForms or Cerberus for validation.
   ```python
   from wtforms import Form, StringField, validators
   
   class RegistrationForm(Form):
       username = StringField('Username', [
           validators.Length(min=4, max=25),
           validators.Regexp('^[a-zA-Z0-9_]+$', message="Username can only contain letters, numbers, and underscores")
       ])
   ```

### Input Sanitization

1. **Sanitize All Inputs**: Sanitize user inputs to prevent XSS, SQL injection, and other attacks.

2. **Escape Output**: Escape output when rendering it in templates.
   ```python
   {{ user_input | safe }}  # Only if you are sure the input is safe
   {{ user_input }}        # Automatically escaped by default
   ```

3. **Use ORM for Database Queries**: Use SQLAlchemy to avoid SQL injection.
   ```python
   # Safe: Using SQLAlchemy
   user = User.query.filter_by(username=username).first()
   
   # Unsafe: Raw SQL queries
   cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
   ```

## Secure Coding Practices

### General Practices

1. **Dependency Management**:
   - Regularly update dependencies to patch known vulnerabilities
   - Use `pip-audit` or `safety` to scan for vulnerable dependencies

2. **Error Handling**:
   - Avoid exposing sensitive information in error messages
   - Use generic error messages for users
   - Log detailed errors for debugging

3. **Logging**:
   - Log security-related events (e.g., login attempts, permission changes)
   - Avoid logging sensitive data (e.g., passwords, API keys)
   - Use structured logging for easier analysis

### Specific Practices

1. **Secure Headers**: Implement security headers to protect against common vulnerabilities.
   ```python
   from flask_talisman import Talisman
   
   Talisman(app, 
       force_https=True,
       strict_transport_security=True,
       session_cookie_secure=True
   )
   ```

2. **CSRF Protection**: Use Flask-WTF or similar libraries to protect against CSRF attacks.
   ```python
   from flask_wtf.csrf import CSRFProtect
   
   csrf = CSRFProtect(app)
   ```

3. **Rate Limiting**: Implement rate limiting to prevent brute force attacks.
   ```python
   from flask_limiter import Limiter
   from flask_limiter.util import get_remote_address
   
   limiter = Limiter(
       app,
       key_func=get_remote_address,
       default_limits=["200 per day", "50 per hour"]
   )
   
   @app.route('/login')
   @limiter.limit("5 per minute")
   def login():
       pass
   ```

4. **Secure File Uploads**:
   - Validate file types and extensions
   - Scan files for malware
   - Store files outside the web root
   - Use random filenames to prevent overwrites

## Handling Sensitive Data

### Data Storage

1. **Encryption**:
   - Encrypt sensitive data at rest using PostgreSQL's encryption features
   - Use environment variables for secrets, not hardcoded values

2. **Database Security**:
   - Restrict database access to authorized users only
   - Use strong passwords for database users
   - Regularly rotate database credentials

### Data Transmission

1. **HTTPS**: Enforce HTTPS for all communications.
   - Use HSTS headers to ensure browsers always use HTTPS
   - Obtain SSL certificates from trusted providers (e.g., Let's Encrypt)

2. **API Keys**:
   - Use short-lived tokens where possible
   - Restrict API keys to specific IP addresses or ranges
   - Rotate API keys regularly

### Sensitive Data in Code

1. **Environment Variables**: Store sensitive data in environment variables.
   ```python
   import os
   
   SECRET_KEY = os.environ.get('SECRET_KEY')
   DATABASE_URL = os.environ.get('DATABASE_URL')
   ```

2. **Configuration Files**: Never commit configuration files with sensitive data to version control.
   - Add configuration files to `.gitignore`
   - Use `.env.example` to document required environment variables

## Security Testing Procedures

### Automated Testing

1. **Static Application Security Testing (SAST)**:
   - Use tools like Bandit or Semgrep to scan for vulnerabilities in code
   - Integrate SAST into your CI/CD pipeline

2. **Dynamic Application Security Testing (DAST)**:
   - Use tools like OWASP ZAP or Burp Suite for dynamic testing
   - Perform DAST in staging environments

3. **Dependency Scanning**:
   - Use tools like Dependabot or Snyk to monitor dependencies for vulnerabilities
   - Scan dependencies regularly, especially before releases

### Manual Testing

1. **Penetration Testing**:
   - Conduct regular penetration tests
   - Use third-party security firms for comprehensive assessments

2. **Code Reviews**:
   - Perform security-focused code reviews
   - Pay special attention to authentication, authorization, and data handling code

3. **Threat Modeling**:
   - Identify and assess potential threats
   - Document threat models for critical components

### Vulnerability Management

1. **Vulnerability Scanning**:
   - Scan for vulnerabilities regularly
   - Use tools like OpenVAS or Nessus

2. **Patch Management**:
   - Apply security patches promptly
   - Test patches in a staging environment before deploying to production

3. **Incident Response**:
   - Develop an incident response plan
   - Conduct regular incident response drills
   - Document and review security incidents

## Resources

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [Flask Security Documentation](https://flask.palletsprojects.com/en/1.1.x/security/)
- [Python Security Best Practices](https://docs.python-guide.org/writing/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/overview-security.html)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

For questions about security, refer to this document or consult the team.

## Services
Never use external services that arent controled by "52k".

52k is the group that owns spacedock and  the infrastructure its running on.

52k controls the folowing domains:

- 52k.de

- spacedock.info
