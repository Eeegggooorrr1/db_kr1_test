from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import Integer, String, Date, Text, func, TIMESTAMP, ForeignKey, JSON, Float, Enum, ARRAY, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from db.database import Base

class AttackTypeEnum(str, enum.Enum):
    no_attack = "no_attack"
    blur = "blur"
    noise = "noise"
    adversarial = "adversarial"
    other = "other"

class Experiment(Base):
    __tablename__ = "experiments"

    experiment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_date: Mapped[date] = mapped_column(Date, server_default=func.current_date())

    runs: Mapped[list["Run"]] = relationship("Run", back_populates="experiment", cascade="all, delete-orphan")


class Run(Base):
    __tablename__ = "runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.experiment_id", ondelete="CASCADE"))
    run_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    flagged: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    experiment: Mapped["Experiment"] = relationship("Experiment", back_populates="runs")
    images: Mapped[list["Image"]] = relationship("Image", back_populates="run", cascade="all, delete-orphan")


class Image(Base):
    __tablename__ = "images"

    image_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.run_id", ondelete="CASCADE"))
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    original_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    attack_type: Mapped[AttackTypeEnum] = mapped_column(Enum(AttackTypeEnum, name="attack_type_enum"), nullable=False)
    added_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("DATE_TRUNC('second', NOW()::timestamp)"))

    coordinates: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer, dimensions=1), nullable=True)

    run: Mapped["Run"] = relationship("Run", back_populates="images")
