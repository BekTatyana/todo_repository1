from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging
import os


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users_names'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = 'users_tasks'
    task_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users_names.user_id'), nullable=False)
    task = Column(Text, nullable=False)
    user = relationship("User", back_populates="tasks")

class Database:
    def __init__(self):
        try:
            load_dotenv()
            db_host = os.getenv("DB_HOST")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME")
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            self.engine = create_engine(database_url, echo=False)
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            logger.info("Связь с базой данных установлена")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подключении к базе данных: {e}")
            raise

    def close_session(self):
        self.session.close()
        logger.info("Сессия базы данных закрыта")

    def save_tasks(self, username, tasks):
        try:
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                user = User(username=username)
                self.session.add(user)
                self.session.flush()
            
            for task in tasks:
                if task:
                    new_task = Task(task=task, user=user)
                    self.session.add(new_task)
            
            self.session.commit()
            logger.info(f"Задачи пользователя {username} успешно сохранены")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка при добавлении задач: {e}")
            return False

    def get_all_info(self):
        try:
            users = self.session.query(User).order_by(User.username).all()
            
            if not users:
                print('В базе данных нет пользователей')
                return
            
            print("\nЗадачи всех пользователей:")
            for user in users:
                if  not user.tasks: continue 
                print(f"\nПользователь: {user.username}")
                for task in user.tasks:
                    print(f"ID: {task.task_id}: {task.task}")
        except Exception as e:
            logger.error(f"Ошибка при получении данных: {e}")

    def delete_user_tasks(self, username):
        try:
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                logger.warning(f"Пользователь {username} не найден")
                return
            
            self.session.query(Task).filter(Task.user_id == user.user_id).delete()
            self.session.commit()
            logger.info(f"Все задачи пользователя {username} удалены")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка при удалении задач пользователя: {e}")

    def delete_all(self):
        try:
            self.session.query(Task).delete()
            self.session.query(User).delete()
            self.session.commit()
            logger.info("Все данные удалены из базы")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка при удалении всех данных: {e}")
            return False

    def delete_only_id_tasks(self, task_ids):
        try:   
            ids = list(set(int(id_) for id_ in task_ids if id_.isdigit()))
            
            if not ids:
                logger.warning("Нет корректных ID для удаления")
                return False
                
            deleted_count = self.session.query(Task).filter(Task.task_id.in_(ids)).delete()
            self.session.commit()
            logger.info(f"Удалено {deleted_count} задач")
            return deleted_count > 0
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка при удалении задач по ID: {e}")
            return False
