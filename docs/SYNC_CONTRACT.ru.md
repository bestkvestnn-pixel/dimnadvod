# SYNC_CONTRACT.ru.md — совместимый указатель

> **СТАТУС: НЕНОРМАТИВНЫЙ / NON-NORMATIVE**
>
> Этот файл оставлен только для совместимости со старыми ссылками.

Актуальная русская справочная копия межрепозиторного контракта:

[CONTENT_DELIVERY.ru.md](CONTENT_DELIVERY.ru.md)

Нормативный английский источник:

[../contracts/content-delivery/AGENTS.md](../contracts/content-delivery/AGENTS.md)

Старый термин «синхронизация двух баз» больше не отражает архитектуру проекта.

Актуальная модель:

```text
dimnadvod
  ONE CANONICAL CONTENT DATABASE
      ↓ versioned projections
test-app
  INTERFACES + RUNTIME
```

Author Studio может инициировать каноническую запись, но такая запись выполняется непосредственно в `dimnadvod`; это не reverse sync.
