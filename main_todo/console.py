from pathlib import Path

#класс для получения списка задач и имени
class ConsoleInput:
    def get_choice(self):
        while True:
            print('Выберите способ ввода:')
            print('1 - Консоль   2 - Файл')
            choice = input('Ваш выбор: ').strip().lower()
            if choice in ('1', 'консоль'):
                return self.get_input()
            elif choice in ('2', 'файл'):
                return self.get_file()
            else: print('Некорректный ввод, попробуйте снова')

    def get_input(self):
        print('Вводите задачи (для завершения введите & в конце строки):')
        tasks = []
        while True:
            task = input().strip()
            if task.endswith('&'):
                task = task.strip('&')
                if task:
                    tasks.append(task)
                break
            if task: tasks.append(task)
        return tasks

    def get_file(self):
        while True:
            path = input('Укажите путь к файлу: ').strip()
            try:
                print('Вы выбрали файл!')
                spisok = []
                while  not spisok:
                    way = input('Укажите путь к файлу: ')
                    spisok = Path(way).read_text(encoding='utf-8').splitlines()
            except Exception as e:
                print(f'Ошибка чтения файла: {e}')
            return spisok

    def get_username(self):
        while True:
            username = input('Введите имя пользователя: ').strip()
            if username:
                return username.lower()
            print('Имя не может быть пустым')

    def get_id_for_delete(self):
        print('Введите ID задач для удаления (по одному, 0 для завершения):')
        ids = []
        while True:
            try:
                id_ = input().strip()
                if id_ == '0':
                    break
                if id_.isdigit():
                    ids.append(id_)
                else: print('ID должен быть числом')
            except Exception as e:
                print(f'Ошибка ввода: {e}')
        return ids

