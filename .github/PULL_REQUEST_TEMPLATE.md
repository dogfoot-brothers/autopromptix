# Pull Request

## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test addition/improvement

## Related Issues

<!-- Link to the issue(s) this PR addresses -->

Fixes #(issue_number)
Closes #(issue_number)
Related to #(issue_number)

## Changes Made

<!-- Describe the specific changes made in this PR -->

- 
- 
- 

## Testing

<!-- Describe the tests you ran to verify your changes -->

### Test Environment

- Python version:
- Operating System:
- Browser (for frontend changes):

### Tests Performed

- [ ] Unit tests pass (`python -m pytest`)
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Frontend tests pass (`npm test`)

### New Tests Added

<!-- If you added new tests, describe them -->

- 
- 

## Documentation

<!-- Check all that apply -->

- [ ] Code is self-documenting with clear variable/function names
- [ ] Added/updated docstrings for new functions
- [ ] Updated README.md if needed
- [ ] Updated API documentation if needed
- [ ] Added examples for new features

## Code Quality Checklist

<!-- Ensure your code meets our standards -->

- [ ] Code follows PEP 8 style guidelines
- [ ] All files end with a newline character
- [ ] No trailing whitespace
- [ ] Type hints are included for new functions
- [ ] Error handling is implemented where appropriate
- [ ] Code is properly commented where necessary

## Breaking Changes

<!-- If this is a breaking change, describe what breaks and migration path -->

- [ ] This PR introduces breaking changes
- [ ] Migration guide is provided
- [ ] Deprecation warnings are added (if applicable)

## Frontend Changes (if applicable)

<!-- For dashboard/frontend changes -->

- [ ] Components are properly typed with TypeScript
- [ ] UI is responsive and works on mobile
- [ ] Accessibility standards are followed
- [ ] No console errors or warnings
- [ ] Material-UI components are used consistently

## Security Considerations

<!-- Consider security implications -->

- [ ] No sensitive information is exposed
- [ ] Input validation is implemented
- [ ] API endpoints are properly secured
- [ ] Dependencies are up to date and secure

## Performance Impact

<!-- Assess performance implications -->

- [ ] No significant performance regression
- [ ] Database queries are optimized (if applicable)
- [ ] Large datasets are handled efficiently
- [ ] Memory usage is reasonable

## Deployment Considerations

<!-- Consider deployment and operational aspects -->

- [ ] No new environment variables required
- [ ] Database migrations are included (if applicable)
- [ ] Backward compatibility is maintained
- [ ] Configuration changes are documented

## Screenshots (if applicable)

<!-- Add screenshots for UI changes -->

### Before

<!-- Screenshot of current behavior -->

### After

<!-- Screenshot of new behavior -->

## Additional Notes

<!-- Any additional information or context -->

## Reviewer Checklist

<!-- For maintainers reviewing the PR -->

- [ ] Code review completed
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] No merge conflicts
- [ ] CI/CD checks pass
- [ ] Security review completed (if needed)
- [ ] Performance impact assessed
- [ ] Ready for merge

---

## Submission Checklist

Before submitting this PR, please make sure:

- [ ] I have read and followed the [Contributing Guidelines](../CONTRIBUTING.md)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## For Maintainers

<!-- Notes for project maintainers -->

### Merge Strategy

- [ ] Squash and merge (for feature branches)
- [ ] Create a merge commit (for release branches)
- [ ] Rebase and merge (for simple fixes)

### Post-Merge Actions

- [ ] Update changelog
- [ ] Tag version (if release)
- [ ] Update documentation site
- [ ] Notify community (if significant change)