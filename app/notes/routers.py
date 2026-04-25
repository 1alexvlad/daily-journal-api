from fastapi import APIRouter, HTTPException, status, Body
from typing import List 
from sqlalchemy.exc import SQLAlchemyError


from app.notes.schemas import SNote
from app.notes.services import find_all, add, get_one_or_none, delete_note, update_note_is_done, change_note

router = APIRouter(prefix='/entries')




@router.get('/')
async def get_list_entries() -> List[SNote]:
    notes = await find_all()
    if not notes:
        raise HTTPException(status_code=404, detail="Записи не найден")

    return [SNote.model_validate(note) for note in notes]

@router.post('/')
async def create_entries(title: str, content: str) -> SNote:
    entries = await add(title=title, content=content)
    if not entries:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Не удалось добавить запись')
    return SNote.model_validate(entries)


@router.get('/{id}') 
async def get_by_id_entrie(id: int) -> SNote:
    if id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='id должен быть положительным')
    note = await get_one_or_none(id=id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Не смогли найти id')
    return SNote.model_validate(note)


@router.put('/{id}')
async def change_entrie_by_id(id: int, title: str, content: str) -> SNote:
    try:
        updated_note = await change_note(id=id, title=title, content=content)
        if not updated_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Запись с указанным ID не найдена'
            )
        return SNote.model_validate(updated_note)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при обновлении записи: {str(e)}'
        )


@router.delete('/{id}')
async def delete_entrie_by_id(id: int):
    try:
        note = await delete_note(id=id)
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Не смогли найти id') 
        return {'message': 'Запись удалена'}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ошибка базы данных при удалении'
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Внутренняя ошибка сервера: {str(e)}'
        )


@router.patch('/{id}')
async def change_entrie_by_id(id: int, is_done: bool = Body(..., embed=True)):
    try:
        success = await update_note_is_done(id=id, is_done=is_done)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Запись с указанным ID не найдена'
            )
        return {'message': 'Запись была изменена '}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при обновлении записи: {str(e)}'
        )
