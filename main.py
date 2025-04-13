from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, text, func, select
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from enum import Enum

# Создаем базовый класс
Base = declarative_base()

# Enum для статусов оплаты
class PaymentStatus(str, Enum):
    WAITING = "ожидание"
    CONFIRMED = "подтверждено"
    CANCELLED = "отменено"
    CERTIFICATE = "сертификат"

# Модель мероприятия
class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    name = Column(String, nullable=False)
    master = Column(String, nullable=False)
    available_seats = Column(Integer, nullable=False)

    registrations = relationship("Registration", back_populates="event")

    @hybrid_property
    def remaining_seats(self):
        confirmed_count = sum(1 for r in self.registrations
                            if r.payment_status in [PaymentStatus.WAITING,
                                                  PaymentStatus.CONFIRMED,
                                                  PaymentStatus.CERTIFICATE])
        return self.available_seats - confirmed_count

    @remaining_seats.expression
    def remaining_seats(cls):
        return cls.available_seats - (
            select(func.count(Registration.id))
            .where(Registration.event_id == cls.id)
            .where(Registration.payment_status.in_([
                PaymentStatus.WAITING,
                PaymentStatus.CONFIRMED,
                PaymentStatus.CERTIFICATE
            ]))
            .scalar_subquery()
        )

# Модель клиента
class Client(Base):
    __tablename__ = 'clients'

    tg_id = Column(Integer, primary_key=True)
    tg_username = Column(String)
    full_name = Column(String)
    phone = Column(String)
    email = Column(String)

    registrations = relationship("Registration", back_populates="client")

# Модель регистрации
class Registration(Base):
    __tablename__ = 'registrations'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    client_tg_id = Column(Integer, ForeignKey('clients.tg_id'), nullable=False)
    payment_status = Column(String)

    event = relationship("Event", back_populates="registrations")
    client = relationship("Client", back_populates="registrations")

# Создаем подключение к базе данных
engine = create_engine(
    'sqlite:///events.db',
    connect_args={
        'check_same_thread': False,
        'timeout': 30.0
    }
)

# Настройка базы данных
with engine.connect() as conn:
    conn.execute(text("PRAGMA journal_mode=WAL"))
    conn.execute(text("PRAGMA synchronous=NORMAL"))

# Создаем таблицы
Base.metadata.create_all(engine)

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()


def get_events_list():
    """
    Возвращает список мероприятий в виде списка списков
    Каждый внутренний список содержит:
    [id, date, time, name, master, available_seats, remaining_seats]
    """
    try:
        events = session.query(Event).all()
        return [
            [
                event.id,
                event.date,
                event.time,
                event.name,
                event.master,
                event.available_seats,
                event.remaining_seats
            ]
            for event in events
        ]
    except Exception as e:
        print(f"Ошибка при получении списка мероприятий: {e}")
        return []

def print_all_data():
    """Выводит все данные из базы"""
    try:
        # Вывод мероприятий
        print("\nВсе мероприятия:")
        events = session.query(Event).all()
        for event in events:
            print(f"{event.id}: {event.name} ({event.date} {event.time}), "
                  f"Мастер: {event.master}, "
                  f"Мест: {event.available_seats}/{event.remaining_seats}")

        # Вывод клиентов
        print("\nВсе клиенты:")
        clients = session.query(Client).all()
        for client in clients:
            print(f"{client.tg_id}: {client.full_name}, Телефон: {client.phone}")

        # Вывод регистраций
        print("\nВсе регистрации:")
        registrations = session.query(Registration).all()
        for reg in registrations:
            print(f"ID:{reg.id} Мероприятие:{reg.event_id} "
                  f"Клиент:{reg.client_tg_id} Статус:{reg.payment_status}")

    except Exception as e:
        print(f"Ошибка при выводе данных: {e}")

# 1. Функция создания пользователя (только tg_id обязательное)
def create_client(client_data):
    """
    Создает нового клиента (обязателен только tg_id)
    :param client_data: [tg_id, full_name=None, phone=None, tg_username=None, email=None]
    :return: созданный объект Client или None при ошибке
    """
    if not client_data or not client_data[0]:
        return None

    try:

        tg_id = int(client_data[0])
        # Проверяем существование клиента
        existing_client = session.get(Client, tg_id)
        if existing_client:
            return existing_client



        # Убедимся, что список достаточно длинный
        while len(client_data) < 5:
            client_data.append(None)

        client = Client(
            tg_id=int(client_data[0]),
            full_name=client_data[1],
            phone=client_data[2],
            tg_username=client_data[3],
            email=client_data[4]
        )
        session.add(client)
        session.commit()
        return client
    except Exception as e:
        session.rollback()
        print(f"Ошибка при создании клиента: {e}")
        return None


