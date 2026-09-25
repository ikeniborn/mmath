# LLD — Mental Math + Laya

> Current implementation direction: [approved web platform design](superpowers/specs/2026-09-24-mental-math-web-platform-design.md). Its account ownership, idempotent session API, fixed/automatic modes and Docker boundaries refine the conceptual examples below.

## 1. Структура проекта

```text
mental-math/
├── frontend/
├── backend/
│   ├── api/
│   │   ├── sessions.py
│   │   ├── attempts.py
│   │   └── profiles.py
│   ├── game/
│   │   ├── engine.py
│   │   ├── generator.py
│   │   ├── validator.py
│   │   └── constraints.py
│   ├── student/
│   │   ├── state.py
│   │   ├── mastery.py
│   │   └── errors.py
│   ├── policy/
│   │   ├── laya.py
│   │   ├── fallback.py
│   │   └── policy.py
│   └── persistence/
├── laya/
├── migrations/
└── docker-compose.yml
```

---

## 2. Game Engine

Ответственность:
- открыть игровую сессию;
- получить ответ;
- проверить результат;
- обновить состояние;
- вызвать policy;
- сгенерировать следующую задачу.

Псевдокод:

```python
async def process_attempt(session_id, problem_id, answer, response_ms):
    problem = await problem_repo.get(problem_id)

    result = math_validator.validate(problem, answer)

    attempt = await attempt_repo.save(
        session_id=session_id,
        problem_id=problem_id,
        answer=answer,
        correct=result.correct,
        response_ms=response_ms,
    )

    student_state = await student_model.update(attempt)

    action = await adaptive_policy.decide(student_state)

    spec = constraints.apply(
        state=student_state,
        action=action,
    )

    next_problem = problem_generator.generate(spec)

    return result, next_problem
```

---

## 3. Math Engine

### Интерфейс

```python
@dataclass
class ProblemSpec:
    skill: str
    difficulty: int
    hint_type: str | None


class ProblemGenerator:
    def generate(self, spec: ProblemSpec) -> Problem:
        ...
```

### Пример шкалы сложности

```text
addition:

0 -> a,b in 0..5
1 -> result <= 10
2 -> переход через 10
3 -> result <= 20
4 -> result <= 50
```

Проверка ответа выполняется только детерминированным кодом.

---

## 4. Student Model

Пример состояния навыка:

```json
{
  "skill": "addition_10_20",
  "attempts": 31,
  "correct": 22,
  "accuracy": 0.71,
  "last_5_accuracy": 0.60,
  "avg_response_ms": 4300,
  "error_streak": 1,
  "mastery": 0.64
}
```

Простой MVP-вариант mastery:

```text
mastery =
    0.50 * recent_accuracy
  + 0.30 * speed_score
  + 0.20 * consistency
```

Позже заменить на BKT.

---

## 5. Error Classifier

Пример:

```text
8 + 7

15 -> correct
14 -> off_by_one
87 -> concatenation
1  -> subtraction_confusion
```

Интерфейс:

```python
class ErrorClassifier:
    def classify(
        self,
        problem: Problem,
        answer: int
    ) -> str:
        ...
```

---

## 6. Policy State

В Laya передаётся компактный state:

```json
{
  "age_group": "5-6",
  "current_skill": "addition_10_20",
  "current_difficulty": 2,
  "skill_stats": {
    "mastery": 0.61,
    "accuracy_20": 0.70,
    "accuracy_5": 0.40,
    "avg_time_ms": 5200
  },
  "session": {
    "attempt": 14,
    "correct_streak": 0,
    "error_streak": 2,
    "hints_used": 3
  },
  "last_attempt": {
    "correct": false,
    "response_ms": 6100,
    "error_type": "off_by_one"
  }
}
```

---

## 7. Laya Adapter

```python
class LayaPolicyClient:

    async def decide(
        self,
        state: PolicyState,
        allowed_actions: list[str],
    ) -> PolicyDecision:
        ...
```

Концептуальный запрос:

```json
{
  "state": {
    "current_skill": "addition_10_20",
    "mastery": 0.61,
    "accuracy_5": 0.40,
    "error_streak": 2
  },
  "questions": {
    "next_action": {
      "type": "choice",
      "criteria": {
        "repeat": "practice the same skill",
        "easier": "reduce difficulty",
        "switch": "switch to another skill"
      }
    }
  }
}
```

