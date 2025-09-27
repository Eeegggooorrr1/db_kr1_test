from datetime import datetime, UTC, date
from functools import wraps
from typing import Optional, Any, List

from pydantic import ValidationError
from sqlalchemy import select, desc, text, asc
import db.database
from db.models import Experiment, Run, Image, AttackTypeEnum
from db.schemas import ExperimentCreate, RunCreate, ImageCreate, ImageEdit, RunEdit
from sqlalchemy.exc import IntegrityError

from test_data import experiments_data, runs_data, images_data


def with_session(commit = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with db.database.SessionLocal() as session:
                kwargs['session'] = session
                result = func(*args, **kwargs)
                if commit:
                    session.commit()
                return result
        return wrapper
    return decorator

@with_session(commit=True)
def create_experiment(name, description = None, *, session):
    ExperimentCreate(name=name, description=description, created_date=datetime.now().date())
    exp = Experiment(name=name, description=description, created_date=datetime.now().date())
    session.add(exp)

@with_session(commit=True)
def create_run(experiment_id, accuracy = None, flagged = None, *, session):
    RunCreate(experiment_id=experiment_id, run_date=datetime.now(UTC), accuracy=accuracy, flagged=flagged)
    if session.get(Experiment, experiment_id) is None :
        raise ValueError(f"Experiment с id={experiment_id} не найден")

    run = Run(experiment_id=experiment_id, run_date=datetime.now(UTC), accuracy=accuracy, flagged=flagged)
    session.add(run)

@with_session(commit=True)
def create_image(run_id, file_path, attack_type, original_name = None, added_date = None, coordinates = None, *, session):
    ImageCreate(run_id=run_id, file_path=file_path, original_name=original_name, attack_type=attack_type,
                added_date=added_date, coordinates=coordinates)
    if session.get(Run, run_id) is None:
        raise ValueError(f"Run с id={run_id} не найден")
    img = Image(run_id=run_id, file_path=file_path, original_name=original_name, attack_type=attack_type, added_date=added_date, coordinates=coordinates)
    session.add(img)

@with_session()
def get_experiment_max_id(*, session):
    result = session.execute(text("SELECT COALESCE(MAX(experiment_id), 0) FROM experiments"))
    return result.scalar()

@with_session()
def get_run_max_id(*, session):
    result = session.execute(text("SELECT COALESCE(MAX(run_id), 0) FROM runs"))
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
def update_run(experiment_id, run_id, accuracy, flagged, *, session):
    try:
        update_data = RunEdit(experiment_id = experiment_id, accuracy=accuracy, flagged=flagged)
    except ValidationError as e:
        raise ValueError(f"некорректные изменения: {e}") from e
    run = session.query(Run).filter(Run.run_id == run_id).first()
    if run:
        run.accuracy = accuracy
        run.flagged = flagged
        run.experiment_id = experiment_id

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
    if filters['file_type']:
        query = query.filter(Image.file_path.endswith(filters['file_type']))
    if filters['sort_id'] == 'asc':
        query = query.order_by(asc(Image.image_id))
    elif filters['sort_id'] == 'desc':
        query = query.order_by(desc(Image.image_id))
    if not filters['sort_id']:
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
def update_image(image_id, run_id, attack_type, *, session):
    try:
        update_data = ImageEdit(run_id=run_id, attack_type=attack_type)
    except ValidationError as e:
        raise ValueError(f"некорректные изменения: {e}") from e
    image = session.query(Image).filter(Image.image_id == image_id).first()
    if image:
        image.attack_type = attack_type
        image.run_id = run_id

@with_session(commit=True)
def delete_image(image_id, *, session):
    image = session.query(Image).filter(Image.image_id == image_id).first()
    if image:
        session.delete(image)


def insert_test_data():
    for exp in experiments_data:
        create_experiment(**exp)
    for rn in runs_data:
        create_run(**rn)
    for img in images_data:
        create_image(**img)


