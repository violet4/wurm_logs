from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
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


class LogType(Base):
    __tablename__ = 'log_type'
    log_type_id = Column(Integer, primary_key=True)
    message = Column(String)


class LogMessage(Base):
    __tablename__ = 'log_message'
    log_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    date_id = Column(Integer, ForeignKey('date.date_id'))
    log_type_id = Column(Integer, ForeignKey('log_type.log_type_id'))
    hour = Column(Integer)
    minute = Column(Integer)
    second = Column(Integer)
    user = relationship("User")
    date = relationship("Date")
    log_type = relationship("LogType")


class LogActions(LogMessage):
    __tablename__ = 'log_actions'
    log_id = Column(Integer, ForeignKey('log_message.log_id'), primary_key=True)  # Inherit log_id
    action = Column(String)


engine = create_engine('sqlite:///db.sqlite3', echo=False)  # Change database name if needed

def create_tables():
    Base.metadata.create_all(engine)


def create_example_data():
    Session = sessionmaker(bind=engine)
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
    user1 = session.query(User).where(User.username==usernames[0]).one()

    today = datetime.date.today()
    date1 = Date(year=today.year, month=today.month, day=today.day)
    session.add(date1)

    log_type1 = LogType(message='You start {action}.')
    session.add(log_type1)

    log_message1 = LogActions(
        user=user1,
        date=date1,
        log_type=log_type1,
        hour=10,
        minute=35,
        second=20,
        action='to dig'
    )
    session.add(log_message1)

    session.commit()


def reconstruct_messages():
    Session = sessionmaker(bind=engine)
    session = Session()

    for action_log in session.query(LogActions):
        full_message = action_log.log_type.message.format(action=action_log.action)
        print(f"{action_log.user.username} - {action_log.date} - {full_message}")


def main():
    create_tables()
    create_example_data()
    reconstruct_messages()


if __name__ == '__main__':
    main()
