# ADR — Mental Math + Laya

> Current implementation direction: [approved web platform design](superpowers/specs/2026-09-24-mental-math-web-platform-design.md). This document remains the architectural baseline. The approved design clarifies GPU Framework ownership of Laya deployment and adds account, profile, resume and connected-PWA requirements.

## ADR-001. Laya не решает арифметику

**Статус:** Accepted

**Решение:** разделить систему на:
- `Math Engine` — генерация задач и точная проверка ответов;
- `Student Model` — модель состояния и прогресса ребёнка;
- `Adaptive Policy` на Laya — выбор следующего педагогического действия;
- `Game Engine` — игровой цикл и применение решения.

Laya используется не для вычисления `7 + 8`, а для выбора:
- повторить навык;
- снизить/повысить сложность;
- дать подсказку;
- сменить тип упражнения.

Причина: арифметика детерминирована, а выбор следующего упражнения — вероятностная задача на основе состояния ученика.

---

## ADR-002. Локальный inference

**Статус:** Accepted

Laya разворачивается локально рядом с backend приложения.

```text
Game Backend -> Laya HTTP API
```

История ребёнка и профиль навыков не отправляются во внешние AI API.

Базовый вариант запуска:

```bash
pip install "laya[serve]"

LAYA_DEVICE=cpu \
LAYA_PRELOAD=1 \
laya-serve
```

---

## ADR-003. Гибрид Rules + Laya

**Статус:** Accepted

Laya не имеет абсолютного контроля над игровым процессом.

Жёсткие ограничения задаются обычным кодом:
- возрастные ограничения;
- допустимые арифметические операции;
- пределы значений;
- запрет повышения сложности после серии ошибок;
- лимиты длительности сессии.

Поток:

```text
Rules -> допустимые действия -> Laya -> выбранное действие
```

При недоступности Laya используется `fallback policy`.

---

## ADR-004. Fine-tuning после MVP

**Статус:** Accepted

Первый MVP работает на правилах и базовой Laya.

На первом этапе Laya рекомендуется включить в `shadow mode`:

```text
Rule Engine: REPEAT
Laya:        HARDER
Applied:     REPEAT
```

Все решения логируются.

После накопления данных формируется датасет:

```text
state
+
decision
+
outcome
```

Далее:
- fine-tuning;
- калибровка вероятностей;
- offline evaluation;
- A/B сравнение с rule-based policy.

---

## ADR-005. Student Model отделён от Policy

**Статус:** Accepted

Оценка уровня владения навыком не делегируется Laya.

`Student Model` отвечает на вопрос:

> Что ребёнок уже умеет?

`Laya Policy` отвечает на вопрос:

> Что лучше сделать дальше?

Для оценки mastery можно использовать:
- простую взвешенную формулу;
- Bayesian Knowledge Tracing;
- Elo-подобную модель.

---

## ADR-006. Решения Laya ограничены малым action space

**Статус:** Accepted

Предпочтительное пространство действий:

```text
repeat
easier
harder
switch
hint
no_hint
```

Перед inference из списка исключаются запрещённые действия.

Это уменьшает риск некорректного поведения и упрощает валидацию.

---

## ADR-007. Backend на Python + FastAPI

**Статус:** Accepted

Причины:
- Laya работает в Python-экосистеме;
- минимальная интеграционная сложность;
- простой HTTP API;
- удобное тестирование;
- быстрая реализация MVP.

---

## ADR-008. Логировать все policy decisions

**Статус:** Accepted

Для каждого решения сохраняются:
- входной state;
- версия модели;
- ответ Laya;
- итоговое применённое действие;
- результат следующих упражнений.

Таблица `policy_decision` обязательна для дальнейшего обучения и анализа.
