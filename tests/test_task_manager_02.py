import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from task_manager_02_db import (
    vytvoreni_tabulky,
    db_pridat_ukol,
    db_ziskat_ukoly,
    db_aktualizovat_stav,
    db_odstranit_ukol,
    db_smazat_vsechny_ukoly
)

@pytest.fixture
def test_db():
    # zajistí, že tabulka existuje
    vytvoreni_tabulky()

    # před testem uklidíme
    db_smazat_vsechny_ukoly()

    yield

    # po testu znovu uklidíme
    db_smazat_vsechny_ukoly()

def test_pridani_ukolu(test_db):
    db_pridat_ukol("Test úkol", "Popis testu")

    ukoly = db_ziskat_ukoly()

    assert len(ukoly) == 1
    assert ukoly[0][1] == "Test úkol"

def test_odstraneni_ukolu(test_db):
    db_pridat_ukol("Mazací úkol", "Bude smazán")

    ukoly = db_ziskat_ukoly()
    ukol_id = ukoly[0][0]

    db_odstranit_ukol(ukol_id)

    ukoly_po = db_ziskat_ukoly()
    assert len(ukoly_po) == 0

def test_aktualizace_stavu(test_db):
    db_pridat_ukol("Úkol k aktualizaci", "Popis úkolu")
    
    ukoly = db_ziskat_ukoly()
    ukol_id = ukoly[0][0]

    db_aktualizovat_stav(ukol_id, "Probíhá")

    ukoly_po = db_ziskat_ukoly()
    assert ukoly_po[0][3] == "Probíhá"

def test_pridani_neplatneho_ukolu(test_db):
    # prázdný název
    db_pridat_ukol("", "Popis")
    ukoly = db_ziskat_ukoly()
    assert len(ukoly) == 0  # žádný úkol se neměl přidat

    # prázdný popis
    db_pridat_ukol("Název", "")
    ukoly = db_ziskat_ukoly()
    assert len(ukoly) == 0

def test_aktualizace_neexistujiciho_id(test_db):
    db_pridat_ukol("Existující úkol", "Popis")
    ukoly = db_ziskat_ukoly()
    existujici_id = ukoly[0][0]

    # zkusíme ID, které neexistuje
    neexistujici_id = existujici_id + 100
    db_aktualizovat_stav(neexistujici_id, "Hotovo")

    # ujistíme se, že existující úkol zůstal nezměněn
    ukoly_po = db_ziskat_ukoly()
    assert ukoly_po[0][3] == "Nezahájeno"

def test_mazani_neexistujiciho_id(test_db):
    db_pridat_ukol("Úkol k mazání", "Popis")
    ukoly = db_ziskat_ukoly()
    existujici_id = ukoly[0][0]

    # zkusíme ID, které neexistuje
    neexistujici_id = existujici_id + 100
    db_odstranit_ukol(neexistujici_id)

    # ujistíme se, že existující úkol zůstal
    ukoly_po = db_ziskat_ukoly()
    assert len(ukoly_po) == 1
    assert ukoly_po[0][0] == existujici_id
