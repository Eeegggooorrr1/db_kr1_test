import logging
from datetime import datetime, date, timezone
from functools import wraps
from typing import Optional, List, Dict, Any, Callable

import math
from pydantic import BaseModel, validator, Field, root_validator
from sqlalchemy.orm import validates
from sqlalchemy.exc import IntegrityError

from db.models import AttackTypeEnum


from pydantic import ValidationError

orig_val = ValidationError.__str__
def change_err(self):
    msgs = [e.get("msg") for e in self.errors()]
    return "\n".join(msgs) if msgs else "какая то ошибка"
ValidationError.__str__ = change_err #я должен сидеть за это в тюрьме



logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def log_validation_errors(field_name: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(cls, v):
            try:
                return func(cls, v)
            except Exception as e:
                from gui.logger_widget import initialize_qt_logger, _qt_handler
                if _qt_handler is None:
                    initialize_qt_logger()
                field = field_name or func.__name__.replace('validate_', '').replace('_non_empty', '')
                error_logger = logging.getLogger('validation')
                error_logger.error(f"Validation error for field '{field}': {e}")
                error_logger.error(f"Invalid value: {repr(v)[:100]}...")
                raise

        return wrapper

    return decorator
def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def dt_to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)



class ImageCreate(BaseModel):
    run_id: int
    file_path: Optional[str] = Field(..., max_length=500)
    original_name: Optional[str] = Field(None, max_length=255)
    attack_type: AttackTypeEnum
    added_date: Optional[datetime] = None
    coordinates: Optional[List[int]] = None

    @validator("file_path")
    @log_validation_errors("file_path")
    def file_path(cls, v: str):
        v2 = v.strip()
        if not v2: raise ValueError("file_path не может быть пустой строкой")
        if len(v2) > 500: raise ValueError("file_path длиннее 500 символов")
        return v2


    @validator("original_name")
    @log_validation_errors("original_name")
    def original_name(cls, v: Optional[str]):
        if v is None: return None
        vv = v.strip()
        return vv if vv != "" else None

    @validator("added_date", pre=True, always=False)
    @log_validation_errors("added_date")
    def added_date(cls, v: Optional[datetime]):
        if v is None: return None
        if not isinstance(v, datetime): raise ValueError("added_date должен быть datetime")
        dt = dt_to_utc(v)
        if dt > now_utc(): raise ValueError("added_date не может быть в будущем")
        return dt

    # @validator("coordinates")
    # @log_validation_errors("coordinates")
    # def coordinates_format(cls, v: Optional[List[int]]):
    #     if v is None:
    #         return None
    #     if not isinstance(v, (list, tuple)):
    #         raise ValueError("coordinates должен быть списком из 4 целых чисел")
    #     coords: List[int] = []
    #     for item in v:
    #         if isinstance(item, bool):
    #             raise ValueError("coordinates должны быть целыми числами, не булевыми")
    #         if not isinstance(item, int):
    #             if isinstance(item, float) and item.is_integer():
    #                 iv = int(item)
    #             else:
    #                 raise ValueError("все элементы coordinates должны быть целыми числами")
    #         else:
    #             iv = item
    #         coords.append(iv)
    #     return coords

class ImageEdit(BaseModel):
    run_id:int
    attack_type: AttackTypeEnum

class RunCreate(BaseModel):
    experiment_id: int
    run_date: Optional[datetime] = None
    accuracy: Optional[float] = None
    flagged: Optional[bool] = None


    @validator("run_date", pre=True, always=False)
    @log_validation_errors("run_date")
    def run_date(cls, v: Optional[datetime]):
        if v is None: return None
        if not isinstance(v, datetime): raise ValueError("run_date должен быть datetime")
        dt = dt_to_utc(v)
        if dt > now_utc(): raise ValueError("run_date не может быть в будущем")
        return dt

    @validator("accuracy")
    @log_validation_errors("accuracy")
    def accuracy(cls, v: Optional[float]):
        if v is None: return None
        try:
            fv = float(v)
        except Exception: raise ValueError("accuracy должно быть числом")
        if not (0.0 <= fv <= 1.0): raise ValueError("accuracy должно быть в диапазоне [0.0, 1.0]")
        return fv

    @validator("flagged")
    @log_validation_errors("flagged")
    def flagged_bool(cls, v: Optional[bool]):
        if v is None: return None
        if not isinstance(v, bool): raise ValueError("flagged должно быть булевым значением")
        return v
class RunEdit(BaseModel):
    experiment_id: int
    accuracy: float
    flagged: bool

class ExperimentCreate(BaseModel):
    experiment_id: Optional[int] = None
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    created_date: Optional[date] = None


    @validator("name")
    @log_validation_errors("name")
    def name_not_empty(cls, v: str):
        v2 = v.strip()
        if not v2: raise ValueError("name не может быть пустой строкой")
        if len(v2) > 255: raise ValueError("name длиннее 255 символов")
        return v2

    @validator("description")
    @log_validation_errors("description")
    def descript(cls, v: Optional[str]):
        if v is None: return None
        vv = v.strip()
        return vv if vv != "" else None

    @validator("created_date", pre=True, always=False)
    @log_validation_errors("created_date")
    def created_date(cls, v: Optional[date]):
        if v is None:
            return None
        if not isinstance(v, date): raise ValueError("created_date должен быть date")
        if v > date.today(): raise ValueError("created_date не может быть в будущем")
        return v