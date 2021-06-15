# djangorestframework-snatch

## 1. Введение

Основные фичи библиотеки:

- Предоставление CRUD для таблиц из БД. Каждая таблица имеет следующие эндпойнты:
    - _table_schema/table_name/list_
        - GET - получение списка объектов
    - table_schema/table_name/size
        - GET - получение количества объектов в списке
    - _table_schema/table_name/_
        - GET - получение объекта
        - POST - создание объекта
        - PUT - изменение объекта
        - DELETE - удаление объекта
    - _table_schema/table_name/info/_
        - GET - получение информации о таблице
    - _table_schema/table_name/info/table_attribute_
        - GET - редирект на список элементов из родительской таблицы (если поле является ссылкой)
- Сериализация вложенных объектов (отношений) через **self** и **link** (пункт 1.1).
- Десериализация вложенных объектов с **self** и **link** как существующих объектов моделей при
  создании/изменении/удалении объекта (пункт 1.2).
- Использование следующих параметров запроса (пункт 1.3):
    - _query_ - параметры фильтрации
    - _max_level_ - максимальный уровень вложенности
    - _level_ - максимальный уровень вложенности по атрибуту (более точная настройка относительно max_level)
    - _order_ - сортировка
    - _limit_ - количество записей
    - _offset_ - сдвиг от начала
    - _distinct_ - признак получения уникальных записей
- Предоставление метаданных о таблице с возможностью редиректа (пункт 1.4).

### 1.1. Сериализация объектов

При сериализации объектов модели каждая точка вложенности оборачивается в **self** и **link** кроме первого уровня.
Точкой вложенности считается любое отношение данного объекта с любым другим. Уровнем вложенности (**max_level**)
пользователь API ограничивает количество точек вложенности, которое требуется запросить. По-умолчанию уровень
вложенности = 1.

Поле **self** соответствует данным одного объекта/списка элементов родительского/дочернего отношения. Данное поле может
быть равен _null_, если сериализуемое поле не имеет отношения, либо если исчерпан лимит уровня вложенности. Во втором
случае получение данных можно произвести запросом на url из соответствующего **link**. Поле **link** соответствует
url (_null_, если сериализуемое поле не имеет отношения) для получения данных из **self**.

**Пример:**

_/api/public/example/?max_level=2&query=id.eq.1_

```json
{
  "id": 1,
  "name": "Parent 1",
  "parent": {
    "link": "/api/public/example/?query=id.eq.0",
    "self": {
      "id": 0,
      "name": "Parent 0",
      "parent": {
        "link": null,
        "self": null
      },
      "children": {
        "link": "/api/public/example/list?query=parent.eq.0",
        "self": null
      }
    }
  },
  "children": {
    "link": "/api/public/example/list?query=parent.eq.1",
    "self": [
      {
        "id": 2,
        "name": "Child 1",
        "parent": {
          "link": "/api/public/example/?query=id.eq.1",
          "self": null
        },
        "children": {
          "link": null,
          "self": null
        }
      },
      {
        "id": 3,
        "name": "Child 2",
        "parent": {
          "link": "/api/public/example/?query=id.eq.1",
          "self": null
        },
        "children": {
          "link": null,
          "self": null
        }
      }
    ]
  }
}
```

_/api/public/example/?query=id.eq.1_

```json
{
  "id": 1,
  "name": "Parent 1",
  "parent": {
    "link": "/api/public/example/query=id.eq.0",
    "self": null
  },
  "children": {
    "link": "/api/public/example/list?query=parent.eq.1",
    "self": null
  }
}
```

### 1.2. Десериализация объектов

Нотация данных для создания и обновления объектов аналогична сериализованным данным: вложенные отношения должны быть
обернуты в **self** и **link**. Правила для родительских объектов:

- Родительская запись на момент создания/изменения дочерней записи должна существовать в БД.
- Поле **link** может быть пустым.
- Поле **self** не может быть пустым, если требуется добавить ссылку на родительский объект. При этом достаточно указать
  только первичный ключ родительской записи.

