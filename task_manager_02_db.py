import pymysql

# --- KONFIGURACE ---
# Zde nastav, kterou databázi chceš používat
PRODUKCNI_DB = "task_manager_02_db"
TEST_DB = "task_manager_02_test_db"

# Vybraná databáze: "PRODUKCNÍ_DB" nebo "TEST_DB"
DB_NAZEV = TEST_DB


def pripojeni_db():
    """Vytvoří připojení k MySQL databázi."""
    try:
        spojeni = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='1111',
            database=DB_NAZEV
        )
        return spojeni
    except Exception as e:
        print(f"Chyba při připojení: {e}")
        return None


def vytvoreni_tabulky():
    """Vytvoří tabulku 'ukoly', pokud ještě neexistuje."""
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
    """Přidá úkol do databáze."""
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
    """Vrátí seznam úkolů, volitelně jen s vybranými stavy."""
    spojeni = pripojeni_db()
    if spojeni is None:
        return []
    try:
        with spojeni.cursor() as cursor:
            if stavy:
                placeholders = ", ".join(["%s"] * len(stavy))
                sql = f"SELECT id, nazev, popis, stav FROM ukoly WHERE stav IN ({placeholders}) ORDER BY id"
                cursor.execute(sql, stavy)
            else:
                sql = "SELECT id, nazev, popis, stav FROM ukoly ORDER BY id"
                cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"Chyba při získávání úkolů: {e}")
        return []
    finally:
        spojeni.close()


def db_aktualizovat_stav(ukol_id, novy_stav):
    """Aktualizuje stav konkrétního úkolu podle jeho ID."""
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
    """Odstraní úkol podle ID."""
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


def db_smazat_vsechny_ukoly():
    """Smaže všechny úkoly z tabulky (pouze pro testy nebo lokální reset)."""
    spojeni = pripojeni_db()
    if spojeni is None:
        return
    try:
        with spojeni.cursor() as cursor:
            cursor.execute("DELETE FROM ukoly")
        spojeni.commit()
        print("Všechny úkoly byly smazány.")
    except Exception as e:
        print(f"Chyba při mazání všech úkolů: {e}")
    finally:
        spojeni.close()
