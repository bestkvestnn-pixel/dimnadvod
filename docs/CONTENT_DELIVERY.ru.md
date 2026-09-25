# CONTENT_DELIVERY.ru.md — ненормативная русская копия межрепозиторного контракта

> **СТАТУС: ТОЛЬКО ДЛЯ ЧТЕНИЯ ЧЕЛОВЕКОМ / NON-NORMATIVE**
>
> Нормативный источник:
> [`/contracts/content-delivery/AGENTS.md`](../contracts/content-delivery/AGENTS.md)
>
> При расхождении всегда действует английский нормативный файл.
>
> **source_blob_sha:** `8545316d1db7353b168400714486898ac6f84476`
>
> Если SHA нормативного файла отличается, этот перевод считается устаревшим.

# Контракт доставки контента и парных репозиториев

## 1. Главная модель

Есть **одна авторская база**, а не две синхронизируемые сюжетные базы.

- `dimnadvod` — единственный канонический источник контента.
- `test-app` — интерфейсный репозиторий.

`test-app` может содержать:
- Player App;
- Author Studio;
- код;
- runtime;
- generated/cache проекции;
- тесты.

Но не независимый канон.

## 2. Два разных потока

### Доставка контента

```text
dimnadvod
   ↓ derive/export
versioned content package
   ↓
test-app
```

### Авторская команда

```text
Author Studio
   ↓ авторская команда
правила dimnadvod
   ↓
каноническая запись в dimnadvod
```

Второй поток — не reverse sync.

## 3. Классы владения

- **SOURCE** — авторские данные в `dimnadvod`.
- **DERIVED** — JSON, SQLite, indexes, packages, cache и другие производные представления.
- **APP CODE** — код интерфейсов.
- **RUNTIME** — состояние конкретной партии.
- **TEST** — fixtures, mocks и прототипы.

Только SOURCE является авторской истиной.

## 4. Состояния не дублируются

Каноническая модель состояний существует только в `dimnadvod`.

Не вести в приложении отдельные:
- статусы Г1/Г2;
- копии world state;
- копии player knowledge;
- копии availability;
- альтернативные прошлые состояния из-за позднего раскрытия.

Предпочтительная цепочка:

```text
СОБЫТИЯ / СЦЕНЫ
      ↓
СОСТОЯНИЕ МИРА
      ↓
ЗНАНИЕ + ДОСТУПНОСТЬ
      ↓
СРЕЗ / КООРДИНАТА ЗАПРОСА
      ↓
PLAYER PROJECTION
      ↓
test-app
      ↓
SESSION RUNTIME
```

## 5. Stable ID не меняется между репозиториями

Если сущность имеет ID:

`char-sergey-akunin`

то этот же ID используется в производных данных и интерфейсах.

Не заменять его удобным новым идентификатором типа `sergey`, если речь идёт о той же сущности.

Отдельный аккаунт, автомобиль или материал — отдельная сущность со своим ID и явной связью.

## 6. Версионированная зависимость

`test-app` должен уметь однозначно определить, какую ревизию `dimnadvod` он использует.

Целевая модель:

```json
{
  "source_repository": "bestkvestnn-pixel/dimnadvod",
  "source_revision": "<commit SHA>",
  "schema_version": 1,
  "package_hash": "<hash>"
}
```

Generated cache не заменяет content lock/manifest.

## 7. Инкрементальное обновление

```text
KNOWN CONTENT REVISION
        ↓
COMPARE
        ↓
CHANGED SOURCE PATHS ONLY
        ↓
CHANGED INSTRUCTIONS FIRST
        ↓
CHANGED SOURCE
        ↓
REQUIRED DEPENDENCIES ONLY
        ↓
AFFECTED PROJECTIONS ONLY
        ↓
VALIDATE
        ↓
PUBLISH
        ↓
CONTENT LOCK LAST
```

Полный rebuild — исключение.

## 8. Сначала инструкции

Если изменились:
- root/local `AGENTS.md`;
- template;
- schema;
- role dictionary;
- index rule;
- export/projection rule;
- validator,

сначала применяется новое правило, потом данные в его области.

## 9. Согласование парных инструкций

Парный набор:

1. [dimnadvod/AGENTS.md](../AGENTS.md)
2. [test-app/AGENTS.md](https://github.com/bestkvestnn-pixel/test-app/blob/main/AGENTS.md)
3. [content-delivery contract](../contracts/content-delivery/AGENTS.md)

Если меняется общая архитектурная граница, в той же операции проверить все три.

Общие темы:
- роли репозиториев;
- владение каноном;
- состояние/projection;
- stable IDs;
- Author Studio;
- content delivery;
- content lock;
- generated/runtime;
- правила обновления инструкций.

Корневые файлы не должны быть одинаковыми: общий закон — в контракте, локальные обязанности — в корнях.

## 10. Материал создан внутри приложения

Если в `test-app` создано фото, документ или текст:

- если это fixture/mock/debug → TEST;
- если автор решил, что это канонический материал → Author Studio инициирует запись непосредственно в `dimnadvod`.

После канонической записи создаётся производная копия для интерфейса.

## 11. Generated drift

Ручное изменение производного файла не становится каноном.

Исправлять нужно владельца:
- SOURCE;
- projection/export;
- UI.

## 12. Защита runtime

Обновление контента не должно без причины стирать:
- opened/seen;
- answers;
- progress;
- preferences;
- saves.

При несовместимости нужна явная миграция.

## 13. Renames/deletes

Stable ID — якорь identity.

Переименование пути или display name при прежнем ID не создаёт новую сущность.

Удаление SOURCE должно убрать только затронутые производные ссылки.

## 14. Бинарные файлы

Для изображений, PDF, audio/video:
- сначала сравнивать SHA/hash;
- переносить только изменённые;
- metadata-only правка не должна копировать бинарник заново.

## 15. Конфликты

- **Canonical source conflict** — решается в `dimnadvod`.
- **Generated drift** — регенерируется.
- **Runtime incompatibility** — миграция runtime.
- **Instruction mismatch** — остановить межрепозиторное обновление.
- **Schema mismatch** — остановить публикацию до явного решения.

## 16. Атомарная публикация

1. определить delta;
2. построить затронутые projections;
3. проверить;
4. проверить IDs/links;
5. перенести assets;
6. опубликовать;
7. выполнить targeted tests;
8. обновить content lock последним.

## 17. Минимальная запись

Если производный файл после пересчёта идентичен — не переписывать его.

## 18. Критерий завершения

Обновление завершено только если:
- delta известна;
- инструкции прочитаны первыми;
- SOURCE и зависимости обработаны;
- пересчитаны только затронутые projections;
- IDs/links валидны;
- assets присутствуют;
- runtime сохранён или мигрирован;
- targeted tests прошли;
- lock указывает точную source revision;
- три нормативные инструкции согласованы.

> **Одна каноническая база. Два репозитория. Состояние описывается один раз и проецируется.**
