from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime
from typing import Optional, List

Base = declarative_base()

DATABASE_URL = "sqlite:///travel_planning.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    itineraries = relationship("Itinerary", back_populates="user", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    budget_log = Column(Text, nullable=True)

    user = relationship("User", back_populates="itineraries")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=True)
    item = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="expenses")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def register_user(username: str, password: str) -> bool:
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return False
        new_user = User(username=username, password=password)
        db.add(new_user)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()


def authenticate_user(username: str, password: str) -> Optional[User]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username, User.password == password).first()
        return user
    finally:
        db.close()


def get_user_by_username(username: str) -> Optional[User]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        return user
    finally:
        db.close()


def save_itinerary(user_id: int, content: str, budget_log: str = None) -> bool:
    db = SessionLocal()
    try:
        new_itinerary = Itinerary(user_id=user_id, content=content, budget_log=budget_log)
        db.add(new_itinerary)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()


def get_user_itineraries(user_id: int) -> List[Itinerary]:
    db = SessionLocal()
    try:
        itineraries = db.query(Itinerary).filter(Itinerary.user_id == user_id).all()
        return itineraries
    finally:
        db.close()


def get_latest_itinerary(user_id: int) -> Optional[Itinerary]:
    db = SessionLocal()
    try:
        itinerary = db.query(Itinerary).filter(Itinerary.user_id == user_id).order_by(Itinerary.id.desc()).first()
        return itinerary
    finally:
        db.close()


def update_itinerary_budget(itinerary_id: int, budget_log: str) -> bool:
    db = SessionLocal()
    try:
        itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
        if itinerary:
            if itinerary.budget_log:
                itinerary.budget_log += "\n" + budget_log
            else:
                itinerary.budget_log = budget_log
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()


def get_total_budget(user_id: int) -> str:
    db = SessionLocal()
    try:
        expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
        total = sum(exp.amount for exp in expenses)
        return f"{total:.2f}"
    finally:
        db.close()


def add_expense(user_id: int, item: str, amount: float, itinerary_id: int = None) -> bool:
    db = SessionLocal()
    try:
        new_expense = Expense(user_id=user_id, item=item, amount=amount, itinerary_id=itinerary_id)
        db.add(new_expense)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()


def get_user_expenses(user_id: int, itinerary_id: int = None) -> List[Expense]:
    db = SessionLocal()
    try:
        query = db.query(Expense).filter(Expense.user_id == user_id)
        if itinerary_id:
            query = query.filter(Expense.itinerary_id == itinerary_id)
        expenses = query.order_by(Expense.created_at.desc()).all()
        return expenses
    finally:
        db.close()


def delete_expense(expense_id: int) -> bool:
    db = SessionLocal()
    try:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if expense:
            db.delete(expense)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()


def delete_itinerary(itinerary_id: int) -> bool:
    db = SessionLocal()
    try:
        itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
        if itinerary:
            db.delete(itinerary)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()
