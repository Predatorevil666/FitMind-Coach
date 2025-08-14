#!/usr/bin/env python
"""
Скрипт для создания суперпользователя.
Запуск: python -m api.create_superuser
"""

import asyncio
import sys

from getpass import getpass

from api.crud.user import user
from api.db.database import SessionLocal
from api.schemas.user import UserIn


async def create_superuser():
    """Создает суперпользователя с правами администратора."""
    print("Создание суперпользователя")

    # Проверяем аргументы командной строки
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Тестовый режим с фиксированными данными
        email = "admin@example.com"
        username = "admin"
        password = "adminpassword"
        print(
            f"Создание тестового суперпользователя с email: {email} "
            f"и паролем: {password}"
        )
    else:
        # Запрос данных пользователя
        email = input("Email: ")
        username = input("Имя пользователя: ")

        # Запрос пароля (не отображается при вводе)
        while True:
            password = getpass("Пароль: ")
            password_confirm = getpass("Подтвердите пароль: ")

            if password == password_confirm:
                break
            print("Пароли не совпадают. Попробуйте еще раз.")

    # Создание объекта пользователя
    user_data = UserIn(
        email=email,
        username=username,
        password=password,
        is_active=True,
        is_superuser=True,
    )

    # Получение сессии базы данных
    async with SessionLocal() as session:
        try:
            # Проверка существования пользователя с таким email
            existing_user = await user.get_by_email(session, email=email)
            if existing_user:
                print(f"Пользователь с email {email} уже существует.")
                return

            # Проверка существования пользователя с таким username
            existing_user = await user.get_by_username(
                session, username=username
            )
            if existing_user:
                print(f"Пользователь с именем {username} уже существует.")
                return

            # Создание суперпользователя
            new_user = await user.create(session, obj_in=user_data)
            print(f"Суперпользователь {new_user.username} успешно создан!")
            print("\nДля авторизации используйте:")
            print(f"Email: {email}")
            print("Пароль: [введенный вами пароль]")
            print("\nПри авторизации через API в поле username укажите email.")
        except Exception as e:
            print(f"Ошибка при создании суперпользователя: {e}")
            return


if __name__ == "__main__":
    asyncio.run(create_superuser())
