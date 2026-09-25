# CONTENT_DELIVERY.ru.md — ненормативная русская копия межрепозиторного контракта

> **СТАТУС: ТОЛЬКО ДЛЯ ЧТЕНИЯ ЧЕЛОВЕКОМ / NON-NORMATIVE**
>
> Нормативный источник:
> [`/contracts/content-delivery/AGENTS.md`](../contracts/content-delivery/AGENTS.md)
>
> При любом расхождении действует английский нормативный файл.
>
> **source_blob_sha:** `8545316d1db7353b168400714486898ac6f84476`
>
> Если текущий SHA нормативного файла отличается, перевод считается устаревшим.

# Контракт канонической доставки контента и парных репозиториев

## 0. Приоритет

Этот файл — ненормативная русская копия межрепозиторного контракта для пары:

- [bestkvestnn-pixel/dimnadvod](https://github.com/bestkvestnn-pixel/dimnadvod) — канонический content / knowledge repository;
- [bestkvestnn-pixel/test-app](https://github.com/bestkvestnn-pixel/test-app) — interface repository.

Локальные корневые инструкции остаются нормативными внутри своих репозиториев:

- [dimnadvod/AGENTS.md](../AGENTS.md)
- [test-app/AGENTS.md](https://github.com/bestkvestnn-pixel/test-app/blob/main/AGENTS.md)

Этот контракт определяет границу между ними.

Если локальный root противоречит контракту в межрепозиторном вопросе, остановить операцию и считать набор инструкций несогласованным. Не угадывать, какая версия подразумевалась.

---

# 1. Базовая архитектура

Есть **одна авторская база контента**, а не две синхронизируемые сюжетные базы.

`dimnadvod` — единственный канонический store для:
- world facts;
- entities и stable IDs;
- events, scenes, processes и temporal states;
- knowledge и interpretations;
- chapters, transitions, slices и availability rules;
- authored materials и source assets;
- export schemas и projection rules.

`test-app` — интерфейсный репозиторий. В нём могут быть:
- Player App;
- Author Studio;
- application code;
- runtime/session state;
- generated projections и caches;
- tests и fixtures.

Он НЕ должен поддерживать независимую авторскую копию сюжетной базы.

```text
ONE CANONICAL CONTENT STORE
        │
        ├── author reads/writes
        │
        └── versioned projections
                 ↓
          INTERFACE REPOSITORY
```

---

# 2. Направления данных — разные операции

Нельзя моделировать связь как `DB A ⇄ DB B`.

Есть два разных потока.

## 2.1. Доставка контента

```text
dimnadvod
   ↓ derive/export
versioned content package
   ↓
test-app
```

Это односторонняя доставка авторского контента.

## 2.2. Авторская команда

Author-facing UI в `test-app` может инициировать утверждённое каноническое изменение:

```text
Author Studio
   ↓ author command
apply dimnadvod instructions
   ↓
dimnadvod canonical write
```

Это НЕ reverse synchronization.

Команда должна применяться непосредственно к каноническому репозиторию по его root и applicable local `AGENTS.md`.

Нельзя сначала создать авторскую истину во второй app-базе, а затем сливать её обратно как равноправный источник.

---

# 3. Классы владения

Каждый относящийся к системе артефакт должен принадлежать одному классу.

## 3.1. SOURCE

Авторски поддерживаемый канонический контент в `dimnadvod`.

SOURCE — единственная авторская истина.

## 3.2. DERIVED

Generated projections, packages, indexes, JSON, SQLite, search indexes и app-ready data, производные от SOURCE.

DERIVED:
- одноразовые/восстанавливаемые;
- могут быть регенерированы;
- НЕ редактируются как канон;
- по возможности содержат source revision и schema version.

## 3.3. APP CODE

Интерфейсная реализация, которой владеет `test-app`.

Примеры:
- components;
- routes;
- styles;
- rendering;
- storage mechanics;
- client adapters.

APP CODE не канон.

## 3.4. RUNTIME

Состояние конкретной игровой сессии.

Примеры:
- opened/seen materials;
- current UI progress;
- submitted answers;
- session flags;
- preferences;
- local saves.

RUNTIME не авторская истина.

## 3.5. TEST

Fixtures, prototypes, debug data и временные эксперименты.

TEST должен быть физически и семантически отделён от production DERIVED-content.

---

# 4. Владение состоянием: не дублировать самое сложное

Каноническая temporal/knowledge-модель существует только в `dimnadvod`.

Нельзя независимо авторить в `test-app`:
- состояние персонажа Г1;
- состояние персонажа Г2;
- копии world state;
- копии player knowledge;
- копии availability;
- альтернативные timelines из-за позднего раскрытия.

Канонический источник хранит базовые изменения:
- events/scenes;
- temporal state changes;
- knowledge changes;
- availability rules;
- interpretations.

Chapter/player views — производные проекции.

```text
EVENTS / SCENES
      ↓
WORLD STATE
      ↓
KNOWLEDGE + AVAILABILITY
      ↓
SLICE / QUERY COORDINATE
      ↓
PLAYER PROJECTION
      ↓
test-app
      ↓
SESSION RUNTIME
```

Приложение может кэшировать результат, но cache остаётся DERIVED.

RUNTIME может хранить факт открытия материала игроком, но не определяет, существует ли материал канонически и при каких условиях он становится доступным.

---

# 5. Stable IDs проходят границу без изменения

Канонические entity IDs из `dimnadvod` должны оставаться неизменными в derived packages и application consumers.

Не создавать convenience aliases как новую identity.

Например:

```text
char-sergey-akunin
```

не должен тихо превращаться в:

```text
sergey
```

если речь идёт о том же человеке.

Если существует отдельная independently identifiable сущность, дать ей собственный ID и явную связь.

Пример:

```yaml
id: social-sergey-akunin
owner_ref: char-sergey-akunin
```

Source paths, display names, handles и UI labels не являются identity anchors.

---

# 6. Версионированная зависимость контента

`test-app` должен уметь определить точную каноническую ревизию, которую он потребляет.

Целевая machine-readable модель lock/manifest:

```json
{
  "source_repository": "bestkvestnn-pixel/dimnadvod",
  "source_revision": "<commit SHA>",
  "schema_version": 1,
  "package_hash": "<hash>"
}
```

Конкретное имя файла и реализация могут изменяться, но инвариант обязателен:

> Проверенная/собранная версия интерфейса должна воспроизводимо привязываться к точной канонической ревизии.

Generated cache не является dependency declaration; для этого нужен lock/manifest.

---

# 7. Инкрементальная доставка по умолчанию

Доставка контента начинается с известного baseline и вычисления delta.

```text
KNOWN CONTENT REVISION
        ↓
COMPARE WITH CURRENT CANON REVISION
        ↓
LIST CHANGED SOURCE PATHS
        ↓
READ CHANGED INSTRUCTIONS/SCHEMAS FIRST
        ↓
READ CHANGED SOURCE CONTENT
        ↓
EXPAND ONLY REQUIRED DEPENDENCIES
        ↓
RECOMPUTE ONLY AFFECTED PROJECTIONS
        ↓
VALIDATE
        ↓
PUBLISH
        ↓
UPDATE CONTENT LOCK/MANIFEST LAST
```

Не перечитывать и не пересобирать всё при обычном локальном изменении.

Full scan/rebuild оправдан только если:
- нет надёжного baseline;
- dependency/index state потерян или повреждён;
- глобально изменилась schema/projection rule;
- область влияния нельзя безопасно ограничить;
- пользователь явно просит full audit/rebuild.

---

# 8. Сначала инструкции

Если delta меняет:
- root `AGENTS.md`;
- local `AGENTS.md`;
- template;
- schema;
- role dictionary;
- index rule;
- export/projection rule;
- validator,

сначала прочитать и применить новую инструкцию, потом обрабатывать данные в её области.

Изменение текста правила не означает автоматическую массовую миграцию. Сначала определить реальную область влияния.

---

# 9. Согласование парных инструкций

Парный нормативный набор:

1. [dimnadvod/AGENTS.md](../AGENTS.md)
2. [test-app/AGENTS.md](https://github.com/bestkvestnn-pixel/test-app/blob/main/AGENTS.md)
3. [этот контракт](../contracts/content-delivery/AGENTS.md)

Если изменение касается общей архитектурной границы, в той же операции проверить все три файла.

Общие темы:
- repository roles;
- canonical ownership;
- content delivery direction;
- Author Studio canonical writes;
- stable ID rules между репозиториями;
- state/projection ownership;
- content revision locking;
- generated/runtime boundaries;
- cross-repository update protocol.

Не делать три файла механически одинаковыми.

Вместо этого:
- общий закон обновлять в контракте;
- каждый root менять только там, где изменились его локальные обязанности/ссылки;
- несвязанные локальные правила не трогать.

Если обновить все затронутые инструкции невозможно, явно зафиксировать необходимость follow-up до следующей межрепозиторной доставки. Не оставлять противоречие молча.

---

# 10. Авторский материал, созданный внутри приложения

Если фото, документ, текст или иной материал создан при работе в `test-app`, сначала определить его предназначение.

## Только test/runtime

Если это:
- UI fixture;
- visual prototype;
- debug artifact;
- temporary mock;

оставить в TEST/APP scope. В канон не включать.

## Канонический материал

Если автор решил, что это часть игрового мира или набора материалов:

1. считать UI-действие authoring command;
2. прочитать `dimnadvod/AGENTS.md`;
3. прочитать applicable local source instruction, например Materials `AGENTS.md`;
4. разрешить referenced entities через stable IDs/index;
5. создать/обновить canonical material и source asset в `dimnadvod`;
6. валидировать каноническое изменение;
7. построить соответствующую application projection;
8. обновить consumed content revision.

Нельзя сначала утвердить материал как авторскую истину внутри app-owned database.

---

# 11. Граница generated data

DERIVED application content должен находиться в явно обозначенной generated/cache-зоне.

Он может коммититься или не коммититься — это решение реализации, но его полномочия не меняются.

Ручное изменение derived-файла — **generated drift**, а не canonical edit.

Если derived content неверен:
1. определить владельца: SOURCE, projection/export logic или UI rendering;
2. исправить слой-владелец;
3. регенерировать только затронутые outputs.

---

# 12. Защита runtime

Content updates НЕ должны без причины перезаписывать session state.

При совместимости сохранять:
- unlocked materials;
- seen state;
- answers;
- progress;
- preferences;
- saves.

Если новая content/schema version требует migration:
1. определить явную migration;
2. ограничить область;
3. сохранять пользовательские данные, где возможно;
4. тестировать old-save compatibility.

Не сбрасывать весь runtime только из-за изменения канона.

---

# 13. Удаления и переименования

Stable IDs — основной identity anchor.

- Переименование source path при прежнем ID не создаёт новую сущность.
- Удалённая SOURCE-сущность требует обновить только затронутые derived references.
- После доставки не должно оставаться dangling canonical IDs.
- Изменение display label не должно требовать runtime identity migration при прежнем ID.

---

# 14. Бинарные assets

Для images, PDF, audio, video и других крупных assets:

1. сначала сравнивать SHA/hash/version;
2. передавать только новые/изменённые binaries;
3. не копировать неизменившиеся bytes;
4. metadata-only изменение не должно принуждать к повторной передаче binary;
5. source assets принадлежат `dimnadvod`, application delivery copies остаются DERIVED.

---

# 15. Классы конфликтов

## 15.1. Canonical source conflict

В `dimnadvod` произошли конкурирующие канонические изменения.

Решать по canonical ownership и instruction hierarchy. App data не использовать как tie-breaker.

## 15.2. Generated drift

DERIVED artifact был изменён вручную.

Не импортировать автоматически в канон.

## 15.3. Runtime incompatibility

Новый контент несовместим с сохранённым session state.

Решать через runtime migration.

## 15.4. Contract/instruction mismatch

Root-инструкции и контракт расходятся по общей границе.

Остановить cross-repository delivery до согласования.

## 15.5. Schema mismatch

Source projection schema и application consumer schema несовместимы.

Остановить публикацию. Не угадывать семантику полей.

---

# 16. Атомарная публикация

Предпочтительный порядок:

1. определить delta;
2. вычислить affected projections;
3. валидировать generated content;
4. валидировать canonical IDs/references;
5. stage/copy changed assets;
6. опубликовать изменённые outputs;
7. выполнить targeted consumer tests;
8. обновить content lock/manifest **последним**.

Если validation не прошла:
- не продвигать consumed canonical revision;
- не заявлять успешную delivery;
- по возможности сохранять последнюю валидную пару app/content.

---

# 17. Правило минимальной записи

Если recomputation даёт byte/content-identical output:
- не переписывать;
- не создавать noisy commit;
- не обновлять timestamps только потому, что генератор запускался.

То же правило действует для mirrors и indexes.

---

# 18. Критерии завершения

Межрепозиторное обновление контента завершено только если:

1. canonical delta известна;
2. changed instructions прочитаны первыми;
3. affected SOURCE прочитан;
4. required dependencies разрешены;
5. пересчитаны только affected projections;
6. IDs и references валидны;
7. required assets существуют;
8. runtime state сохранён или явно мигрирован;
9. targeted app tests проходят;
10. content lock/manifest указывает точную canonical revision;
11. paired instructions остаются взаимно согласованными.

---

# 19. Краткая формула

> **Одна каноническая база.**

> **Два репозитория с разными обязанностями.**

> **Authoring command может исходить из интерфейса, но canonical write попадает в dimnadvod.**

> **Состояние описывается один раз и проецируется, а не дублируется по главам или репозиториям.**

> **Generated content одноразовый. Runtime остаётся runtime.**

> **Общие изменения инструкций проверяются по обоим root-файлам и этому контракту.**
