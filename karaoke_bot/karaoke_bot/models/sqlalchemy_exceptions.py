class TelegramProfileNotFoundError(Exception):
    def __init__(self, telegram_id: int):
        message = f"Telegram profile with id={telegram_id} not found."
        super().__init__(message)


class KaraokeNotFoundError(Exception):
    def __init__(self, karaoke_name: str):
        message = f"Karaoke with name '{karaoke_name}' not found."
        super().__init__(message)


class InvalidAccountStateError(Exception):
    def __init__(self, account_id: int, state: str):
        message = f"Account with id={account_id} is in an invalid state: {state}."
        super().__init__(message)


class EmptyFieldError(Exception):
    def __init__(self, table_name: str, field_name: str):
        message = f"{table_name} has an empty field '{field_name}'"
        super().__init__(message)
