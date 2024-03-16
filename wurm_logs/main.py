from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, select
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Mapped
from sqlalchemy import create_engine
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)


class Date(Base):
    __tablename__ = 'date'
    date_id = Column(Integer, primary_key=True)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)

    __table_args__ = (UniqueConstraint('year', 'month', 'day'),)

    def __str__(self):
        return f"{self.year}-{self.month:02d}-{self.day:02d}"


class LogType(Base):
    __tablename__ = 'log_type'
    log_type_id = Column(Integer, primary_key=True)
    message = Column(String, unique=True)


class LogMessage(Base):
    __tablename__ = 'log_message'
    log_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    date_id = Column(Integer, ForeignKey('date.date_id'))
    log_type_id = Column(Integer, ForeignKey('log_type.log_type_id'))
    hour = Column(Integer)
    minute = Column(Integer)
    second = Column(Integer)
    log_type_name = Column(String)

    user = relationship("User")
    date = relationship("Date")
    log_type = relationship("LogType")

    __mapper_args__ = {
        'polymorphic_on': log_type_name,
        'polymorphic_identity': 'log_message',
    }


class LogActions(LogMessage):
    __tablename__ = 'log_actions'
    log_id = Column(Integer, ForeignKey('log_message.log_id'), primary_key=True)
    action = Column(String)

    __table_args__ = (UniqueConstraint('log_id', 'action'),)  # Unique action per log_id

    __mapper_args__ = {
        'polymorphic_identity': 'action',
    }


engine = create_engine('sqlite:///db.sqlite3', echo=False)
Session = sessionmaker(bind=engine)


def create_tables():
    Base.metadata.create_all(engine)


def create_example_data():
    session = Session()

    usernames = [
        'john_doe',
        'jane_smith',
    ]
    for username in usernames:
        result = session.query(User).where(User.username==username).one_or_none()
        if not result:
            user = User(username=username)
            session.add(user)
    user1 = session.execute(select(User).where(User.username == 'john_doe')).scalar_one_or_none()

    now = datetime.datetime.now()
    date1 = session.query(Date).where(Date.year == now.year, Date.month == now.month, Date.day == now.day).one_or_none()
    if not date1:
        date1 = Date(year=now.year, month=now.month, day=now.day)
        session.add(date1)

    log_type1 = session.query(LogType).filter_by(message='You start {action}.').first()
    if not log_type1:
        log_type1 = LogType(message='You start {action}.')
        session.add(log_type1)

    log_message1 = LogActions(
        user=user1,
        date=date1,
        log_type=log_type1,
        hour=now.hour,
        minute=now.minute,
        second=now.second,
        action="to dig",
    )
    session.add(log_message1)

    session.commit()


def reconstruct_messages():
    session = Session()

    log_message: LogMessage
    for log_message in session.query(LogMessage).join(LogActions).filter(LogMessage.log_type_name=='action'):
        full_message = log_message.log_type.message.format(action=log_message.action)
        print(f"{log_message.user.username} - {log_message.date} {log_message.hour:02d}:{log_message.minute:02d}:{log_message.second:02d} - {full_message}")


def main():
    create_tables()
    create_example_data()
    reconstruct_messages()


if __name__ == '__main__':
    main()
