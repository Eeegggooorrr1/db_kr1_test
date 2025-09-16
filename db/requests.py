from datetime import datetime, UTC
from functools import wraps
from typing import Optional, Any, List

from pydantic import ValidationError
from sqlalchemy import select, desc, text, asc
import db.database
from db.models import Experiment, Run, Image
from db.schemas import ExperimentCreate, RunCreate, ImageCreate
from sqlalchemy.exc import IntegrityError

def with_session(commit: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with db.database.SessionLocal() as session:
                kwargs['session'] = session
                try:
                    result = func(*args, **kwargs)
                    if commit:
                        session.commit()
                        try:
                            if isinstance(result, list):
                                for r in result:
                                    session.refresh(r)
                            else:
                                if result is not None:
                                    session.refresh(result)
                        except Exception:
                            pass
                    return result
                except IntegrityError:
                    session.rollback()
                    raise
                except Exception:
                    session.rollback()
                    raise
        return wrapper
    return decorator

@with_session(commit=True)
def create_experiment(name: str, description: Optional[str] = None, *, session):
    ExperimentCreate(name=name, description=description, created_date=datetime.now().date())
    exp = Experiment(name=name, description=description, created_date=datetime.now().date())
    session.add(exp)
    return exp

@with_session(commit=True)
def create_run(experiment_id: int, accuracy: Optional[float] = None, flagged: Optional[bool] = None, *, session):
    if session.get(Experiment, experiment_id) is None:
        raise ValueError(f"Experiment с id={experiment_id} не найден")
    RunCreate(experiment_id=experiment_id, run_date=datetime.now(UTC), accuracy=accuracy, flagged=flagged)
    run = Run(experiment_id=experiment_id, run_date=datetime.now(UTC), accuracy=accuracy, flagged=flagged)
    session.add(run)
    return run

@with_session(commit=True)
def create_image(run_id: int, file_path: str, attack_type: Any, original_name: Optional[str] = None, added_date: Optional[datetime] = None, coordinates: Optional[List[int]] = None, *, session):
    if session.get(Run, run_id) is None:
        raise ValueError(f"Run с id={run_id} не найден")
    ImageCreate(run_id=run_id, file_path=file_path, original_name=original_name, attack_type=attack_type, added_date=added_date, coordinates=coordinates)
    img = Image(run_id=run_id, file_path=file_path, original_name=original_name, attack_type=attack_type, added_date=added_date, coordinates=coordinates)
    session.add(img)
    return img

@with_session()
def get_experiment_max_id(*, session):
    result = session.execute(text("SELECT nextval('experiments_experiment_id_seq')"))
    return result.scalar()

@with_session()
def get_run_max_id(*, session):
    result = session.execute(text("SELECT nextval('runs_run_id_seq')"))
    return result.scalar()

@with_session()
def get_all_experiments(*, session):
    results = session.execute(select(Experiment)).scalars().all()
    return results

@with_session()
def get_experiment_by_id(experiment_id, *, session):
    experiment = session.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    return experiment

@with_session(commit=True)
def update_experiment(experiment_id, name, description, *, session):
    try:
        update_data = ExperimentCreate(name=name, description=description)
    except ValidationError as e:
        raise ValueError(f"некорректные изменения: {e}") from e
    experiment = session.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if experiment:
        experiment.name = update_data.name
        experiment.description = update_data.description
    return experiment

@with_session(commit=True)
def delete_experiment(experiment_id, *, session):
    experiment = session.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if experiment:
        session.delete(experiment)

@with_session()
def get_all_runs(*, session):
    results = session.execute(select(Run)).scalars().all()
    return results

@with_session()
def get_run_by_id(run_id, *, session):
    run = session.query(Run).filter(Run.run_id == run_id).first()
    return run

@with_session(commit=True)
def update_run(run_id, accuracy, flagged, *, session):
    try:
        update_data = RunCreate(accuracy=accuracy, flagged=flagged)
    except ValidationError as e:
        raise ValueError(f"некорректные изменения: {e}") from e
    run = session.query(Run).filter(Run.run_id == run_id).first()
    if run:
        run.accuracy = update_data.accuracy
        run.flagged = update_data.flagged
    return run

@with_session(commit=True)
def delete_run(run_id, *, session):
    run = session.query(Run).filter(Run.run_id == run_id).first()
    if run:
        session.delete(run)

@with_session()
def get_all_images(*, session):
    images = session.query(Image).all()
    return images

@with_session()
def get_all_images_filtered(filters, *, session):
    query = session.query(Image)
    if filters['attack_type']:
        query = query.filter(Image.attack_type == filters['attack_type'])
    if filters['sort_id'] == 'asc':
        query = query.order_by(asc(Image.image_id))
    elif filters['sort_id'] == 'desc':
        query = query.order_by(desc(Image.image_id))
    if filters['sort_run_id'] == 'asc':
        query = query.order_by(asc(Image.run_id))
    elif filters['sort_run_id'] == 'desc':
        query = query.order_by(desc(Image.run_id))
    if filters.get('sort_experiment_id') == 'asc':
        query = query.join(Run, Image.run_id == Run.run_id).order_by(asc(Run.experiment_id))
    elif filters.get('sort_experiment_id') == 'desc':
        query = query.join(Run, Image.run_id == Run.run_id).order_by(desc(Run.experiment_id))

    if not filters['sort_id'] and not filters['sort_run_id'] and not filters.get('sort_experiment_id'):
        query = query.order_by(asc(Image.image_id))

    rows = query.join(Run, Image.run_id == Run.run_id).add_columns(Run.experiment_id).all()

    images = []
    for row in rows:
        image_obj = row[0]
        experiment_id = row[1]
        setattr(image_obj, 'experiment_id', experiment_id)
        images.append(image_obj)

    return images

@with_session()
def get_image_by_id(image_id, *, session):
    image = session.query(Image).filter(Image.image_id == image_id).first()
    return image

@with_session(commit=True)
def update_image(image_id, attack_type, *, session):
    image = session.query(Image).filter(Image.image_id == image_id).first()
    if image:
        image.attack_type = attack_type
    return image

@with_session(commit=True)
def delete_image(image_id, *, session):
    image = session.query(Image).filter(Image.image_id == image_id).first()
    if image:
        session.delete(image)

