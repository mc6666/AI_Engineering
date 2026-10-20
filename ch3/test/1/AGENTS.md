# Repository Guidelines

## Project Structure & Module Organization

This directory currently contains no tracked source tree, tests, assets, or Git metadata. When adding project files, keep production code under a clearly named source directory (for example, `src/`), tests under `tests/` or alongside modules using the established project convention, and reusable static files under `assets/`. Update this section when the project structure is established.

## Build, Test, and Development Commands

No build or test tooling is configured yet. Document the canonical commands here as soon as a toolchain is added; for example, `npm install` to install dependencies, `npm test` to run tests, and `npm run build` to produce a release build. Prefer repository-local scripts over undocumented machine-specific commands.

## Coding Style & Naming Conventions

Use the formatter and linter selected by the project, and commit their configuration with the code. Unless a language-specific standard is introduced, use four spaces for indentation, descriptive names, and small focused modules. Name files consistently with the surrounding code; use `PascalCase` for types or components and `camelCase` for variables and functions where those conventions apply.

## Testing Guidelines

Add tests with each behavior change. Use the project's chosen framework and place test files in the established test directory, with names that identify the unit or feature (for example, `test_<feature>.*` or `<feature>.test.*`). Record the exact test and coverage commands here when configured.

## Commit & Pull Request Guidelines

There is no Git history to infer a commit convention from. Use short, imperative commit subjects such as `Add input validation`, and keep unrelated changes separate. Pull requests should explain the purpose, summarize implementation details, list validation performed, and include screenshots or reproduction steps when a user-facing change is added.

## Security & Configuration Tips

Do not commit credentials, private keys, generated secrets, large build outputs, or local environment files. Provide a sanitized example configuration such as `.env.example` when configuration becomes necessary, and document required environment variables without exposing their values.