# 2. Функция обновления пользователя (простое обновление по словарю)
def update_client(tg_id, update_data):
    """
    Обновляет данные клиента
    :param tg_id: ID клиента в Telegram
    :param update_data: словарь {поле: новое_значение}
    :return: обновленный объект Client или None если не найден
    """
    client = session.get(Client, tg_id)
    if not client:
        return None

    try:
        for field, value in update_data.items():
            if hasattr(client, field):
                setattr(client, field, value)
        session.commit()
        return client
    except Exception as e:
        session.rollback()
        print(f"Ошибка при обновлении клиента {tg_id}: {e}")
        return None


# 3. Функция создания регистрации
def create_registration(event_id, client_tg_id, status):
    """
    Создает новую регистрацию
    :param event_id: ID мероприятия
    :param client_tg_id: ID клиента в Telegram
    :param status: статус из PaymentStatus
    :return: созданный объект Registration или None при ошибке
    """
    try:
        registration = Registration(
            event_id=int(event_id),
            client_tg_id=int(client_tg_id),
            payment_status=status
        )
        session.add(registration)
        session.commit()
        return registration
    except Exception as e:
        session.rollback()
        print(f"Ошибка при создании регистрации: {e}")
        return None


# 4. Функция обновления статуса регистрации
def update_registration_status(registration_id, new_status):
    """
    Обновляет статус регистрации по ID регистрации
    :param registration_id: ID регистрации в таблице registrations
    :param new_status: новый статус из PaymentStatus
    :return: True если обновлено успешно, False если ошибка или не найдено
    """
    try:
        registration = session.get(Registration, registration_id)
        if not registration:
            print(f"Регистрация с ID {registration_id} не найдена")
            return False

        registration.payment_status = new_status
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Ошибка при обновлении статуса регистрации {registration_id}: {e}")
        return False


# 5. Функция синхронизации мероприятий (простая реализация)
def sync_events(events_data):
    """
    Обновляет список мероприятий (полная синхронизация)
    :param events_data: список списков [id, date, time, name, master, available_seats]
    """
    if not events_data:
        return

    try:
        # Получаем все текущие ID мероприятий
        current_ids = {e[0] for e in session.query(Event.id).all()}
        new_ids = {int(e[0]) for e in events_data if e and e[0]}

        # Удаляем мероприятия, которых нет в новых данных
        session.query(Event).filter(Event.id.notin_(new_ids)).delete(synchronize_session=False)

        # Добавляем/обновляем мероприятия
        for event_data in events_data:
            if len(event_data) < 6 or not event_data[0]:
                continue

            event_id = int(event_data[0])
            event = session.get(Event, event_id)

            if event:
                # Обновляем существующее мероприятие
                event.date = event_data[1]
                event.time = event_data[2]
                event.name = event_data[3]
                event.master = event_data[4]
                event.available_seats = int(event_data[5])
            else:
                # Добавляем новое мероприятие
                event = Event(
                    id=event_id,
                    date=event_data[1],
                    time=event_data[2],
                    name=event_data[3],
                    master=event_data[4],
                    available_seats=int(event_data[5]))
                session.add(event)

                session.commit()
    except Exception as e:
        session.rollback()
        print(f"Ошибка при синхронизации мероприятий: {e}")


# Пример использования
if __name__ == "__main__":
    """
    # 1. Создаем клиента только с tg_id
    new_client = create_client([123])
    print(f"Создан клиент только с tg_id: {new_client.tg_id if new_client else 'ошибка'}")

    # 2. Обновляем клиента (добавляем данные)
    update_client(123, {
        "full_name": "Новый Клиент",
        "phone": "+79998887766",
        "email": "new@example.com"
    })
    updated_client = session.get(Client, 123)
    print(f"Обновленный клиент: {updated_client.full_name if updated_client else 'не найден'}")

    # 3. Создаем регистрацию
    create_registration(1, 123, PaymentStatus.WAITING)

    # 4. Обновляем статус регистрации
    update_registration_status(1, 987654, PaymentStatus.CONFIRMED)

    # 5. Полная синхронизация мероприятий
    sync_events([
        [1, "2023-12-01", "18:00", "Новое название", "Новый мастер", 20],
        [2, "2023-12-02", "19:00", "Другое мероприятие", "Другой мастер", 15]
    ])
    """

    #print(get_events_list())
    # Выводим все данные
    #print_all_data()

