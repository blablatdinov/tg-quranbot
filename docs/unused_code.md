<!---
SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
SPDX-License-Identifier: MIT
-->
# Поиск неиспользуемого кода

```bash
poetry pip install vulture
poetry run vulture src --exclude '*test*'
```
