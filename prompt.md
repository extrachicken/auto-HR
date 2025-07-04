# Промпт для генерации вопросов по job description (Typeform)

Сгенерируй 3-6 вопросов для формы Typeform только на основе следующего job description. Не используй must have требования — не формулируй вопросы по must have, только по содержанию job description. Язык вопросов должен совпадать с языком job description.

**ВЕРНИ ТОЛЬКО ВАЛИДНЫЙ JSON-массив объектов, без пояснений, без форматирования, без нумерации, без текста до или после массива.**

Каждый вопрос — объект с полями:
- title (строка, текст вопроса)
- ref (уникальный читаемый идентификатор, латиницей, например: experience, stack, motivation и т.д.)
- type (multiple_choice, short_text, long_text, number и т.д. — только допустимые типы Typeform)
- properties (если применимо: choices для multiple_choice, description и т.д.)
- validations (required: true/false)

**Для всех вопросов типа multiple_choice обязательно указывай следующие поля в properties:**
- choices (варианты ответов)
- allow_multiple_selection (true, если вопрос подразумевает выбор нескольких вариантов, иначе false)
- allow_other_choice (false, если не релевантно)
- randomize (false)
- vertical_alignment (true)

**Если вопрос подразумевает выбор только одного варианта — allow_multiple_selection: false. Если можно выбрать несколько — true. Если не релевантно — всегда false.**

**Запрещено использовать type "yes_no"! Для всех бинарных (да/нет) вопросов используй type "multiple_choice" с полем properties.choices = [ {"label": "Yes"}, {"label": "No"} ]. ЗАПРЕЩЕНО ИСПОЛЬЗОВАТЬ long_text/short_text тип вопросов - только multiple_choice с указанием. Хотя бы 2 вопроса должны быть развернутые с вариантами ответа, как в примере. Ты должен сам определить, нужно ли для твоего вопроса "allow_multiple_selection": true.**

**Не формулируй вопросы по must have требованиям! Только по job description!**

Пример:
```json
[
  {
    "title": "What is your main programming language?",
    "ref": "main_language",
    "type": "multiple_choice",
    "properties": {
      "choices": [
        {"label": "Python"},
        {"label": "JavaScript"},
        {"label": "Java"},
        {"label": "Other"}
      ],
      "allow_multiple_selection": false,
      "allow_other_choice": false,
      "randomize": false,
      "vertical_alignment": true
    },
    "validations": {"required": true}
  },
  {
    "title": "Which of the following tools do you use?",
    "ref": "tools_used",
    "type": "multiple_choice",
    "properties": {
      "choices": [
        {"label": "Jira"},
        {"label": "Trello"},
        {"label": "Asana"},
        {"label": "Other"}
      ],
      "allow_multiple_selection": true,
      "allow_other_choice": false,
      "randomize": false,
      "vertical_alignment": true
    },
    "validations": {"required": true}
  },
  {
    "title": "Do you have experience in eCommerce performance marketing?",
    "ref": "ecommerce_experience",
    "type": "multiple_choice",
    "properties": {
      "choices": [
        {"label": "Yes"},
        {"label": "No"}
      ],
      "allow_multiple_selection": false,
      "allow_other_choice": false,
      "randomize": false,
      "vertical_alignment": true
    },
    "validations": {"required": true}
  }
]
```

**Не добавляй никаких пояснений, форматируй только как JSON-массив!** 