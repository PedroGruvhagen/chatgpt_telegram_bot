from typing import Optional, Any
import uuid
import pymssql
from datetime import datetime

class Database:
    def __init__(self):
        mssql_connection_string = {
            "host": "PEDROSPC",
            "user": "pedrogpt",
            "password": "@Karoline9106040182",
            "database": "master"
        }
        self.conn = pymssql.connect(**mssql_connection_string)

    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM [user] WHERE id = %s", (user_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                return True
            else:
                if raise_exception:
                    raise ValueError(f"User {user_id} does not exist")
                else:
                    return False

    def add_new_user(self, user_id: int, chat_id: int, username: str = "", first_name: str = "", last_name: str = ""):
        user = {
            "id": user_id,
            "chat_id": chat_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "last_interaction": datetime.now(),
            "first_seen": datetime.now(),
            "current_dialog_id": None,
            "current_chat_mode": "assistant",
            "current_model": "default_model",
            "n_used_tokens": {},
            "n_generated_images": 0,
            "n_transcribed_seconds": 0.0
        }

        if not self.check_if_user_exists(user_id):
            with self.conn.cursor() as cursor:
                cursor.execute("""
                INSERT INTO [user] (id, chat_id, username, first_name, last_name,
                                  last_interaction, first_seen, current_dialog_id,
                                  current_chat_mode, current_model, n_used_tokens,
                                  n_generated_images, n_transcribed_seconds)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user["id"], user["chat_id"], user["username"], user["first_name"], user["last_name"],
                      user["last_interaction"], user["first_seen"], user["current_dialog_id"], user["current_chat_mode"], user["current_model"], str(user["n_used_tokens"]),
                      user["n_generated_images"], user["n_transcribed_seconds"]))
                self.conn.commit()

    def start_new_dialog(self, user_id: int):
        self.check_if_user_exists(user_id, raise_exception=True)

        dialog_id = str(uuid.uuid4())
        dialog = {
            "id": dialog_id,
            "user_id": user_id,
            "chat_mode": self.get_user_attribute(user_id, "current_chat_mode"),
            "start_time": datetime.now(),
            "model": self.get_user_attribute(user_id, "current_model"),
            "messages": []
        }

        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO dialog (id, user_id, chat_mode, start_time, model, messages)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (dialog["id"], dialog["user_id"], dialog["chat_mode"], dialog["start_time"], dialog["model"], str(dialog["messages"])))
            self.conn.commit()

        self.set_user_attribute(user_id, "current_dialog_id", dialog_id)

        return dialog_id

    def get_user_attribute(self, user_id: int, key: str):
        self.check_if_user_exists(user_id, raise_exception=True)

        with self.conn.cursor() as cursor:
            cursor.execute("SELECT {} FROM [user] WHERE id = %s".format(key), (user_id,))
            value = cursor.fetchone()[0]

        return value

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        self.check_if_user_exists(user_id, raise_exception=True)

        with self.conn.cursor() as cursor:
            cursor.execute(f"UPDATE [user] SET {key} = %s WHERE id = %s", (value, user_id))
            self.conn.commit()

    def update_n_used_tokens(self, user_id: int, model: str, n_input_tokens: int, n_output_tokens: int):
        n_used_tokens_dict = self.get_user_attribute(user_id, "n_used_tokens")

        if model in n_used_tokens_dict:
            n_used_tokens_dict[model]["n_input_tokens"] += n_input_tokens
            n_used_tokens_dict[model]["n_output_tokens"] += n_output_tokens
        else:
            n_used_tokens_dict[model] = {
                "n_input_tokens": n_input_tokens,
                "n_output_tokens": n_output_tokens
            }

        self.set_user_attribute(user_id, "n_used_tokens", n_used_tokens_dict)

    def get_dialog_messages(self, user_id: int, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        with self.conn.cursor() as cursor:
            cursor.execute("SELECT messages FROM dialog WHERE id = %s AND user_id = %s", (dialog_id, user_id))
            messages = cursor.fetchone()[0]

        return messages

    def set_dialog_messages(self, user_id: int, dialog_messages: list, dialog_id: Optional[str]=None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        with self.conn.cursor() as cursor:
            cursor.execute("UPDATE dialog SET messages = %s WHERE id = %s AND user_id = %s", (str(dialog_messages), dialog_id, user_id))
            self.conn.commit()
