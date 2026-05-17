from fastapi import APIRouter, Body, Depends
from typing import List 


from app.notes.schemas import SNote
from app.notes.services import NoteServices, delete_note, update_note_is_done, change_note
from app.notes.services import NoteServices
from app.users.models import User
from app.users.dependencies import get_current_user
from app.exceptions import (
    AddNotedException, ShowNotesException, 
    NotesNotFoundOrEditingRightsException, 
    InternalServerException, UpdateNoteException)


router = APIRouter(prefix='/entries', tags=['notes'])



@router.get('/')
async def get_list_entries(current_user: User = Depends(get_current_user)) -> List[SNote]:
    try:
        notes = await NoteServices.find_all(current_user)
        if not notes:
            return []  

        return [SNote.model_validate(note) for note in notes]
    except Exception as e:
        raise ShowNotesException

@router.post('/')
async def create_entries(title: str, content: str, current_user: User = Depends(get_current_user)) -> SNote:
    entries = await NoteServices.add(title=title, content=content, user_id = current_user.id)
    if not entries:
        raise AddNotedException
    return SNote.model_validate(entries)


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
            raise NotesNotFoundOrEditingRightsException
        return SNote.model_validate(updated_note)
    except Exception as e:
        raise UpdateNoteException

@router.delete('/{id}')
async def delete_entrie_by_id(id: int, current_user: User = Depends(get_current_user)):
    try:
        note = await delete_note(id, current_user)
        if not note:
            raise NotesNotFoundOrEditingRightsException
        return {'message': 'Запись удалена'}

    except Exception as e:
        raise InternalServerException


@router.patch('/{id}')
async def change_entrie_by_id(id: int, is_done: bool = Body(..., embed=True), current_user: User = Depends(get_current_user)) -> SNote:
    try:
        updated_note  = await update_note_is_done(id, is_done, current_user)
        if not updated_note :
            raise NotesNotFoundOrEditingRightsException
        return SNote.model_validate(updated_note)

    except Exception as e:
        raise UpdateNoteException
