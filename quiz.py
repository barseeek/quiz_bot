import re
import os


def get_questions(filename):
    base_dir = os.path.dirname(__file__)
    filename = os.path.join(base_dir, filename)
    with open(filename, encoding='koi8-r') as file:
        text = file.read()

    pattern = re.compile(r"Вопрос \d+:(.*?)Ответ:\s*(.*?)(?=Комментарий:|Источник:|Автор:|$)", re.S)

    question_answer = {}

    matches = pattern.findall(text)
    for match in matches:
        question_text = match[0].strip()
        answer_text = match[1].strip()

        question_lines = re.split(r"\d+\.\s+", question_text)[1:]
        answer_lines = re.split(r"\d+\.\s+", answer_text)[1:]

        for question, answer in zip(question_lines, answer_lines):
            question = question.strip().rstrip('.')
            answer = answer.strip().rstrip('.')
            question_answer[question] = answer
    return question_answer
