import sqlite3


class Database:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_subs(self, status=True):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscriptions` WHERE `sub_status` = ?", (status,)).fetchall()

    def user_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id):
        """Добавляем нового юзера"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `subscriptions` (`user_id`) VALUES(?)", (user_id,))

    def update_difference(self, user_id, difference):
        """Обновляем статус разницы пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `votes_difference` = ? WHERE `user_id` =?",
                                       (difference, user_id))

    def get_difference(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT votes_difference FROM subscriptions WHERE user_id =?",
                                       (user_id,)).fetchone()[0]

    def update_subscription(self, user_id, status):
        """Обновляем статус разницы пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `sub_status` = ? WHERE `user_id` =?",
                                       (status, user_id))

    def get_subscription(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT sub_status FROM subscriptions WHERE user_id =?", (user_id,)).fetchone()[
                0]

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
