# SpaceDock Contribution Guidelines

This document provides comprehensive guidelines for contributing to the SpaceDock project, including how to submit pull requests, the code review process, commit message conventions, documentation standards, and issue tracking and triage.

## How to Contribute

### Getting Started

1. **Fork the Repository**: Create your own fork of the SpaceDock repository on GitHub.

2. **Clone the Repository**: Clone your fork to your local machine.
   ```bash
   git clone https://github.com/your-username/SpaceDock.git
   cd SpaceDock
   ```

3. **Set Upstream Remote**: Add the original repository as an upstream remote.
   ```bash
   git remote add upstream https://github.com/KSP-SpaceDock/SpaceDock.git
   ```

4. **Install Dependencies**: Follow the installation instructions in the [main CONTINUE.md](/.continue/README.md) file.

5. **Create a Branch**: Create a new branch for your changes.
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Making Changes

1. **Follow Coding Standards**: Adhere to the coding standards outlined in the [Coding Standards](/.continue/rules/coding-standards.md) document.

2. **Write Tests**: Ensure your changes are covered by tests. Refer to the [Testing Guidelines](/.continue/rules/testing.md) for more information.

3. **Update Documentation**: Update any relevant documentation to reflect your changes.

4. **Commit Your Changes**: Use meaningful commit messages following the conventions outlined below.
   ```bash
   git commit -m "feat: add new feature"
   ```

### Submitting Pull Requests

1. **Push Your Changes**: Push your branch to your fork on GitHub.
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**: Go to the original repository on GitHub and create a new pull request from your branch.

3. **Fill Out the Pull Request Template**: Provide a clear and concise description of your changes, including:
   - A summary of the changes
   - The motivation behind the changes
   - Any related issues or pull requests
   - Screenshots or examples, if applicable

4. **Request a Review**: Assign reviewers to your pull request. If you're unsure who to assign, leave it unassigned, and the maintainers will review it.

5. **Address Feedback**: Respond to any feedback from reviewers and make the necessary changes.

6. **Merge**: Once your pull request is approved, it will be merged by a maintainer.

## Code Review Process

### Reviewing Pull Requests

1. **Check the Description**: Ensure the pull request description is clear and concise.

2. **Review the Changes**: Carefully review the changes to ensure they:
   - Follow the coding standards
   - Are well-tested
   - Do not introduce any regressions
   - Are consistent with the existing codebase

3. **Test the Changes**: If possible, test the changes locally to ensure they work as expected.

4. **Provide Feedback**: Provide constructive feedback, highlighting any issues or suggestions for improvement.

5. **Approve or Request Changes**: Approve the pull request if it meets all the criteria, or request changes if further work is needed.

### Review Checklist

- [ ] Code follows the coding standards
- [ ] Changes are well-tested
- [ ] No regressions are introduced
- [ ] Documentation is updated
- [ ] Commit messages are clear and concise
- [ ] Changes are consistent with the existing codebase

## Commit Message Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages. This ensures that our commit history is clear and consistent.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (e.g., formatting, missing semicolons)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries

### Scopes

The scope should be the name of the component or file affected by the change (e.g., `mods`, `api`, `frontend`).

### Subject

The subject should be a short description of the change, written in the imperative mood (e.g., "Add new feature" instead of "Added new feature").

### Body

The body should provide more detailed information about the change, including:
- The motivation behind the change
- The approach taken
- Any related issues or pull requests

### Footer

The footer should include any references to issues or pull requests (e.g., `Fixes #123`, `Closes #456`).

### Examples

```
feat(mods): add download statistics

Add download statistics to the mod details page.

This change adds a new section to the mod details page that displays
the number of downloads for each version of the mod.

Fixes #123
```

```
fix(api): handle null values in search results

Handle null values in search results to prevent errors.

This change ensures that the API handles null values in search results
gracefully, preventing errors when displaying search results.

Closes #456
```

## Documentation Standards

### Documentation Structure

- **Code Comments**: Use clear and concise comments to explain complex logic or non-obvious code.
- **Docstrings**: Use docstrings for functions and classes to provide detailed documentation.
- **README Files**: Include a README file in each directory to explain its purpose and contents.
- **API Documentation**: Update the API documentation to reflect any changes to the API.

### Documentation Style

- **Clear and Concise**: Write documentation that is easy to understand and to the point.
- **Consistent**: Use consistent formatting and style throughout the documentation.
- **Up-to-Date**: Ensure that documentation is always up-to-date with the latest changes.
- **Examples**: Provide examples where applicable to illustrate how to use a feature or API.

### Documentation Tools

- **Sphinx**: Use Sphinx for generating documentation from docstrings.
- **Markdown**: Use Markdown for README files and other documentation.
- **Swagger**: Use Swagger for API documentation.

## Issue Tracking and Triage

### Reporting Issues

1. **Check Existing Issues**: Before reporting a new issue, check if it has already been reported.

2. **Provide Details**: When reporting a new issue, provide as much detail as possible, including:
   - A clear and concise description of the issue
   - Steps to reproduce the issue
   - The expected behavior
   - The actual behavior
   - Any relevant logs or error messages
   - Your environment (e.g., browser, operating system, version of SpaceDock)

3. **Use the Issue Template**: Fill out the issue template provided in the repository.

### Triage Process

1. **Label Issues**: Apply appropriate labels to issues to categorize them (e.g., `bug`, `enhancement`, `documentation`).

2. **Prioritize Issues**: Prioritize issues based on their impact and urgency.

3. **Assign Issues**: Assign issues to team members or volunteers who are interested in working on them.

4. **Close Issues**: Close issues that are no longer relevant or have been resolved.

### Issue Labels

- **bug**: A bug or unexpected behavior
- **enhancement**: A new feature or improvement
- **documentation**: A change or addition to the documentation
- **good first issue**: A good issue for new contributors
- **help wanted**: The team is looking for help with this issue
- **wontfix**: This issue will not be addressed

### Issue Templates

Use the provided issue templates to ensure that issues are reported with all the necessary information:

- **Bug Report**: For reporting bugs or unexpected behavior
- **Feature Request**: For requesting new features or improvements
- **Documentation Issue**: For reporting issues with the documentation

## Best Practices

### Code Quality

- **Follow Coding Standards**: Adhere to the coding standards outlined in the [Coding Standards](/.continue/rules/coding-standards.md) document.
- **Write Tests**: Ensure your changes are covered by tests.
- **Review Code**: Participate in code reviews to ensure high code quality.

### Communication

- **Be Respectful**: Treat all contributors with respect and kindness.
- **Be Clear**: Communicate clearly and concisely.
- **Be Helpful**: Offer help and support to other contributors.

