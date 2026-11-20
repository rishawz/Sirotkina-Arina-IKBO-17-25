"""Исключения приложения."""


class AppError(Exception):
    """Базовая ошибка приложения."""


class ConfigError(AppError):
    """Некорректное значение параметра."""


class SourceError(AppError):
    """Ошибка получения данных о зависимостях."""