Список дочерних объектов не учитывается при создании/изменении родительской. То есть для добавления дочерней записи в
родительскую необходимо создать/получить родительскую запись, создать/изменить дочернюю запись с указанием ссылки на
родительскую. Для удаления дочерней записи из родительской: изменить дочернюю запись, удалив ссылку на родительскую.

Поиск и удаление объекта производится за счет параметров запроса.

### 1.3. Параметры запроса

За основу обработки параметров запросов был взять PostgREST.

#### 1.3.1. Признак получения уникальных записей

Ключ _distinct_ используется как признак получения уникальных записей. Применим для эндпойнтов /list и /size. Дает
возможность получить записи (количества записей) без повторений.

**Пример:**

_/api/public/example/list?distinct&query=children.parent.eq.1_

```json
[
  {
    "id": 1,
    "name": "Parent 1",
    "parent": {
      "link": null,
      "self": null
    },
    "children": {
      "link": "/api/public/example/list?query=parent.eq.1",
      "self": null
    }
  }
]
```

#### 1.3.2. Пагинация

Ключ _limit_ и _offset_ используются для получения среза данных. Применим для эндпойнтов /list и /size. По-умолчанию
limit = PAGE_SIZE из настроек django, а offset = 0.

**Пример:**

_/api/public/example2/list?limit=3&offset=1_

```json
[
  {
    "id": 2,
    "name": "Data 2"
  },
  {
    "id": 3,
    "name": "Data 3"
  },
  {
    "id": 4,
    "name": "Data 4"
  }
]
```

#### 1.3.3. Уровень вложенности

Ключ _max_level_ используется для стандартного ограничения уровня вложенности для данных. Применим для эндпойнтов /list
и /. По-умолчанию max_level = 1. Пример можно посмотреть в пункте 1.1.

Ключ _level_ используется для более точной настройки уровня вложенности. Применим для эндпойнтов /list и /.
**(!!! В данной версии фича пока не реализована !!!)**

**Пример:**

_/api/public/example/?level=parent.2&query=id.eq.1_

```json
{
  "id": 1,
  "name": "Parent 1",
  "parent": {
    "link": "/api/public/example/?query=id.eq.0",
    "self": {
      "id": 0,
      "name": "Parent 0",
      "parent": {
        "link": null,
        "self": null
      },
      "children": {
        "link": "/api/public/example/list?query=parent.eq.0",
        "self": [
          {
            "link": "/api/public/example/?query=id.eq.1",
            "self": {
              "id": 1,
              "name": "Parent 1",
              "parent": {
                "link": "/api/public/example/?query=id.eq.0",
                "self": null
              },
              "children": {
                "link": "/api/public/example/list?query=parent.eq.1",
                "self": null
              }
            }
          }
        ]
      }
    }
  },
  "children": {
    "link": "/api/public/example/list?query=parent.eq.1",
    "self": null
  }
}
```

#### 1.3.4. Сортировка

Ключ _order_ используется для сортировки данных по одному или нескольким полям. Применим для эндпойнта /list. Для
указания направления сортировки используются операторы asc и desc, которые необходимо отделять от последнего атрибута
точкой. Сортировать данные можно и по родительским полям.

**Примеры:**

_/api/public/example2/list?order=name.asc_

```json
[
  {
    "id": 1,
    "name": "Data 1"
  },
  {
    "id": 2,
    "name": "Data 2"
  }
]
```

_/api/public/example2/list?order=name.desc_

```json
[
  {
    "id": 2,
    "name": "Data 2"
  },
  {
    "id": 1,
    "name": "Data 1"
  }
]
```

_/api/public/example4/list?order=(parent.name.asc,name.desc)_

