# must_haves_json.py
"""
Генерация второй части json (вопросы по must haves, логика для зарплаты) вручную.
"""

import re
import openai
from settings import OPENAI_API_KEY

def detect_language(job_description):
    """
    Определяет язык job description с помощью OpenAI.
    Возвращает код языка: 'en', 'ru', 'es', 'it', и т.д.
    """
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "Determine the language of the given text. Respond with only the language code (en, ru, es, it, de, fr, etc.)"
                },
                {
                    "role": "user", 
                    "content": job_description[:500]  # Берем первые 500 символов для анализа
                }
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip().lower()
    except Exception:
        return "en"  # Fallback to English

def translate_text(text, target_language):
    """
    Переводит текст на целевой язык с помощью OpenAI.
    """
    # Определяем язык текста (если нужно, можно добавить функцию detect_language(text))
    if not text or not target_language:
        return text
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Translate the following text to {target_language}. Return only the translation, nothing else."},
                {"role": "user", "content": text}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return text

def paraphrase_question(question, target_language):
    """
    Переформулирует вопрос с помощью OpenAI, чтобы он звучал естественно на нужном языке.
    """
    try:
        system_message = {
            'ru': 'Ты — помощник по формулировке вопросов для собеседования на русском языке.',
            'en': 'You are an assistant for phrasing interview questions in English.',
            'es': 'Eres un asistente para formular preguntas de entrevista en español.',
            'de': 'Du bist ein Assistent für die Formulierung von Interviewfragen auf Deutsch.',
            'fr': 'Tu es un assistant pour formuler des questions d\'entretien en français.',
            'it': 'Sei un assistente per formulare domande di colloquio in italiano.'
        }.get(target_language, 'You are an assistant for phrasing interview questions.')
        prompt = {
            'ru': f"Сделай из вопроса '{question}' естественный, грамотный вопрос для собеседования на русском языке. Вопрос должен сохранить формат ответов Да/нет. Верни только сам вопрос, без пояснений.",
            'en': f"Make the question '{question}' sound like a natural, well-phrased interview question in English. The question should keep the Yes/No answer format. Return only the question, no explanations.",
            'es': f"Haz que la pregunta '{question}' suene como una pregunta de entrevista natural y bien formulada en español. La pregunta debe mantener el formato de respuesta Sí/No. Devuelve solo la pregunta, sin explicaciones.",
            'de': f"Formuliere die Frage '{question}' als eine natürlich klingende, gut formulierte Interviewfrage auf Deutsch. Die Frage soll das Ja/Nein-Antwortformat beibehalten. Gib nur die Frage zurück, keine Erklärungen.",
            'fr': f"Formule la question '{question}' comme une question d'entretien naturelle et bien formulée en français. La question doit conserver le format de réponse Oui/Non. Retourne uniquement la question, sans explications.",
            'it': f"Rendi la domanda '{question}' una domanda di colloquio naturale e ben formulata in italiano. La domanda deve mantenere il formato di risposta Sì/No. Restituisci solo la domanda, senza spiegazioni."
        }.get(target_language, f"Make the question '{question}' sound like a natural, well-phrased interview question in {target_language}. The question should keep the Yes/No answer format. Return only the question, no explanations.")
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return question

def split_salary_from_must_haves(must_haves):
    salary_lines = []
    other_lines = []
    for line in must_haves:
        if re.search(r'зарплат|salary|budget', line, re.IGNORECASE):
            salary_lines.append(line)
        else:
            other_lines.append(line)
    return salary_lines, other_lines

