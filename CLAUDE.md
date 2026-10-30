### Git Commit Conventions

Follow **Conventional Commits** using the format `type(scope): description`.
Use `feat` for new analyses or functionality, `fix` for bug fixes, `data` for dataset changes, `docs` for documentation and reports, `refactor` for code restructuring, and `chore` for project configuration and maintenance.
Write commit messages in English, using concise, imperative descriptions (e.g., `feat(analysis): add 4ft-miner analysis`). Each commit should represent one logical change.
When preprocessing changes affect the dataset, commit the updated script and regenerated data together to maintain reproducibility.
Do not commit temporary files, caches, or generated artifacts unless they are required for reproducibility or submission.
Do not create commits automatically unless explicitly requested.
