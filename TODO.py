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
    
    def get_id_for_delete(self):
        print('введите нужные id через enter, для окончания ввода нажмите enter, ничего не вводя')
        id_spisok = []
        while True:
           a = input()
           if not a: break
           id_spisok.append(a)
        print( 'конец ввода')
        return id_spisok

#класс для работы с sql 
class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname='postgres',
                user='postgres',
                password='792100',
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
                    SELECT t.task_id, u.username, t.task
                    FROM users_task t
                    JOIN name_users u ON t.user_id = u.user_id
                    ORDER BY u.username, t.task_id
                ''')
                all_tasks = cursor.fetchall()
        
                if not all_tasks:
                    print('В таблице нет данных')
                    return
        
                print("\nЗадачи всех пользователей:")
                current_user = None
                for task_id, username, task in all_tasks:
                    if username != current_user:
                        print(f"\nПользователь: {username}")
                        current_user = username
                    print(f"id: {task_id} - задание: {task}")
            
            except Exception as e:
                print(f"Ошибка при получении данных: {e}")
    
    #удаляем задачи для определенного юзера
    def delete_user_tasks(self, username):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('SELECT user_id FROM name_users WHERE username = %s', (username,))
                user_result = cursor.fetchone()
            
                if not user_result:
                    print(f"Пользователь {username} не найден")
                    return
            
                cursor.execute('DELETE FROM users_task WHERE user_id = %s', (user_result[0],))
                self.conn.commit()
                print(f"Все задачи пользователя {username} удалены")
            except Exception as e:
                self.conn.rollback()
                print(f"Ошибка при удалении задач: {e}")
    
    #удаляем все
    def delete_all(self):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('TRUNCATE TABLE users_task, name_users RESTART IDENTITY CASCADE')
                self.conn.commit()
                print("Все данные удалены")
            except Exception as e:
                self.conn.rollback()
                print(f"Ошибка при очистке таблиц: {e}")

    #удаляем только по айди заданий
    def delete_only_id_tasks(self, id_for_delete):
        with self.conn.cursor() as cursor:
            try:
                for task_id in id_for_delete:
                    if task_id in id_for_delete:
                        cursor.execute('DELETE FROM users_task WHERE task_id = %s', (task_id,))
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                print(f"Ошибка при удалении задач: {e}")

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
    print('\nХотите удалить все данные из таблицы? Напишите - 1 ')
    print('Хотите удалить данные определенного имени? Напишите - 2  ')
    print('Хотите удалить данные определенного id? Напишите - 3  ')
    print('Если вам ничего не нужно, нажмите enter')
    while True:
        a = input().strip()
        if a in ('2'): 
            username = console_input.get_username()
            db.delete_user_tasks(username)
            db.get_all_info()
            break
        elif a in ('1'):
            db.delete_all()
            db.get_all_info()
            print('выполнено успешно!')
            break
        elif a in ('3'): 
            id_for_delete = console_input.get_id_for_delete()
            db.delete_only_id_tasks(id_for_delete)
            db.get_all_info()
            


    db.close()



main()