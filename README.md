# MoodleParser
Парсер для студентов, написанный для ВолгГТУ (так называемого "ЭИОСа")

## Настройка
Переименовываете `config-example.py` -> `config.py`
Настраиваете:
- **EOS_AUTH_URL** - если вы из ВолгГТУ, то не трогаете
- **EOS_AUTH_LOGIN** - ваш логин
- **EOS_AUTH_PASSWORD** - ваш пароль
- **ONE_OF_COURSE_ID** - ID любого курса на которов вы есть (нужно для парсинга)

остальное меняете если понимаете что делаете.

После запускаете main.py (`$ python3 ./main.py`)
По окончанию он создаст файл `result.json`

Который выглядит примерно так:
```json
{
  "courses": {
    "136": {
      "first": {
        "score": "0",
        "skipped": "2"
      },
      "name": "ФЭВТ 12.03.01 Линейная алгебра и аналитическая геометрия 1сем О_Н Горобцов",
      "second": {
        "score": "–",
        "skipped": "–"
      },
      "total": {
        "score": 0,
        "skip": 0
      }
    },
  // ...
  },
  "timestamp": 1730374444,
  "total": {
    "score": 83,
    "skip": 0
  }
}
```

# Thanks
- ❤️ [@razdvathree ](https://github.com/razdvathree) - разобрался в том как залогинеться в eos2 programmatically
