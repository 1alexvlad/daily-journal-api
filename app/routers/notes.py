from fastapi import APIRouter, Body, Depends

from app.core.exceptions import *
from app.models.users import User
from app.schemas.note import SNote
from app.services.notes import NoteServices
from app.core.dependencies import get_current_user

note_router = APIRouter(prefix="/entries", tags=["notes"])


@note_router.get("/")
async def get_list_entries(current_user: User = Depends(get_current_user)) -> list[SNote]:
    notes = await NoteServices.find_all(user_id=current_user.id)
    return [SNote.model_validate(note) for note in notes]


@note_router.post("/")
async def create_entries(title: str, content: str, current_user: User = Depends(get_current_user)) -> SNote:
    entries = await NoteServices.add(title=title, content=content, user_id=current_user.id)
    if not entries:
        raise AddNotedException
    return SNote.model_validate(entries)


@note_router.put("/{id}")
async def change_entrie_by_id(
    id: int,
    title: str | None = None,
    content: str | None = None,
    is_done: bool | None = None,
    current_user: User = Depends(get_current_user),
) -> SNote:
    updated_note = await NoteServices.change_note(id, current_user, title, content, is_done)
    if not updated_note:
        raise NotesNotFoundOrEditingRightsException
    return SNote.model_validate(updated_note)


@note_router.delete("/{id}")
async def delete_entrie_by_id(id: int, current_user: User = Depends(get_current_user)):
    note = await NoteServices.delete_note(id, current_user)
    if not note:
        raise NotesNotFoundOrEditingRightsException
    return {"message": "Запись удалена"}


@note_router.patch("/{id}")
async def update_note_by_id(
    id: int, is_done: bool = Body(..., embed=True), current_user: User = Depends(get_current_user)
) -> SNote:
    updated_note = await NoteServices.update_note_is_done(id, is_done, current_user)
    if not updated_note:
        raise NotesNotFoundOrEditingRightsException

    return SNote.model_validate(updated_note)
