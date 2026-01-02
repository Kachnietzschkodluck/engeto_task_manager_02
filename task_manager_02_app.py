from task_manager_02_db import (
    vytvoreni_tabulky,
    db_pridat_ukol,
    db_ziskat_ukoly,
    db_aktualizovat_stav,
    db_odstranit_ukol
)


def pridat_ukol():
    print("\n--- Přidání úkolu ---")
    nazev = input("Zadej název úkolu: ").strip()
    popis = input("Zadej popis úkolu: ").strip()

    db_pridat_ukol(nazev, popis)


def zobrazit_ukoly():
    print("\n--- Seznam úkolů ---")
    ukoly = db_ziskat_ukoly(["Nezahájeno", "Probíhá"])

    if not ukoly:
        print("Žádné úkoly k zobrazení.")
        return

    for ukol in ukoly:
        print(f"ID: {ukol[0]} | Název: {ukol[1]} | Popis: {ukol[2]} | Stav: {ukol[3]}")


def aktualizovat_ukol():
    print("\n--- Aktualizace úkolu ---")
    ukoly = db_ziskat_ukoly()

    if not ukoly:
        print("Neexistují žádné úkoly.")
        return

    for ukol in ukoly:
        print(f"ID: {ukol[0]} | Název: {ukol[1]} | Stav: {ukol[3]}")

    try:
        ukol_id = int(input("Zadej ID úkolu: "))
    except ValueError:
        print("ID musí být číslo.")
        return

    print("Vyber nový stav:")
    print("1. Probíhá")
    print("2. Hotovo")

    volba = input("Volba: ")

    if volba == "1":
        novy_stav = "Probíhá"
    elif volba == "2":
        novy_stav = "Hotovo"
    else:
        print("Neplatná volba.")
        return

    db_aktualizovat_stav(ukol_id, novy_stav)


def odstranit_ukol():
    print("\n--- Odstranění úkolu ---")
    ukoly = db_ziskat_ukoly()

    if not ukoly:
        print("Neexistují žádné úkoly.")
        return

    for ukol in ukoly:
        print(f"ID: {ukol[0]} | Název: {ukol[1]} | Stav: {ukol[3]}")

    try:
        ukol_id = int(input("Zadej ID úkolu k odstranění: "))
    except ValueError:
        print("ID musí být číslo.")
        return

    potvrzeni = input("Opravdu chceš úkol smazat? (a/n): ").lower()
    if potvrzeni == "a":
        db_odstranit_ukol(ukol_id)
        print("Úkol byl odstraněn.")
    else:
        print("Akce zrušena.")


def hlavni_menu():
    while True:
        print("\n=== TASK MANAGER ===")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Ukončit program")

        volba = input("Vyber možnost: ")

        if volba == "1":
            pridat_ukol()
        elif volba == "2":
            zobrazit_ukoly()
        elif volba == "3":
            aktualizovat_ukol()
        elif volba == "4":
            odstranit_ukol()
        elif volba == "5":
            print("Ukončuji program.")
            break
        else:
            print("Neplatná volba, zkus to znovu.")


if __name__ == "__main__":
    vytvoreni_tabulky()
    hlavni_menu()
