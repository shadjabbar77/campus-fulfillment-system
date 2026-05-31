from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class PackageOrder(Base):
    __tablename__ = "package_orders"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=False)
    student_email = Column(String, nullable=False)
    package_code = Column(String, nullable=False, unique=True)
    priority = Column(String, default="STANDARD")
    status = Column(String, default="PENDING")
    locker_number = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
        else_=1,
