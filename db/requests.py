from datetime import date, datetime, UTC
from typing import Optional, Any, List

from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import Experiment, Run, Image, AttackTypeEnum
from db.schemas import ExperimentCreate, RunCreate, ImageCreate
from sqlalchemy.exc import IntegrityError

def create_experiment(
    name: str,
    description: Optional[str] = None,
) -> Experiment:

    ExperimentCreate(name=name, description=description, created_date=datetime.now().date())
    with SessionLocal() as session:
        exp = Experiment(name=name, description=description, created_date=datetime.now().date())
        session.add(exp)
        try:
            session.commit()
            session.refresh(exp)
            return exp
        except IntegrityError:
            session.rollback()
            raise


def create_run(
    experiment_id: int,
    accuracy: Optional[float] = None,
    flagged: Optional[bool] = None,
) -> Run:
    with SessionLocal() as session:
        if session.get(Experiment, experiment_id) is None:
            raise ValueError(f"Experiment с id={experiment_id} не найден")

        RunCreate(experiment_id=experiment_id, run_date=datetime.now(UTC), accuracy=accuracy, flagged=flagged)

        run = Run(experiment_id=experiment_id, run_date=datetime.now(UTC), accuracy=accuracy, flagged=flagged)
        session.add(run)
        try:
            session.commit()
            session.refresh(run)
            return run
        except IntegrityError:
            session.rollback()
            raise


def create_image(
    session: Session,
    *,
    run_id: int,
    file_path: str,
    attack_type: Any,
    original_name: Optional[str] = None,
    added_date: Optional[datetime] = None,
    coordinates: Optional[List[int]] = None,
) -> Image:

    if session.get(Run, run_id) is None:
        raise ValueError(f"Run с id={run_id} не найден")
    if ImageCreate is not None:
        ImageCreate(run_id=run_id, file_path=file_path, original_name=original_name,
                    attack_type=attack_type, added_date=added_date, coordinates=coordinates)

    img = Image(
        run_id=run_id,
        file_path=file_path,
        original_name=original_name,
        attack_type=attack_type,
        added_date=added_date,
        coordinates=coordinates,
    )
    session.add(img)
    try:
        session.commit()
        session.refresh(img)
        return img
    except IntegrityError:
        session.rollback()
        raise
def get_experiment_max_id():
    with SessionLocal() as session:
        return session.scalars(select(Experiment).order_by(desc(Experiment.experiment_id)).limit(1)).first().experiment_id
def get_run_max_id():
    with SessionLocal() as session:
        return session.scalars(select(Run).order_by(desc(Run.run_id)).limit(1)).first().run_id
# with SessionLocal() as session:
#     try:
#         # exp = create_experiment(session, name="exp_linked_1", description="пример последовательного добавления")
#         # print("Created experiment id:", exp.experiment_id)
#
#         # run = create_run(session, experiment_id=1, run_date=datetime.utcnow(), accuracy=0.95, flagged=False)
#         # print("Created run id:", run.run_id)
#         #
#         # attack_value = AttackTypeEnum.SOME_ATTACK if 'AttackTypeEnum' in globals() and hasattr(AttackTypeEnum, 'SOME_ATTACK') else "some_attack"
#         #
#         img = create_image(
#             session,
#             run_id=1,
#             file_path="/data/images/img_002.png",
#             attack_type=AttackTypeEnum.no_attack,
#             original_name="img_002.png",
#             added_date=datetime.now(UTC),
#             coordinates=[1, 2, 3, 4],
#         )
#         # print("Created image id:", img.image_id)
#     except Exception as e:
#         print("Ошибка при создании связанных сущностей:", type(e), e)
#
