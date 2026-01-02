import pymysql

def pripojeni_db():
    try:
        spojeni = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='1111',
            database='ukoly_db'
        )
        return spojeni
    except Exception as e:
        print(f"Chyba při připojení: {e}")
        return None

def vytvoreni_tabulky():
    spojeni = pripojeni_db()
    if spojeni is None:
        return
    try:
        with spojeni.cursor() as cursor:
            sql = """
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT NOT NULL,
                stav VARCHAR(20) NOT NULL DEFAULT 'Nezahájeno',
                datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(sql)
        spojeni.commit()
    except Exception as e:
        print(f"Chyba při vytváření tabulky: {e}")
    finally:
        spojeni.close()

def db_pridat_ukol(nazev, popis):
    nazev = nazev.strip()
    popis = popis.strip()
    if not nazev or not popis:
        print("Název a popis musí být vyplněny!")
        return
    if len(nazev) > 255:
        print("Název nesmí být delší než 255 znaků!")
        return
    spojeni = pripojeni_db()
    if spojeni is None:
        return
    try:
        with spojeni.cursor() as cursor:
            sql = "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)"
            cursor.execute(sql, (nazev, popis))
        spojeni.commit()
    except Exception as e:
        print(f"Chyba při přidávání úkolu: {e}")
    finally:
        spojeni.close()

def db_ziskat_ukoly(stavy=None):
    spojeni = pripojeni_db()
    if spojeni is None:
        return []
    try:
        with spojeni.cursor() as cursor:
            if stavy:
                placeholders = ", ".join(["%s"] * len(stavy))
                sql = f"SELECT id, nazev, popis, stav FROM ukoly WHERE stav IN ({placeholders})"
                cursor.execute(sql, stavy)
            else:
                sql = "SELECT id, nazev, popis, stav FROM ukoly"
                cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"Chyba při získávání úkolů: {e}")
        return []
    finally:
        spojeni.close()

def db_aktualizovat_stav(ukol_id, novy_stav):
    spojeni = pripojeni_db()
    if spojeni is None:
        return
    try:
        with spojeni.cursor() as cursor:
            sql = "UPDATE ukoly SET stav = %s WHERE id = %s"
            cursor.execute(sql, (novy_stav, ukol_id))
        spojeni.commit()
    except Exception as e:
        print(f"Chyba při aktualizaci úkolu: {e}")
    finally:
        spojeni.close()

def db_odstranit_ukol(ukol_id):
    spojeni = pripojeni_db()
    if spojeni is None:
        return
    try:
        with spojeni.cursor() as cursor:
            sql = "DELETE FROM ukoly WHERE id = %s"
            cursor.execute(sql, (ukol_id,))
        spojeni.commit()
    except Exception as e:
        print(f"Chyba při mazání úkolu: {e}")
    finally:
        spojeni.close()
