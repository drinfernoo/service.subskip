import pymysql.cursors


_database = "a4kSkips"

create_database_statement = f"create database if not exists {_database};"
create_points_table_statement = "create table if not exists Points (point_id int auto_increment, imdb_id char(10), season int, episode int, type char(10), start time, end time, length time, primary key (point_id));"

get_points_query = "select * from Points where Points.imdb_id=%s and Points.season=%s and Points.episode=%s"


class Database:
    def __init__(self):
        self._host = "localhost"
        self._user = "root"
        self._password = "mysql"
        self._database = _database

        self._create_database()
        self._create_tables()

    def _create_connection(self, database):
        return pymysql.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor,
        )

    def _create_database(self):
        connection = self._create_connection(None)

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(create_database_statement)

            connection.commit()

    def _create_tables(self):
        connection = self._create_connection(self._database)

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(create_points_table_statement)

            connection.commit()

    def get_points(self, imdb, season, episode, type=None):
        connection = self._create_connection(self._database)

        with connection:
            with connection.cursor() as cursor:
                query = get_points_query
                args = [
                    imdb,
                    season,
                    episode,
                ]

                if type is not None:
                    query += " and Points.type=%s;"
                    args.append(type)
                else:
                    query = +";"

                cursor.execute(query, args)
                result = cursor.fetchall()

        return result
