# Contributing

Thanks for helping improve the project.

## Development workflow

1. Create a focused branch.
2. Make a small, documented change.
3. Add or update tests.
4. Run `pytest` locally.
5. Open a pull request describing behavior, safety impact, and limitations.

## Healthcare-specific expectations

- Use synthetic data only.
- Do not add clinical claims without a reliable source and an explicit review plan.
- Preserve the emergency escalation behavior.
- Avoid collecting or logging identifiers.
- Treat model output as untrusted text and validate integration boundaries.