```json
[
  {
    "id": 1,
    "parent": {
      "link": "/api/public/example2/?query=id.eq.2",
      "self": null
    },
    "name": "Y"
  },
  {
    "id": 17,
    "parent": {
      "link": "/api/public/example2/?query=id.eq.2",
      "self": null
    },
    "name": "X"
  },
  {
    "id": 10,
    "parent": {
      "link": "/api/public/example2/?query=id.eq.4",
      "self": null
    },
    "name": "Z"
  }
]
```

#### 1.3.5. Фильтрация

Ключ _query_ используется для фильтрации данных. Применим для эндпойнтов /list, /size и /. При этом для эндпойнтва /
фильтр должен давать единственную запись из БД, иначе произойдет ошибка получения данных из БД. Для построения значения
параметра _query_ используются наименования полей модели, включая все вложенные поля. То есть запрос можно построить по
любым вложенным отношениям относительно данной модели.

**Пример:**

_/api/public/example4/list?query=parent.name.like.Data*_

```json
[
  {
    "id": 1,
    "parent": {
      "link": "/api/public/example2/?query=id.eq.2",
      "self": null
    },
    "name": "Y"
  },
  {
    "id": 10,
    "parent": {
      "link": "/api/public/example2/?query=id.eq.4",
      "self": null
    },
    "name": "Z"
  },
  {
    "id": 17,
    "parent": {
      "link": "/api/public/example2/?query=id.eq.2",
      "self": null
    },
    "name": "X"
  }
]
```

Для построения запросов используются операторы из модуля snatch.search.operators.consts. В таблице 1 перечислены 
основные операторы.

Таблица 1. Операторы для фильтрации

| Оператор | Пример значения в параметрах запроса | Пример преобразования в запрос Django |
| :-------: | :-------------: | :------: |
| eq | id.eq.1 | Q(id__exact=1) |
| eq | id.eq.null | Q(id__isnull=True) |
| neq | id.neq.1 | ~Q(id__exact=1) |
| neq | id.neq.null | ~Q(id__isnull=True) |
| gt | number.gt.100 | Q(number__gt=100) |
| gte | number.gte.100 | Q(number__gte=100) |
| lt | number.lt.100 | Q(number__lt=100) |
| lte | number.lte.100 | Q(number__lte=100) |
| like | name.like.A | Q(name__exact="A") |
| like | name.like.*A* | Q(name__contains="A") |
| like | name.like.A* | Q(name__startswith="A") |
| like | name.like.*A | Q(name__endswith="A") |
| is | name.is.false | Q(name__is=False) |
| is | name.is.true | Q(name__is=True) |
| is | name.is.null | Q(name__isnull=True) |
| year | bday.year.1993 | Q(bday__year="1993") |
| month | bday.month.06 | Q(bday__month="06") |
| day | bday.day.23 | Q(bday__day="23") |
| ov | locations.ov.(US,Korea,Germany) | Q(locations__overlap=\["US", "Korea", "Germany"\]) |
| between | date_start.between.(01-12-1999, 31-12-1999) | Q(date_start__between=\["01-12-1999", "31-12-1999"\]) |
| in | locations.in.(US,Korea,Germany) | Q(locations__in=\["US", "Korea", "Germany"\]) |
| and | and(id.eq.1,name.like.A*) | Q(id__exact=1, name__startswith="A") |
| or | or(id.neq.1,name.like.A*) | Q(~Q(id__exact=1) &#124; Q(name__startswith="A")) |
| not | not(or(id.neq.1,name.like.A*)) | ~Q(~Q(id__exact=1) &#124; Q(name__startswith="A")) |
| -------- | --------------- | -------- |

### 1.4. Метаданные о таблице

### 1.5. Оптимизация (!!! В данной версии фича пока не реализована !!!)

Значения параметров запроса _max_level_, _level_, _query_, _order_ в части атрибутов используются для построения
оптимальных запросов к БД посредством указания в **select_related** и **prefetch_related** необходимых связанных
объектов.