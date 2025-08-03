import psycopg2

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
        except psycopg2.OperationalError as e:
            print(f'Произошла ошибка подключения: {e}')
            raise
    
    #создаем таблицы
    def create_tables(self):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users_names (
                        user_id SERIAL PRIMARY KEY,
                        username varchar(25) NOT NULL UNIQUE
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users_tasks (
                        task_id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        task TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users_names(user_id)
                    )
                ''')
                self.conn.commit()
            except psycopg2.Error as e:
                print(f"Ошибка при создании таблиц: {e}")
                self.conn.rollback()
                raise
               
    #сохраняем полученные данные в таблицы
    def save_tasks(self, username, tasks):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('''
                    INSERT INTO users_names (username) 
                    VALUES (%s)
                    ON CONFLICT (username) DO NOTHING
                    RETURNING user_id
                ''', (username,))
                result = cursor.fetchone()
                if result:  user_id = result[0]
                else:
                    cursor.execute('SELECT user_id FROM users_names WHERE username = %s', (username,))
                    user_id = cursor.fetchone()[0]
                for task in tasks:
                    if task:
                        cursor.execute('''
                            INSERT INTO users_tasks (user_id, task)
                            VALUES (%s, %s)
                            ON CONFLICT (user_id, task) DO NOTHING
                        ''', (user_id, task))
            except psycopg2.Error as e:
                print(f"Ошибка при сохранении задач: {e}")
                raise
            self.conn.commit()

    # получаем всю информацию из таблиц для всех пользователей
    def get_all_info(self):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('''
                    SELECT t.task_id, u.username, t.task
                    FROM users_tasks t
                    JOIN users_names u ON t.user_id = u.user_id
                    ORDER BY u.username, t.task_id
                ''')
                all_tasks = cursor.fetchall()
        
                if not all_tasks:
                    print('В таблице нет данных')
                    return
                print("\nЗадачи всех пользователей:")
                user = None
                for task_id, username, task in all_tasks:
                    if username != user:
                        print(f"\nПользователь: {username}")
                        user = username
                    print(f"id: {task_id} - задание: {task}")
            except psycopg2.Error as e:
                print(f"Ошибка при получении данных: {e}")
    
    #удаляем задачи для определенного юзера
    def delete_user_tasks(self, username):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('SELECT user_id FROM users_names WHERE username = %s', (username,))
                user_result = cursor.fetchone()
            
                if not user_result:
                    print(f"Пользователь {username} не найден")
                    return
            
                cursor.execute('DELETE FROM users_tasks WHERE user_id = %s', (user_result[0],))
                print(f"Все задачи пользователя {username} удалены")
            except psycopg2.Error as e:
                print(f"Ошибка при удалении задач: {e}")
            self.conn.commit()

    #удаляем все
    def delete_all(self):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute('TRUNCATE TABLE users_tasks, users_names RESTART IDENTITY CASCADE')
                print("Все данные удалены")
            except psycopg2.Error as e:
                print(f"Ошибка при очистке таблиц: {e}")
            self.conn.commit()

    #удаляем только по айди заданий
    def delete_only_id_tasks(self, id_for_delete):
        with self.conn.cursor() as cursor:
            try:
                for task_id in id_for_delete:
                    if task_id in id_for_delete:
                        cursor.execute('DELETE FROM users_tasks WHERE task_id = %s', (task_id,))
            except psycopg2.Error as e:
                print(f"Ошибка при удалении задач: {e}")
            self.conn.commit()

    def close(self):
        self.conn.close()