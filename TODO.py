from pathlib import Path
import psycopg2

#класс для получения списка задач и имени
class ConsoleInput:
    def get_choice(self):
        print('Выберите способ ввода, консоль - 1, файл - 2')
        while True:
            a = input().strip()
            if a.lower() in ('1', 'консоль'):   return self.get_input()
            elif a.lower() in ('2', 'файл'):    return self.get_file()
            else: print('Некорректный ввод, попробуйте снова')

    def get_input(self):
        print('Вы выбрали консоль!')
        print('Можете вводить строки, если хотите закончить напишите на конце строки "&"')
        spisok = []
        while True:
            string = input().strip()
            if string.endswith('&'):
                print('Вы ввели "&", конец ввода')
                if not string.strip(): break
                spisok.append(string.strip('&'))
                break
            if not string: continue
            spisok.append(string)
        return spisok

    def get_file(self):
        print('Вы выбрали файл!')
        spisok = []
        while not spisok:
            try:
                way = input('Укажите путь к файлу: ')
                spisok = Path(way).read_text(encoding='utf-8').splitlines()
            except Exception as e:
                print(f'Произошла ошибка {e}, попробуйте снова')
        return spisok

    def get_username(self):
        return input('Введите имя пользователя: ').strip().lower()

#класс для работы с sql 
class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname='postgres',
                user='postgres',
                password='simple',
                host='localhost',
                port='5432'
            )
            self.create_tables()
        except Exception as e:
            print(f'Произошла ошибка подключения: {e}')
            raise
    
    #создаем таблицы
    def create_tables(self):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS name_users (
                        user_id SERIAL PRIMARY KEY,
                        username varchar(25) NOT NULL UNIQUE
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users_task (
                        task_id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        task TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES name_users(user_id),
                        UNIQUE (user_id, task)
                    )
                ''')
                self.conn.commit()
            except Exception as e:
                print(f"Ошибка при создании таблиц: {e}")
                self.conn.rollback()
                raise
               
    #сохраняем полученные данные в таблицы
    def save_tasks(self, username, tasks):
        with self.conn.cursor() as cursor:
            try:
               
                cursor.execute('''
                    INSERT INTO name_users (username) 
                    VALUES (%s)
                    ON CONFLICT (username) DO NOTHING
                    RETURNING user_id
                ''', (username,))
                
                result = cursor.fetchone()
                if result:
                    user_id = result[0]
                else:
                    cursor.execute('SELECT user_id FROM name_users WHERE username = %s', (username,))
                    user_id = cursor.fetchone()[0]
                
                
                for task in tasks:
                    if task:
                        cursor.execute('''
                            INSERT INTO users_task (user_id, task)
                            VALUES (%s, %s)
                            ON CONFLICT (user_id, task) DO NOTHING
                        ''', (user_id, task))
                
                self.conn.commit()
            except Exception as e:
                print(f"Ошибка при сохранении задач: {e}")
                self.conn.rollback()
                raise

    # получаем всю информацию из таблиц для всех пользователей
    def get_all_info(self):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('''
                    SELECT u.username, t.task
                    FROM users_task t
                    JOIN name_users u ON t.user_id = u.user_id
                    ORDER BY u.username, t.task
                ''')
                all_tasks = cursor.fetchall()
                if not all_tasks: return print('В таблице пусто')
                print("\nЗадачи всех пользователей:")
                current_user = None
                for username, task in all_tasks:
                    if username != current_user:
                        print(f"\nПользователь: {username}")
                        current_user = username
                    print(f"  - {task}")
            
            except Exception as e:
                print(f"Ошибка при получении задач: {e}")

    # удаляем задачи заданного имени
    def delete_user_tasks(self, username):
        with self.conn.cursor() as cursor:
            try:
              
                cursor.execute('SELECT user_id FROM name_users WHERE username = %s', (username,))
                user_result = cursor.fetchone()
                
                if not user_result:
                    print(f"Пользователь {username} не найден")
                    return
                
                user_id = user_result
                cursor.execute('''
                    DELETE FROM users_task 
                    WHERE user_id = %s
                ''', (user_id,))
                self.conn.commit()
            except Exception as e:
                print(f"Ошибка при удалении задач: {e}")
                self.conn.rollback()
                raise

    def close(self):
        
        self.conn.close()


def main():
    console_input = ConsoleInput()
    db = Database()

    username = console_input.get_username()
    data = console_input.get_choice() 

    if not data:
        print('Нечего записывать, список пустой')
        return
    db.save_tasks(username, data)
    db.get_all_info() 

    if input('\nХотите удалить задачи для отдельного пользователя? Напишите да\нет : ').lower() in ('да','хочу'): 
        username = console_input.get_username()
        db.delete_user_tasks(username)
        db.get_all_info()
    db.close()



main()