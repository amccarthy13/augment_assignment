import atexit

from flask import Flask

from resources import postgres
from resources.postgres import PostgreSQL


class AugmentApp(Flask):
    def __init__(self, import_name, **kwargs):
        super().__init__(import_name, **kwargs)
        self.postgres = None
        atexit.register(self.shutdown_handler)

    def set_postgres(self):
        postgres_instance = PostgreSQL()
        postgres_instance.set_db_connection()
        self.postgres = postgres_instance

    def shutdown_handler(self):
        if postgres is not None:
            self.postgres.conn.close()

