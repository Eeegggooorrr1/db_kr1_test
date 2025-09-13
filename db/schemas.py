from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any

import math
from pydantic import BaseModel, validator, Field, root_validator
from sqlalchemy.orm import validates
from sqlalchemy.exc import IntegrityError

from db.models import AttackTypeEnum


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_dt_to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

AttackTypeT = AttackTypeEnum if AttackTypeEnum is not None else Any


class ImageCreate(BaseModel):
    run_id: int
    file_path: str = Field(..., max_length=500)
    original_name: Optional[str] = Field(None, max_length=255)
    attack_type: AttackTypeT
    added_date: Optional[datetime] = None
    coordinates: Optional[List[int]] = None

    @validator("file_path")
    def file_path_non_empty(cls, v: str) -> str:
        v2 = v.strip()
        if not v2: raise ValueError("file_path не может быть пустой строкой")
        if len(v2) > 500: raise ValueError("file_path длиннее 500 символов")
        return v2

    @validator("original_name")
    def original_name_trim(cls, v: Optional[str]) -> Optional[str]:
        if v is None: return None
        vv = v.strip()
        return vv if vv != "" else None

    @validator("added_date", pre=True, always=False)
    def added_date_not_in_future(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None: return None
        if not isinstance(v, datetime): raise ValueError("added_date должен быть datetime")
        dt = _ensure_dt_to_utc(v)
        if dt > _now_utc(): raise ValueError("added_date не может быть в будущем")
        return dt

    @validator("coordinates")
    def coordinates_format(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is None:
            return None
        if not isinstance(v, (list, tuple)):
            raise ValueError("coordinates должен быть списком из 4 целых чисел")
        coords: List[int] = []
        for item in v:
            if isinstance(item, bool):
                raise ValueError("coordinates должны быть целыми числами, не булевыми")
            if not isinstance(item, int):
                if isinstance(item, float) and item.is_integer():
                    iv = int(item)
                else:
                    raise ValueError("все элементы coordinates должны быть целыми числами")
            else:
                iv = item
            coords.append(iv)
        x1, y1, x2, y2 = coords
        if any(c < 0 for c in coords): raise ValueError("все координаты должны быть неотрицательными")
        if x2 <= x1 or y2 <= y1: raise ValueError("должно выполняться x2 > x1 и y2 > y1")
        return coords


class RunCreate(BaseModel):
    experiment_id: int
    run_date: Optional[datetime] = None
    accuracy: Optional[float] = None
    flagged: Optional[bool] = None
    images: Optional[List[ImageCreate]] = None

    @validator("run_date", pre=True, always=False)
    def run_date_not_future(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None: return None
        if not isinstance(v, datetime): raise ValueError("run_date должен быть datetime")
        dt = _ensure_dt_to_utc(v)
        if dt > _now_utc(): raise ValueError("run_date не может быть в будущем")
        return dt

    @validator("accuracy")
    def accuracy_between_0_1(cls, v: Optional[float]) -> Optional[float]:
        if v is None: return None
        try:
            fv = float(v)
        except Exception: raise ValueError("accuracy должно быть числом")
        if not (0.0 <= fv <= 1.0): raise ValueError("accuracy должно быть в диапазоне [0.0, 1.0]")
        return fv

    @validator("flagged")
    def flagged_must_be_bool(cls, v: Optional[bool]) -> Optional[bool]:
        if v is None: return None
        if not isinstance(v, bool): raise ValueError("flagged должно быть булевым значением (True/False)")
        return v

class ExperimentCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    created_date: Optional[date] = None
    runs: Optional[List[RunCreate]] = None

    @validator("name")
    def name_not_empty(cls, v: str) -> str:
        v2 = v.strip()
        if not v2: raise ValueError("name не может быть пустой строкой")
        if len(v2) > 255: raise ValueError("name длиннее 255 символов")
        return v2

    @validator("description")
    def description_trim(cls, v: Optional[str]) -> Optional[str]:
        if v is None: return None
        vv = v.strip()
        return vv if vv != "" else None

    @validator("created_date", pre=True, always=False)
    def created_date_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return None
        if not isinstance(v, date): raise ValueError("created_date должен быть date")
        if v > date.today(): raise ValueError("created_date не может быть в будущем")
        return v