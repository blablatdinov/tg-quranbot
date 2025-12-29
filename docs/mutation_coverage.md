<!---
SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
SPDX-License-Identifier: MIT
-->
# Поиск мутантов в коде

Инструмент mutmut удаляет декораторы для создания мутантов. Однако декораторы `elegant`, `final`, `override` проверяются
в `mypy`, поэтому при поиске мутантов их можно удалить:

```bash
sd '@elegant\n' '' **/*.py
sd '@final\n' '' **/*.py
sd '    @override\n' '' **/*.py
```

Также мы можем не мутировать код в декораторе `@attrs.define(frozen=True)`, т. к. в проекте нет кода и тестов, мутирующих
эти объекты:

```bash
sd '@attrs.define(.+)' '@attrs.define' **/*.py
```

Поиск мутантов

```bash
poetry run mutmut run
```