---

## 8. Constraint Engine

Ограничения применяются до и после Laya.

Пример:

```python
def allowed_actions(state):
    actions = {"repeat", "easier", "harder", "switch"}

    if state.error_streak >= 3:
        actions.discard("harder")

    if state.session_minutes >= 10:
        actions.discard("harder")

    return actions
```

Предпочтительно не передавать запрещённые варианты в Laya вообще.

---

## 9. Fallback Policy

```python
def fallback_policy(state):
    if state.error_streak >= 3:
        return "easier"

    if state.correct_streak >= 5:
        return "harder"

    return "repeat"
```

Используется при:
- timeout;
- HTTP error;
- низкой confidence;
- invalid response;
- недоступности модели.

---

## 10. REST API

### Создать сессию

```http
POST /api/v1/sessions
```

```json
{
  "player_id": "123",
  "mode": "adaptive"
}
```

Ответ:

```json
{
  "session_id": "abc",
  "problem": {
    "id": "p42",
    "expression": "8 + 7",
    "type": "addition"
  }
}
```

### Отправить ответ

```http
POST /api/v1/sessions/abc/attempts
```

```json
{
  "problem_id": "p42",
  "answer": 14,
  "response_ms": 3800
}
```

Ответ:

```json
{
  "correct": false,
  "feedback": {
    "type": "visual_hint"
  },
  "next_problem": {
    "id": "p43",
    "expression": "6 + 7"
  }
}
```

---

## 11. Модель данных

```text
player
------
id
name
birth_year
created_at

skill
-----
id
code

player_skill
------------
player_id
skill_id
mastery
attempt_count
accuracy
avg_response_ms
updated_at

session
-------
id
player_id
started_at
finished_at

problem
-------
id
skill_id
difficulty
operand_a
operand_b
operation
correct_answer

attempt
-------
id
session_id
problem_id
answer
correct
response_ms
hint_used
created_at

policy_decision
---------------
id
session_id
attempt_id
model_version
state_json
decision_json
applied_action
created_at
```

---

## 12. Docker Compose

```yaml
services:
  api:
    build: ./backend
    environment:
      LAYA_URL: http://laya:8000
      DATABASE_URL: postgresql://mental:mental@postgres/mental
    depends_on:
      - postgres
      - laya

  laya:
    image: mental-laya
    environment:
      LAYA_DEVICE: cpu
      LAYA_PRELOAD: "1"

  postgres:
    image: postgres:17

  frontend:
    build: ./frontend
```

---

## 13. Наблюдаемость

Минимальные метрики:

```text
policy_latency_ms
policy_error_total
policy_fallback_total
attempt_total
correct_ratio
session_duration
skill_mastery_change
```

Логи должны содержать:
- session_id;
- player_id;
- skill;
- model_version;
- policy decision;
- applied action;
- inference latency.

---

## 14. Данные для обучения

Пример записи:

```json
{
  "state": {
    "skill": "addition_10_20",
    "mastery": 0.58,
    "accuracy_5": 0.40,
    "error_streak": 2
  },
  "decision": "easier",
  "outcome": {
    "next_5_accuracy": 0.80,
    "next_5_avg_time": 3500,
    "session_completed": true
  }
}
```

Целевой reward можно считать как:

```text
reward =
    0.40 * improvement_accuracy
  + 0.25 * improvement_speed
  + 0.20 * session_completion
  + 0.15 * retention
```

---

## 15. Итоговый runtime flow

```mermaid
sequenceDiagram
    participant UI
    participant API
    participant Game
    participant Math
    participant Student
    participant Policy
    participant Laya

    UI->>API: submit answer
    API->>Game: processAttempt()
    Game->>Math: validate()
    Math-->>Game: result
    Game->>Student: update()
    Student-->>Game: state
    Game->>Policy: decide(state)
    Policy->>Laya: inference
    Laya-->>Policy: probabilities
    Policy-->>Game: action
    Game->>Math: generate(action)
    Math-->>Game: next problem
    Game-->>API: response
    API-->>UI: feedback + next problem
```
