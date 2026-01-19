from task_manager_02_db import (
    pripojeni_db,
    vytvoreni_tabulky,
    db_pridat_ukol,
    db_ziskat_ukoly,
    db_aktualizovat_stav,
    db_odstranit_ukol,
)


def pridat_ukol(spojeni):
    """UI: Přidání úkolu."""
    print("\n--- Přidání úkolu ---")
    nazev = input("Zadej název úkolu: ").strip()
    popis = input("Zadej popis úkolu: ").strip()

    new_id = db_pridat_ukol(spojeni, nazev, popis)
    if new_id is None:
        print("Úkol se nepodařilo přidat (prázdný název/popis nebo chyba).")
    else:
        print(f"Úkol byl přidán (ID: {new_id}).")


def zobrazit_ukoly(spojeni, jen_aktivni=True):
    """UI: Zobrazení úkolů. Ve výchozím stavu filtruje Nezahájeno + Probíhá."""
    print("\n--- Seznam úkolů ---")
    stavy = ["Nezahájeno", "Probíhá"] if jen_aktivni else None
    ukoly = db_ziskat_ukoly(spojeni, stavy)

    if not ukoly:
        print("Žádné úkoly k zobrazení.")
        return []

    for ukol in ukoly:
        print(
            f"ID: {ukol['id']} | Název: {ukol['nazev']} | Popis: {ukol['popis']} | Stav: {ukol['stav']}"
        )
    return ukoly


def aktualizovat_ukol(spojeni):
    """UI: Změna stavu úkolu."""
    print("\n--- Aktualizace úkolu ---")
    ukoly = db_ziskat_ukoly(spojeni)

    if not ukoly:
        print("Neexistují žádné úkoly.")
        return

    for ukol in ukoly:
        print(f"ID: {ukol['id']} | Název: {ukol['nazev']} | Stav: {ukol['stav']}")

    try:
        ukol_id = int(input("Zadej ID úkolu: "))
    except ValueError:
        print("ID musí být číslo.")
        return

    print("Vyber nový stav:")
    print("1. Probíhá")
    print("2. Hotovo")

    volba = input("Volba: ").strip()

    if volba == "1":
        novy_stav = "Probíhá"
    elif volba == "2":
        novy_stav = "Hotovo"
    else:
        print("Neplatná volba.")
        return

    ok = db_aktualizovat_stav(spojeni, ukol_id, novy_stav)
    if not ok:
        print("Úkol s tímto ID neexistuje nebo se nepodařilo změnit stav.")
    else:
        print("Stav úkolu byl aktualizován.")


def odstranit_ukol(spojeni):
    """UI: Odstranění úkolu."""
    print("\n--- Odstranění úkolu ---")
    ukoly = db_ziskat_ukoly(spojeni)

    if not ukoly:
        print("Neexistují žádné úkoly.")
        return

    for ukol in ukoly:
        print(f"ID: {ukol['id']} | Název: {ukol['nazev']} | Stav: {ukol['stav']}")

    try:
        ukol_id = int(input("Zadej ID úkolu k odstranění: "))
    except ValueError:
        print("ID musí být číslo.")
        return

    potvrzeni = input("Opravdu chceš úkol smazat? (a/n): ").strip().lower()
    if potvrzeni != "a":
        print("Akce zrušena.")
        return

    ok = db_odstranit_ukol(spojeni, ukol_id)
    if not ok:
        print("Úkol s tímto ID neexistuje nebo se nepodařilo smazat.")
    else:
        print("Úkol byl odstraněn.")


def hlavni_menu(spojeni):
    """UI: Hlavní smyčka aplikace."""
    while True:
        print("\n=== TASK MANAGER ===")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly (Nezahájeno/Probíhá)")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Ukončit program")

        volba = input("Vyber možnost: ").strip()

        if volba == "1":
            pridat_ukol(spojeni)
        elif volba == "2":
            zobrazit_ukoly(spojeni, jen_aktivni=True)
        elif volba == "3":
            aktualizovat_ukol(spojeni)
        elif volba == "4":
            odstranit_ukol(spojeni)
        elif volba == "5":
            print("Ukončuji program.")
            break
        else:
            print("Neplatná volba, zkus to znovu.")


if __name__ == "__main__":
    spojeni = pripojeni_db(test=False)
    try:
        if not vytvoreni_tabulky(spojeni):
            print("Nepodařilo se připravit tabulku. Ukončuji.")
        else:
            hlavni_menu(spojeni)
    finally:
        spojeni.close()
