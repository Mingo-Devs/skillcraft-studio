import openai
from pywebio import start_server
from pywebio.output import put_table
from pywebio.input import input, textarea

api_key = ""
previous_messages = []

def openai_response(question, prompt):
    openai.api_key = api_key
    messages = [{"role": "system", "content": prompt}] + previous_messages + [{"role": "user", "content": question}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=1024,
        top_p=0.3,
        frequency_penalty=0.6,
        presence_penalty=0.0
    )
    return response.choices[0].message['content']

def main():
    global api_key
    api_key = input("Вставьте свой OpenAI API ключ:", type="password")

    prompt = textarea("Вставьте текст вашего навыка для Айки:", rows=3, placeholder="You are a helpful assistant.")

    while True:
        question = input('Отправьте сообщение')
        response = openai_response(question, prompt)
        previous_messages.append({"role": "user", "content": question})
        previous_messages.append({"role": "assistant", "content": response})
        
        put_table([
            ['Вы:', question],
            ['Aika AI:', response]
        ])

if __name__ == '__main__':
    start_server(main, port=8080, debug=False)