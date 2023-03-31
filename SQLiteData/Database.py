import aiosqlite


class Database:
    def __init__(self):
        self.db = "./SQLiteData/Database.db"

    async def get_animals(self):
        query = """ SELECT DISTINCT type
                    FROM all_animals"""
        async with aiosqlite.connect(self.db) as db:
            db.row_factory = lambda cursor, row: row[0]
            async with db.execute(query) as cursor:
                return await cursor.fetchall()

    async def tbl_data(self, combo_text, vaccine):
        match combo_text:
            case "Корова":
                query = """SELECT * FROM cows_view WHERE vaccine IN ((?), (?))"""
            case "Овца":
                query = """ SELECT * FROM sheeps_view WHERE vaccine IN ((?), (?))"""
            case "Свинья":
                query = """ SELECT * FROM pigs_view WHERE vaccine IN ((?), (?))"""
            case _:
                query = """ SELECT * FROM all_animals WHERE vaccine IN ((?), (?))"""
        async with aiosqlite.connect(self.db) as db:
            async with db.execute(query, vaccine) as cursor:
                return await cursor.fetchall()

    async def data_save(self, data, name_tbl):
        query = """INSERT INTO {} (id, number, id_type, id_gender, weight, date_birth, vaccine)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""".format(name_tbl)
        async with aiosqlite.connect(self.db) as db:
            async with db.cursor() as cursor:
                await cursor.execute("DELETE FROM {}".format(name_tbl))
                await cursor.executemany(query, data)
                count_rows = cursor.rowcount
            await db.commit()
            return count_rows

