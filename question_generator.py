import random

used_questions = set()  # Para evitar repeticiones innecesarias

def generate_question(selected_tables):

    while True:
        table = random.choice(selected_tables)  # Selección de tablas
        multiplier = random.randint(1, 10)  # Selecciona un número del 1 al 10
        question_text = f"{table} x {multiplier}"
        answer = table * multiplier

        # Evitar preguntas repetidas en una misma sesión
        if question_text not in used_questions:
            used_questions.add(question_text)
            return {"text": question_text, "answer": answer}
