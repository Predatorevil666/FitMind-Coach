# # from typing import List - unused

from fastapi import APIRouter, HTTPException, status

from api.core.deps import CurrentUser, SessionDep
from api.crud import lab_result
from api.schemas.lab import LabResultIn, LabResultOut

router = APIRouter(tags=["lab_results"])


@router.post("", response_model=LabResultOut)
async def create_lab_result(
    db: SessionDep, lab_result_in: LabResultIn, current_user: CurrentUser
) -> LabResultOut:
    """
    Создание новой записи о результатах анализов для текущего пользователя.
    """
    return await lab_result.create_with_user(
        db, obj_in=lab_result_in, user_id=current_user.id
    )


@router.get("", response_model=list[LabResultOut])
async def read_lab_results(
    db: SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = None,
) -> list[LabResultOut]:
    """
    Получение списка результатов анализов текущего пользователя.
    """
    return await lab_result.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/{lab_result_id}", response_model=LabResultOut)
async def read_lab_result(
    lab_result_id: int, db: SessionDep, current_user: CurrentUser
) -> LabResultOut:
    """
    Получение информации о результатах анализов по ID.
    """
    db_lab_result = await lab_result.get(db, id=lab_result_id)
    if not db_lab_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Результаты анализов не найдены",
        )

    # Проверяем, принадлежат ли результаты анализов текущему пользователю
    if db_lab_result.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    return db_lab_result


@router.put("/{lab_result_id}", response_model=LabResultOut)
async def update_lab_result(
    lab_result_id: int,
    db: SessionDep,
    lab_result_in: LabResultIn,
    current_user: CurrentUser,
) -> LabResultOut:
    """
    Обновление результатов анализов по ID.
    """
    db_lab_result = await lab_result.get(db, id=lab_result_id)
    if not db_lab_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Результаты анализов не найдены",
        )

    # Проверяем, принадлежат ли результаты анализов текущему пользователю
    if db_lab_result.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    return await lab_result.update(
        db, db_obj=db_lab_result, obj_in=lab_result_in
    )


@router.delete("/{lab_result_id}", response_model=LabResultOut)
async def delete_lab_result(
    lab_result_id: int, db: SessionDep, current_user: CurrentUser
) -> LabResultOut:
    """
    Удаление результатов анализов по ID.
    """
    db_lab_result = await lab_result.get(db, id=lab_result_id)
    if not db_lab_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Результаты анализов не найдены",
        )

    # Проверяем, принадлежат ли результаты анализов текущему пользователю
    if db_lab_result.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    return await lab_result.remove(db, id=lab_result_id)
