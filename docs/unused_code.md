# Поиск неиспользуемого кода

```bash
poetry pip install vulture
poetry run vulture src --exclude '*test*'
```
