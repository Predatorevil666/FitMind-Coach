from typing import Any, Optional, Union, cast

import aiohttp

from bot.config import API_URL
from bot.logger import logger


class APIClient:
    """Клиент для работы с API FitMind Coach."""

    def __init__(self, base_url: str = API_URL):
        """
        Инициализация клиента API.

        Args:
            base_url: Базовый URL API.
        """
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        # Словарь для хранения токенов по Telegram ID
        self.user_tokens: dict[int, str] = {}

    def get_token(self, telegram_id: int) -> Optional[str]:
        """Получить токен для пользователя по Telegram ID."""
        return self.user_tokens.get(telegram_id)

    def set_token(self, telegram_id: int, token: str) -> None:
        """Установить токен для пользователя по Telegram ID."""
        self.user_tokens[telegram_id] = token
        logger.info(f"Токен установлен для пользователя {telegram_id}")

    def clear_token(self, telegram_id: int) -> None:
        """Очистить токен для пользователя по Telegram ID."""
        if telegram_id in self.user_tokens:
            del self.user_tokens[telegram_id]
            logger.info(f"Токен очищен для пользователя {telegram_id}")

    async def start_session(self) -> None:
        """Запуск сессии."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close_session(self) -> None:
        """Закрытие сессии."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def check_user_exists(self, username_or_email: str) -> bool:
        """
        Проверка существования пользователя по email или имени пользователя.

        Args:
            username_or_email: Email или имя пользователя.

        Returns:
            bool: True, если пользователь существует, иначе False.
        """
        await self.start_session()
        if not self.session:
            return True

        try:
            # Проверяем, является ли это email (содержит @ и .)
            is_email = "@" in username_or_email and "." in username_or_email

            # Формируем параметры запроса в зависимости от типа
            # идентификатора
            params = (
                {"email": username_or_email}
                if is_email
                else {"username": username_or_email}
            )

            async with self.session.get(
                f"{self.base_url}/users/check", params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    exists = data.get("exists", False)
                    logger.info(
                        f"Проверка существования пользователя "
                        f"{username_or_email}: {exists}"
                    )
                    return exists
                else:
                    # Если API не поддерживает такой метод, считаем что
                    # проверка не удалась
                    logger.warning(
                        f"API не поддерживает проверку существования "
                        f"пользователя: {response.status}"
                    )
                    # По умолчанию считаем, что пользователь существует
                    return True
        except Exception as e:
            logger.error(
                f"Ошибка при проверке существования пользователя: {e}"
            )
            # По умолчанию считаем, что пользователь существует
            return True

    async def login(self, email: str, password: str, telegram_id: int) -> bool:
        """
        Авторизация пользователя.

        Args:
            email: Email пользователя.
            password: Пароль пользователя.
            telegram_id: Telegram ID пользователя.

        Returns:
            bool: True, если авторизация успешна, иначе False.
        """
        await self.start_session()
        try:
            form_data = aiohttp.FormData()
            form_data.add_field("username", email)
            form_data.add_field("password", password)

            async with self.session.post(
                f"{self.base_url}/auth/login", data=form_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get("access_token")
                    if token:
                        self.set_token(telegram_id, token)
                    logger.info(f"Успешная авторизация пользователя {email}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Ошибка авторизации пользователя {email}: "
                        f"{response.status}, {error_text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Ошибка при авторизации: {e}")
            return False

    async def logout(self, telegram_id: int) -> bool:
        """
        Выход пользователя из системы.

        Args:
            telegram_id: Telegram ID пользователя.

        Returns:
            bool: True, если выход успешен, иначе False.
        """
        # Просто очищаем токен для пользователя
        if self.get_token(telegram_id):
            self.clear_token(telegram_id)
            logger.info(f"Пользователь {telegram_id} вышел из системы")
            return True
        else:
            logger.warning(f"Попытка выхода без авторизации для {telegram_id}")
            return False

    async def register(
        self, email: str, username: str, password: str, telegram_id: int = None
    ) -> bool:
        """
        Регистрация пользователя.

        Args:
            email: Email пользователя.
            username: Имя пользователя.
            password: Пароль пользователя.
            telegram_id: Telegram ID пользователя (опционально).

        Returns:
            bool: True, если регистрация успешна, иначе False.
        """
        await self.start_session()
        try:
            user_data = {
                "email": email,
                "username": username,
                "password": password,
                "is_active": True,
                "is_superuser": False,
            }

            # Добавляем telegram_id если он передан
            if telegram_id is not None:
                user_data["telegram_id"] = telegram_id

            async with self.session.post(
                f"{self.base_url}/users", json=user_data
            ) as response:
                if response.status == 200:
                    logger.info(f"Успешная регистрация пользователя {email}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Ошибка регистрации пользователя {email}: "
                        f"{response.status}, {error_text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Ошибка при регистрации: {e}")
            return False

    async def register_from_telegram(
        self,
        telegram_id: int,
        username: str,
        first_name: str = None,
        last_name: str = None,
    ) -> bool:
        """
        Регистрация пользователя из Telegram данных.

        Args:
            telegram_id: Telegram ID пользователя.
            username: Имя пользователя.
            first_name: Имя пользователя в Telegram.
            last_name: Фамилия пользователя в Telegram.

        Returns:
            bool: True, если регистрация успешна, иначе False.
        """
        await self.start_session()
        try:
            user_data = {
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
                "is_superuser": False,
            }

            async with self.session.post(
                f"{self.base_url}/users", json=user_data
            ) as response:
                if response.status == 200:
                    logger.info(
                        f"Успешная регистрация пользователя {username} "
                        f"с Telegram ID {telegram_id}"
                    )
                    return True
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Ошибка регистрации пользователя {username}: "
                        f"{response.status}, {error_text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Ошибка при регистрации: {e}")
            return False

    async def telegram_auth(self, telegram_id: int) -> bool:
        """
        Авторизация пользователя по Telegram ID.

        Args:
            telegram_id: Telegram ID пользователя.

        Returns:
            bool: True, если авторизация успешна, иначе False.
        """
        await self.start_session()
        try:
            auth_data = {"telegram_id": telegram_id}

            async with self.session.post(
                f"{self.base_url}/auth/telegram-auth", json=auth_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get("access_token")
                    if token:
                        self.set_token(telegram_id, token)
                        logger.info(
                            f"Успешная авторизация пользователя по "
                            f"Telegram ID {telegram_id}"
                        )
                        return True
                    else:
                        logger.error(
                            f"Ответ 200 без access_token при авторизации по "
                            f"Telegram ID {telegram_id}"
                        )
                        return False
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Ошибка авторизации по Telegram ID {telegram_id}: "
                        f"{response.status}, {error_text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Ошибка при авторизации по Telegram: {e}")
            return False

    async def link_telegram(
        self, email: str, password: str, telegram_id: int
    ) -> bool:
        """
        Привязка Telegram ID к существующему аккаунту.

        Args:
            email: Email пользователя.
            password: Пароль пользователя.
            telegram_id: Telegram ID для привязки.

        Returns:
            bool: True, если привязка успешна, иначе False.
        """
        await self.start_session()
        try:
            link_data = {
                "email": email,
                "password": password,
                "telegram_id": telegram_id,
            }

            async with self.session.post(
                f"{self.base_url}/auth/telegram-link", json=link_data
            ) as response:
                if response.status == 200:
                    logger.info(
                        f"Успешная привязка Telegram ID {telegram_id} "
                        f"к аккаунту {email}"
                    )
                    return True
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Ошибка привязки Telegram ID {telegram_id} "
                        f"к аккаунту {email}: {response.status}, {error_text}"
                    )
                    return False
        except Exception as e:
            logger.error(f"Ошибка при привязке Telegram: {e}")
            return False

    async def _request(
        self,
        method: str,
        endpoint: str,
        telegram_id: int,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[dict[str, Any]], None]:
        """
        Выполнение запроса к API.

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE).
            endpoint: Эндпоинт API.
            telegram_id: Telegram ID пользователя.
            data: Данные для отправки в теле запроса.
            params: Параметры запроса.

        Returns:
            Union[dict[str, Any], list[dict[str, Any]], None]: Ответ от API.
        """
        token = self.get_token(telegram_id)
        if not token:
            # Автоматически пытаемся авторизоваться
            auth_success = await self.telegram_auth(telegram_id)
            if not auth_success:
            logger.error(
                    f"Не удалось авторизоваться для пользователя {telegram_id}"
            )
            return None
            token = self.get_token(telegram_id)

        await self.start_session()
        headers = {"Authorization": f"Bearer {token}"}

        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"

            if method == "GET":
                async with self.session.get(
                    url, headers=headers, params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Ошибка запроса {method} {endpoint}: "
                            f"{response.status}, {error_text}"
                        )
                        return None
            elif method == "POST":
                async with self.session.post(
                    url, headers=headers, json=data, params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Ошибка запроса {method} {endpoint}: "
                            f"{response.status}, {error_text}"
                        )
                        return None
            elif method == "PUT":
                async with self.session.put(
                    url, headers=headers, json=data, params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Ошибка запроса {method} {endpoint}: "
                            f"{response.status}, {error_text}"
                        )
                        return None
            elif method == "DELETE":
                async with self.session.delete(
                    url, headers=headers, params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Ошибка запроса {method} {endpoint}: "
                            f"{response.status}, {error_text}"
                        )
                        return None
            else:
                logger.error(f"Неподдерживаемый метод: {method}")
                return None
        except Exception as e:
            logger.error(
                f"Ошибка при выполнении запроса {method} {endpoint}: {e}"
            )
            return None

    # Методы для работы с профилем
    async def get_profile(self, telegram_id: int) -> Optional[dict[str, Any]]:
        """Получение профиля пользователя."""
        result = await self._request("GET", "/users/me/profile", telegram_id)
        return cast(Optional[dict[str, Any]], result)

    async def create_profile(
        self, telegram_id: int, profile_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """
        Создание профиля пользователя.

        Args:
            telegram_id: Telegram ID пользователя.
            profile_data: Данные профиля.

        Returns:
            Optional[dict[str, Any]]: Созданный профиль или None в случае
                ошибки.
        """
        result = await self._request(
            "POST", "/users/me/profile", telegram_id, data=profile_data
        )
        return cast(Optional[dict[str, Any]], result)

    async def update_profile(
        self, telegram_id: int, profile_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """
        Обновление профиля пользователя.

        Args:
            telegram_id: Telegram ID пользователя.
            profile_data: Данные профиля для обновления.

        Returns:
            Optional[dict[str, Any]]: Обновленный профиль или None в случае
                ошибки.
        """
        result = await self._request(
            "PUT", "/users/me/profile", telegram_id, data=profile_data
        )
        return cast(Optional[dict[str, Any]], result)

    # Методы для работы с тренировками
    async def get_workouts(
        self, telegram_id: int, skip: int = 0, limit: int = 10
    ) -> Optional[list[dict[str, Any]]]:
        """Получение списка тренировок."""
        result = await self._request(
            "GET",
            "/workouts",
            telegram_id,
            params={"skip": skip, "limit": limit},
        )
        return cast(Optional[list[dict[str, Any]]], result)

    async def create_workout(
        self, telegram_id: int, workout_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Создание новой тренировки."""
        result = await self._request(
            "POST", "/workouts", telegram_id, data=workout_data
        )
        return cast(Optional[dict[str, Any]], result)

    async def get_workout(
        self, workout_id: int, telegram_id: int
    ) -> Optional[dict[str, Any]]:
        """Получение информации о тренировке."""
        result = await self._request(
            "GET", f"/workouts/{workout_id}", telegram_id
        )
        return cast(Optional[dict[str, Any]], result)

    async def update_workout(
        self,
        workout_id: int,
        workout_data: dict[str, Any],
        telegram_id: int,
    ) -> Optional[dict[str, Any]]:
        """Обновление тренировки."""
        result = await self._request(
            "PUT", f"/workouts/{workout_id}", telegram_id, data=workout_data
        )
        return cast(Optional[dict[str, Any]], result)

    async def delete_workout(
        self, workout_id: int, telegram_id: int
    ) -> Optional[dict[str, Any]]:
        """Удаление тренировки."""
        result = await self._request(
            "DELETE", f"/workouts/{workout_id}", telegram_id
        )
        return cast(Optional[dict[str, Any]], result)

    # Методы для работы с питанием
    async def get_meals(
        self, telegram_id: int, skip: int = 0, limit: int = 10
    ) -> Optional[list[dict[str, Any]]]:
        """Получение списка приемов пищи."""
        result = await self._request(
            "GET", "/meals", telegram_id, params={"skip": skip, "limit": limit}
        )
        return cast(Optional[list[dict[str, Any]]], result)

    async def create_meal(
        self, telegram_id: int, meal_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Создание нового приема пищи."""
        result = await self._request(
            "POST", "/meals", telegram_id, data=meal_data
        )
        return cast(Optional[dict[str, Any]], result)

    async def get_meal(
        self, meal_id: int, telegram_id: int
    ) -> Optional[dict[str, Any]]:
        """Получение информации о приеме пищи."""
        result = await self._request("GET", f"/meals/{meal_id}", telegram_id)
        return cast(Optional[dict[str, Any]], result)

    async def update_meal(
        self,
        meal_id: int,
        meal_data: dict[str, Any],
        telegram_id: int,
    ) -> Optional[dict[str, Any]]:
        """Обновление приема пищи."""
        result = await self._request(
            "PUT", f"/meals/{meal_id}", telegram_id, data=meal_data
        )
        return cast(Optional[dict[str, Any]], result)

    async def delete_meal(
        self, meal_id: int, telegram_id: int
    ) -> Optional[dict[str, Any]]:
        """Удаление приема пищи."""
        result = await self._request(
            "DELETE", f"/meals/{meal_id}", telegram_id
        )
        return cast(Optional[dict[str, Any]], result)

    # Методы для работы с лабораторными анализами
    async def get_lab_results(
        self, telegram_id: int, skip: int = 0, limit: int = 10
    ) -> Optional[list[dict[str, Any]]]:
        """Получение списка результатов анализов."""
        result = await self._request(
            "GET", "/lab", telegram_id, params={"skip": skip, "limit": limit}
        )
        return cast(Optional[list[dict[str, Any]]], result)

    async def create_lab_result(
        self, telegram_id: int, lab_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Создание нового результата анализа."""
        result = await self._request(
            "POST", "/lab", telegram_id, data=lab_data
        )
        return cast(Optional[dict[str, Any]], result)

    async def get_lab_result(
        self, lab_id: int, telegram_id: int
    ) -> Optional[dict[str, Any]]:
        """Получение информации о результате анализа."""
        result = await self._request("GET", f"/lab/{lab_id}", telegram_id)
        return cast(Optional[dict[str, Any]], result)

    async def update_lab_result(
        self,
        lab_id: int,
        lab_data: dict[str, Any],
        telegram_id: int,
    ) -> Optional[dict[str, Any]]:
        """Обновление результата анализа."""
        result = await self._request(
            "PUT", f"/lab/{lab_id}", telegram_id, data=lab_data
        )
        return cast(Optional[dict[str, Any]], result)

    async def delete_lab_result(
        self, lab_id: int, telegram_id: int
    ) -> Optional[dict[str, Any]]:
        """Удаление результата анализа."""
        result = await self._request("DELETE", f"/lab/{lab_id}", telegram_id)
        return cast(Optional[dict[str, Any]], result)


# Создаем глобальный экземпляр клиента API
_api_client = APIClient()


def reinit_api_client():
    """Пересоздает глобальный API клиент с актуальными настройками."""
    global _api_client
    import os

    from dotenv import load_dotenv

    # Перезагружаем переменные окружения
    load_dotenv()

    # Получаем актуальное значение API_URL
    api_url = os.getenv("API_URL", "http://localhost:8003/api/v1")

    logger.info(f"Переинициализация API клиента с URL: {api_url}")
    _api_client = APIClient(api_url)


# Создаем класс-обертку для совместимости
class UserAPIClient:
    """Обертка для API клиента с привязкой к пользователю."""

    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id

    @property
    def client(self):
        """Получить актуальный глобальный API клиент."""
        return _api_client

    async def login(self, email: str, password: str) -> bool:
        return await self.client.login(email, password, self.telegram_id)

    async def logout(self) -> bool:
        return await self.client.logout(self.telegram_id)

    async def telegram_auth(self, telegram_id: int = None) -> bool:
        # Если telegram_id не передан, используем telegram_id из конструктора
        if telegram_id is None:
            telegram_id = self.telegram_id
        return await self.client.telegram_auth(telegram_id)

    async def get_profile(self) -> Optional[dict[str, Any]]:
        return await self.client.get_profile(self.telegram_id)

    async def create_profile(
        self, profile_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        return await self.client.create_profile(self.telegram_id, profile_data)

    async def update_profile(
        self, profile_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        return await self.client.update_profile(self.telegram_id, profile_data)

    async def get_workouts(
        self, skip: int = 0, limit: int = 10
    ) -> Optional[list[dict[str, Any]]]:
        return await self.client.get_workouts(self.telegram_id, skip, limit)

    async def create_workout(
        self, workout_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        return await self.client.create_workout(self.telegram_id, workout_data)

    async def get_meals(
        self, skip: int = 0, limit: int = 10
    ) -> Optional[list[dict[str, Any]]]:
        return await self.client.get_meals(self.telegram_id, skip, limit)

    async def create_meal(
        self, meal_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        return await self.client.create_meal(self.telegram_id, meal_data)

    async def get_lab_results(
        self, skip: int = 0, limit: int = 10
    ) -> Optional[list[dict[str, Any]]]:
        return await self.client.get_lab_results(self.telegram_id, skip, limit)

    async def create_lab_result(
        self, lab_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        return await self.client.create_lab_result(self.telegram_id, lab_data)


# Глобальная переменная для backward compatibility
api_client = _api_client
