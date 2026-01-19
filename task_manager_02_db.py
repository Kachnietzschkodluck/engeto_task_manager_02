import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def pripojeni_db(test=False):
    if test:
        db_name = os.getenv("DB_NAME_TEST")
    else:
        db_name = os.getenv("DB_NAME_PROD")

    if not db_name:
        raise ValueError("Chybí DB_NAME_PROD / DB_NAME_TEST v .env")

    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not host or not user or password is None:
        raise ValueError("Chybí DB_HOST / DB_USER / DB_PASSWORD v .env")

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

def vytvoreni_tabulky(spojeni):
    """Vytvoří tabulku 'ukoly', pokud ještě neexistuje."""
    if spojeni is None:
        return False

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
        return True
    except Exception as e:
        spojeni.rollback()
        print(f"Chyba při vytváření tabulky: {e}")
        return False

def db_pridat_ukol(spojeni, nazev, popis):
    """Přidá úkol do databáze.

    Parametry:
        spojeni: aktivní DB connection (produkční nebo testovací)
        nazev (str): název úkolu
        popis (str): popis úkolu

    Vrací:
        int  - ID nově vloženého úkolu
        None - pokud je vstup neplatný nebo nastala chyba
    """
    if spojeni is None:
        return None

    nazev = nazev.strip()
    popis = popis.strip()

    if not nazev or not popis:
        return None
    if len(nazev) > 255:
        return None

    try:
        with spojeni.cursor() as cursor:
            sql = "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)"
            cursor.execute(sql, (nazev, popis))
            new_id = cursor.lastrowid
        spojeni.commit()
        return new_id
    except Exception as e:
        spojeni.rollback()
        print(f"Chyba při přidávání úkolu: {e}")
        return None

def db_ziskat_ukoly(spojeni, stavy=None):
    """Vrátí seznam úkolů z DB, volitelně filtrovaný podle stavů.

    Parametry:
        spojeni: aktivní DB connection
        stavy (list[str] | None): např. ["Nezahájeno", "Probíhá"]

    Vrací:
        list[dict]: seznam úkolů (DictCursor) nebo prázdný seznam
    """
    if spojeni is None:
        return []

    try:
        with spojeni.cursor() as cursor:
            if stavy:
                placeholders = ", ".join(["%s"] * len(stavy))
                sql = f"""
                    SELECT id, nazev, popis, stav, datum_vytvoreni
                    FROM ukoly
                    WHERE stav IN ({placeholders})
                    ORDER BY id
                """
                cursor.execute(sql, stavy)
            else:
                sql = """
                    SELECT id, nazev, popis, stav, datum_vytvoreni
                    FROM ukoly
                    ORDER BY id
                """
                cursor.execute(sql)

            return cursor.fetchall()
    except Exception as e:
        print(f"Chyba při získávání úkolů: {e}")
        return []

def db_ukol_existuje(spojeni, ukol_id):
    """Ověří, zda úkol s daným ID existuje."""
    if spojeni is None:
        return False

    try:
        with spojeni.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM ukoly WHERE id = %s",
                (ukol_id,)
            )
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Chyba při ověřování existence úkolu: {e}")
        return False

def db_aktualizovat_stav(spojeni, ukol_id, novy_stav):
    """Aktualizuje stav úkolu podle ID.

    Vrací:
        True  - pokud úkol existuje a operace proběhla (i když se stav nezměnil)
        False - pokud úkol neexistuje, stav je neplatný nebo nastala chyba
    """
    if spojeni is None:
        return False

    povolene_stavy = {"Probíhá", "Hotovo", "Nezahájeno"}
    if novy_stav not in povolene_stavy:
        return False

    # 1) Nejdřív ověř, že ID existuje
    if not db_ukol_existuje(spojeni, ukol_id):
        return False

    # 2) Pak teprve update
    try:
        with spojeni.cursor() as cursor:
            sql = "UPDATE ukoly SET stav = %s WHERE id = %s"
            cursor.execute(sql, (novy_stav, ukol_id))
        spojeni.commit()
        return True
    except Exception as e:
        spojeni.rollback()
        print(f"Chyba při aktualizaci úkolu: {e}")
        return False

def db_odstranit_ukol(spojeni, ukol_id):
    """Odstraní úkol podle ID.

    Vrací:
        True  - pokud úkol existoval a byl odstraněn
        False - pokud úkol s daným ID neexistuje nebo nastala chyba
    """
    if spojeni is None:
        return False

    # 1) Ověření existence úkolu
    if not db_ukol_existuje(spojeni, ukol_id):
        return False

    # 2) Smazání
    try:
        with spojeni.cursor() as cursor:
            sql = "DELETE FROM ukoly WHERE id = %s"
            cursor.execute(sql, (ukol_id,))
        spojeni.commit()
        return True
    except Exception as e:
        spojeni.rollback()
        print(f"Chyba při mazání úkolu: {e}")
        return False

def db_smazat_vsechny_ukoly(spojeni):
    """Smaže všechny úkoly z tabulky.
    Používá se pouze v testech nebo pro lokální reset.
    """
    if spojeni is None:
        return False

    try:
        with spojeni.cursor() as cursor:
            cursor.execute("DELETE FROM ukoly")
        spojeni.commit()
        return True
    except Exception as e:
        spojeni.rollback()
        print(f"Chyba při mazání všech úkolů: {e}")
        return False
