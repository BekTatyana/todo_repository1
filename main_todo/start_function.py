import logging
from console import ConsoleInput
from db import Database
from xlsx_and_csv import xlsx_csv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)
    try:
        console = ConsoleInput()
        db = Database()
        
        username = console.get_username()
        tasks = console.get_choice()

        if not tasks:
            logger.warning("Список задач пуст, ничего не будет сохранено")
            return

        xlscsv = xlsx_csv(username=username, spisok=tasks)
        if not xlscsv.add_to_csv() or not xlscsv.add_to_xlsx():
            logger.error("Ошибка при сохранении в файлы")

        if not db.save_tasks(username, tasks):
            logger.error("Ошибка при сохранении задач в БД")
            return

        db.get_all_info()

        while True:
            print('\nМеню удаления:')
            print('1 - Удалить все данные')
            print('2 - Удалить по имени пользователя')
            print('3 - Удалить по ID задачи')
            print('0 - Выход')
            
            a = input('Ваш выбор: ').strip()
            match a:
                case '0': break
                case '1':
                    db.delete_all()
                    db.get_all_info()
                case '2':
                    username_to_delete = console.get_username()
                    db.delete_user_tasks(username_to_delete)
                    db.get_all_info()
                case '3':
                    ids = console.get_id_for_delete()
                    if ids:
                        db.delete_only_id_tasks(ids)
                        db.get_all_info()
                    else: logger.info('вы не подали id для удаления')
                case _ : print('Некорректный ввод')
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
    db.close_session()
    logger.info("Работа программы завершена")



main()


