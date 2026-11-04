# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

# Agent instructions

This file tells AI coding agents how to work in this repository. It is linted by
[agnix](https://github.com/agent-sh/agnix); do not remove or rename it without
updating the quality gates.

## Run every check before a change is done

The single command that runs every quality gate is:

```sh
task check
```

CI runs exactly this command, so what passes locally will pass on pull requests.
Safe autofixes are available via:

```sh
task fix
```

Never skip `task check` to get a change through. If a rule does not apply, add
a narrow exception instead of disabling the check.

## Generated files — never edit by hand

There are currently no generated source files in this repository. If one is
added later, list it here and add a `DO NOT EDIT` header at the top of the
file. The CI generated-code gate will regenerate it and fail if the committed
copy differs.

## Lint rules are never disabled to get a change through

Exceptions must be:

- narrow: one path and one rule, not a whole directory;
- reasoned: include a comment explaining why;
- reviewed: security/risk suppressions carry a review date in the form
  `(review YYYY-MM-DD)` so they expire when the justification goes stale.

Adding or widening an exception needs a human decision. Do not turn a failing
check into a warning.

## Toolchain versions live in mise.toml

Tool versions are pinned in `mise.toml`. Developers and CI both read it. When
a tool needs upgrading, bump the version there and run `mise install`; do not
install ad-hoc versions elsewhere.
