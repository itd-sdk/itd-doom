# itd-doom

DOOM в рисовалке ИТД.

## Запуск

### Майнкрафт:
```bash
uv sync
export TOKEN="Ваш refresh token (см. https://itdsdk.qzz.io/docs/launch/)"
uv run main.py minecraft
```

### DOOM:
```bash
uv sync
export TOKEN="Ваш refresh token (см. https://itdsdk.qzz.io/docs/launch/)"
uv run main.py doom
```
Качетсво изображения можно настравить через параметр `-q` (0.1 - самое низкое, 1.0 - самое высокое):
```bash
uv run main.py minecraft -q 0.8
```


## Прочее
 - `manual.py`: Вариант где пиксели вручную вводятся мышкой (там просто рисуется картинка).
