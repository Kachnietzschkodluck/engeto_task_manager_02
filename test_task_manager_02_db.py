import pytest
from task_manager_02_db import db_pridat_ukol, db_ziskat_ukoly, db_aktualizovat_stav, db_odstranit_ukol
import random

# -------------------- Pomocná funkce pro generování unikátního textu --------------------
def unik_text(baze="TEST"):
    return f"{baze}_{random.randint(10000, 99999)}"

# -------------------- Fixture pro testovací úkol --------------------
@pytest.fixture
def test_ukol():
    nazev = unik_text("Testovací úkol")
    popis = unik_text("Popis")
    db_pridat_ukol(nazev, popis)
    ukoly = db_ziskat_ukoly(["Nezahájeno"])
    ukol = next((u for u in ukoly if u[1] == nazev), None)
    yield ukol
    if ukol:
        db_odstranit_ukol(ukol[0])

# -------------------- Přidání úkolu --------------------
def test_pridat_ukol_pozitivni():
    nazev = unik_text("Pozitivní úkol")
    popis = unik_text("Popis pozitivního úkolu")
    db_pridat_ukol(nazev, popis)
    ukoly = db_ziskat_ukoly(["Nezahájeno"])
    ukol_nalezen = any(u[1] == nazev for u in ukoly)
    # Smazání testovacího úkolu
    for u in ukoly:
        if u[1] == nazev:
            db_odstranit_ukol(u[0])
    assert ukol_nalezen

def test_pridat_ukol_negativni():
    unik_popis = unik_text("Popis bez názvu")
    db_pridat_ukol("", unik_popis)
    ukoly = [u for u in db_ziskat_ukoly() if u[2] == unik_popis]
    # Žádný úkol s prázdným názvem by neměl existovat
    assert all(u[1] != "" for u in ukoly)

# -------------------- Aktualizace úkolu --------------------
def test_aktualizovat_ukol_pozitivni(test_ukol):
    db_aktualizovat_stav(test_ukol[0], "Probíhá")
    ukoly = db_ziskat_ukoly(["Probíhá"])
    assert any(u[0] == test_ukol[0] for u in ukoly)

def test_aktualizovat_ukol_negativni():
    # Aktualizace neexistujícího ID
    db_aktualizovat_stav(999999, "Hotovo")
    ukoly = db_ziskat_ukoly(["Hotovo"])
    assert all(u[0] != 999999 for u in ukoly)

# -------------------- Odstranění úkolu --------------------
def test_odstranit_ukol_pozitivni():
    nazev = unik_text("Úkol k odstranění")
    popis = unik_text("Popis")
    db_pridat_ukol(nazev, popis)
    ukoly = db_ziskat_ukoly()
    ukol_id = next(u[0] for u in ukoly if u[1] == nazev)
    db_odstranit_ukol(ukol_id)
    ukoly = db_ziskat_ukoly()
    assert all(u[0] != ukol_id for u in ukoly)

def test_odstranit_ukol_negativni():
    # Odstranění neexistujícího ID
    db_odstranit_ukol(999999)
    ukoly = db_ziskat_ukoly()
    assert all(u[0] != 999999 for u in ukoly)
