from fastapi import APIRouter, HTTPException, status, Body, Depends
from typing import List 


from app.notes.schemas import SNote
from app.notes.services import NoteServices, find_all, delete_note, update_note_is_done, change_note
from app.users.models import User
from app.notes.models import Note
from app.users.dependencies import get_current_user, get_task_or_403


router = APIRouter(prefix='/entries', tags=['notes'])



@router.get('/')
async def get_list_entries(current_user: User = Depends(get_current_user)) -> List[SNote]:
    try:
        notes = await find_all(current_user)
        if not notes:
            return []  

        return [SNote.model_validate(note) for note in notes]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось получить записи: {str(e)}"
        )

@router.post('/')
async def create_entries(title: str, content: str, current_user: User = Depends(get_current_user)) -> SNote:
    entries = await NoteServices.add(title=title, content=content, user_id = current_user.id)
    if not entries:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Не удалось добавить запись')
    return SNote.model_validate(entries)


@router.get('/{id}') 
async def get_by_id_entrie(task: Note = Depends(get_task_or_403)) -> SNote:
    try:
        return SNote.model_validate(task)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось получить записи: {str(e)}"
        )


@router.put('/{id}')
async def change_entrie_by_id(
    id: int,
    title: str | None = None,
    content: str | None = None,
    is_done: bool | None = None,
    current_user: User = Depends(get_current_user)
) -> SNote:
    try:
        updated_note = await change_note(id, current_user, title, content, is_done)
        if not updated_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Запись с указанным ID не найдена или нет прав на редактирование'
            )
        return SNote.model_validate(updated_note)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при обновлении записи: {str(e)}'
        )

@router.delete('/{id}')
async def delete_entrie_by_id(id: int, current_user: User = Depends(get_current_user)):
    try:
        note = await delete_note(id, current_user)
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Запись с указанным ID не найдена или нет прав на удаление') 
        return {'message': 'Запись удалена'}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Внутренняя ошибка сервера: {str(e)}'
        )


@router.patch('/{id}')
async def change_entrie_by_id(id: int, is_done: bool = Body(..., embed=True), current_user: User = Depends(get_current_user)) -> SNote:
    try:
        updated_note  = await update_note_is_done(id, is_done, current_user)
        if not updated_note :
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Запись с указанным ID не найдена или нет прав на редактирование'
            )
        return SNote.model_validate(updated_note)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при обновлении записи: {str(e)}'
        )
