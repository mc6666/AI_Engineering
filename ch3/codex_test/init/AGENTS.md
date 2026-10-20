# Repository Guidelines

## Project Structure & Module Organization
This repository is currently empty aside from this guide. When you add code, keep the layout simple and predictable:

- `src/` for application code
- `tests/` for automated tests
- `assets/` for static files, fixtures, or sample data
- `docs/` for design notes or longer documentation

Prefer small, focused modules. Use lowercase, descriptive file names such as `user_service.py` or `parser.ts`.

## Build, Test, and Development Commands
No build or test tooling is committed yet. If you add a toolchain, document the exact commands in `README.md` and keep them stable. Common examples:

- `npm test` or `pytest` to run tests
- `npm run build` or `make build` to produce release artifacts
- `npm run dev` to start a local development server

## Coding Style & Naming Conventions
Match the language and formatter you introduce, and keep the project consistent:

- Use 2 or 4 spaces according to the chosen stack, but do not mix styles in one file
- Prefer descriptive names over abbreviations
- Use `snake_case` for Python, `camelCase` for JavaScript/TypeScript variables, and `PascalCase` for classes or components
- Run the repository formatter before committing, if one is added

## Testing Guidelines
Add tests alongside new behavior. Name tests after the unit under test and the behavior being verified, for example:

- `tests/test_parser.py`
- `parser.spec.ts`

Keep tests deterministic and fast. Cover bug fixes with regression tests whenever possible.

## Commit & Pull Request Guidelines
No commit history is available here to infer a project-specific convention. Until one is established, use short imperative commits such as `add parser tests` or `fix input validation`.

Pull requests should include:

- A brief summary of the change
- Any setup or migration notes
- Screenshots or logs when the change affects UI or runtime output
- Links to related issues, if applicable

## Agent-Specific Instructions
Do not overwrite unrelated files. If you add tooling, update this guide so the commands and conventions stay accurate.
