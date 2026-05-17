from fastapi import HTTPException, status



class DailyPlannerException(HTTPException):
    status_code = 500 
    detail = ''

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

class UserAlreadyExistsException(DailyPlannerException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Пользователь уже существует'

class EmailAlreadyExistsException(DailyPlannerException):
    status_code = status.HTTP_409_CONFLICT
    detail = 'email уже существует'

class UserNotFoundException(DailyPlannerException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'Пользователь не найден'


class IncorrectEmailOrPasswordException(DailyPlannerException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Неверная почта или пароль'

class AccountIsBlockedException(DailyPlannerException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Неверная почта или пароль'

class AddNotedException(DailyPlannerException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = 'Не удалось добавить запись'

class ShowNotesException(DailyPlannerException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = 'Не удалось добавить запись'

class NotesNotFoundOrEditingRightsException(DailyPlannerException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = 'Запись не найдена или нет прав на редактирование'

class InternalServerException(DailyPlannerException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = 'Внутренняя ошибка сервера'

class UpdateNoteException(DailyPlannerException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = 'Ошибка при обновлении записи'

class AccountNotAuthorizedException(DailyPlannerException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Аккаунт не авторизован'

class InvalidOrExpiredSessionException(DailyPlannerException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Невалидный или просроченный сеанс'

class SessionExpiredException(DailyPlannerException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Сессия истекла'

class AccountDeletedException(DailyPlannerException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Учётная запись удалена'

class StaffOrAdminException(DailyPlannerException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Доступ запрещён. Требуется роль STAFF или ADMIN'

class NoDataUpdateException(DailyPlannerException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Нет данных для обновления'

class NoDataException(DailyPlannerException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'Данные не найдены'

class StaffNoChangeAdminException(DailyPlannerException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'STAFF не может изменять данные ADMIN'

class StaffNoChangeStaffException(DailyPlannerException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'STAFF не может изменять других STAFF'