def generate_musthaves_questions_json(must_haves, job_description, budget=None, currency=None):
    """
    Генерирует список вопросов по must haves (fields) и jumps/logic для зарплаты.
    Возвращает tuple: (fields, logic)
    """
    fields = []
    logic = []
    salary_field_ref = None
    salary_question_idx = None
    flex_choice_id = None
    
    # Определяем язык job description
    target_language = detect_language(job_description)
    
    # Переводим стандартные фразы
    yes_label = translate_text("Да", target_language)
    no_label = translate_text("Нет", target_language)
    experience_template = translate_text("У вас есть опыт: {must}?", target_language)
    # Формируем строку валюты для вопроса про зарплату
    salary_currency = currency if currency else 'руб.'
    salary_currency_str = f" ({salary_currency})"
    salary_question = translate_text(f"Каковы ваши ожидания по зарплате{salary_currency_str}?", target_language)
    budget_question_template = translate_text("Наш бюджет {budget}. Вы готовы к нему?", target_language)
    
    no_choice_refs = []  # Собираем все ref'ы ответов "Нет"
    
    # --- Новый блок: выделяем и удаляем строки про зарплату ---
    salary_lines, must_haves_wo_salary = split_salary_from_must_haves(must_haves)

    # Генерируем вопросы по must haves (без зарплаты)
    for idx, must in enumerate(must_haves_wo_salary):
        ref = f"musthave_{idx+1}"
        # Генерируем уникальные choice IDs для вопросов да/нет
        no_choice_id = f"no_choice_{idx+1}"
        no_choice_refs.append(no_choice_id)
        raw_question = experience_template.format(must=must)
        paraphrased_question = paraphrase_question(raw_question, target_language)
        field = {
            "title": paraphrased_question,
            "ref": ref,
            "type": "multiple_choice",
            "properties": {
                "choices": [
                    {"label": yes_label, "ref": f"yes_choice_{idx+1}"},
                    {"label": no_label, "ref": no_choice_id}
                ]
            },
            "validations": {"required": True}
        }
        fields.append(field)

    # Вопрос про зарплату добавляем только если есть строка про зарплату
    if salary_lines:
        ref = f"musthave_{len(fields)+1}"
        salary_field_ref = ref
        salary_question_idx = len(fields)
        field = {
            "title": salary_question,
            "ref": ref,
            "type": "number",
            "validations": {"required": True}
        }
        fields.append(field)
    else:
        salary_field_ref = None
        salary_question_idx = None

    # Вопрос про гибкость бюджета (flex_field) всегда добавляем, если есть salary_field_ref и budget > 0
    print(f"DEBUG: salary_field_ref={salary_field_ref}, budget={budget}, currency={currency}")
    budget_value = 0
    if budget is not None:
        try:
            budget_str = str(budget).replace(' ', '').replace(',', '').replace('.', '')
            budget_value = float(budget_str)
        except Exception as e:
            print(f"DEBUG: Ошибка преобразования budget: {budget} ({e})")
            budget_value = 0
    if salary_field_ref and budget_value > 0:
        flex_ref = "salary_flexibility"
        flex_choice_no_id = "flex_no_choice"
        budget_str_disp = f"{budget} {salary_currency}"
        flex_field = {
            "title": budget_question_template.format(budget=budget_str_disp),
            "ref": flex_ref,
            "type": "multiple_choice",
            "properties": {
                "choices": [
                    {"label": yes_label, "ref": "flex_yes_choice"},
                    {"label": no_label, "ref": flex_choice_no_id}
                ]
            },
            "validations": {"required": True}
        }
        fields.insert(salary_question_idx+1, flex_field)

        # Логика: jump на flex_field только если ожидаемая зарплата выше бюджета
        logic.append({
            "type": "field",
            "ref": salary_field_ref,
            "actions": [
                {
                    "action": "jump",
                    "details": {
                        "to": {
                            "type": "field",
                            "value": flex_ref
                        }
                    },
                    "condition": {
                        "op": "greater_than",
                        "vars": [
                            {"type": "field", "value": salary_field_ref},
                            {"type": "constant", "value": budget_value}
                        ]
                    }
                }
            ]
        })
    
    # Логика обработки must-have ответов перенесена в process_submission функцию
    # В Typeform оставляем только логику для зарплаты (если есть)
    
    return fields, logic

# TODO: реализовать генерацию must have вопросов и логику для зарплаты 