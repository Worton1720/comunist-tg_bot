import telebot
import sqlite3

# Функция для получения пути к файлу в директории, где находится текущий скрипт ###
def F_get_file_path(filename: str) -> str:
    from os.path import dirname, realpath, join

    dir_path = dirname(realpath(__file__))
    try:
        out_path = join(dir_path, filename)
    except Exception:
        out_path = None
    return out_path

bot = telebot.TeleBot('1841813695:AAGXRF-vRgQcNHJvX8iXPaibhZlqF9KVQfE')

keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

# Открываем соединение с базой данных
conn = sqlite3.connect(F_get_file_path('infco.db'))
cursor = conn.cursor()

# Выполняем SQL-запрос для получения всех уникальных категорий
cursor.execute("SELECT DISTINCT name_resource FROM Utilities")
result_resources = cursor.fetchall()  # Получаем все категории в виде списка кортежей

# Преобразуем список кортежей в список строк
buttons = [row[0] for row in result_resources]
conn.close()

keyboard.add(*buttons)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Здравствуйте! Я бот, который поможет вам связаться с городской администрацией по вопросам ЖКХ. Выберите интересующую вас категорию:", reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    category = message.text
    
    if category in buttons:
        
        # Открываем соединение с базой данных
        conn = sqlite3.connect(F_get_file_path('infco.db'))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM Utilities WHERE name_resource = ?", (category,))
        result = cursor.fetchone()

        if result:
            
            # Формируем сообщение автоматически
            text = f'Информация о категории "{category}":\n'
            for i in range(1, len(result)):
                if cursor.description[i][0] == "name_company":
                    text += f'Компания: {result[i]}\n'
                elif cursor.description[i][0] == "contacts_supplier":
                    text += f'Связь: {result[i]}\n'

            bot.send_message(message.chat.id, text)

        else:
            bot.send_message(message.chat.id, 'Информация не найдена')
        # Закрываем соединение с базой данных
        conn.close()
    else:
        bot.send_message(message.chat.id, 'Выберите категорию из списка!')

if __name__ == '__main__':
    bot.polling()
