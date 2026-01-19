import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from task_manager_02_db import (
    pripojeni_db,
    vytvoreni_tabulky,
    db_pridat_ukol,
    db_aktualizovat_stav,
    db_odstranit_ukol,
    db_smazat_vsechny_ukoly,
)


@pytest.fixture
def test_db_spojeni():
    """Vytvoří připojení do test DB a po každém testu uklidí data."""
    spojeni = pripojeni_db(test=True)

    # tabulka musí existovat
    assert vytvoreni_tabulky(spojeni) is True

    # před testem uklidit
    assert db_smazat_vsechny_ukoly(spojeni) is True

    yield spojeni

    # po testu uklidit
    db_smazat_vsechny_ukoly(spojeni)
    spojeni.close()


def _select_all_ukoly(spojeni):
    """Pomocný SELECT pro ověření dat v testech (nezávisle na db_ziskat_ukoly)."""
    with spojeni.cursor() as cursor:
        cursor.execute("SELECT id, nazev, popis, stav FROM ukoly ORDER BY id")
        return cursor.fetchall()


def test_pridani_ukolu_pozitivni(test_db_spojeni):
    new_id = db_pridat_ukol(test_db_spojeni, "Test úkol", "Popis testu")
    assert new_id is not None

    ukoly = _select_all_ukoly(test_db_spojeni)
    assert len(ukoly) == 1
    assert ukoly[0]["nazev"] == "Test úkol"
    assert ukoly[0]["popis"] == "Popis testu"
    assert ukoly[0]["stav"] == "Nezahájeno"


def test_pridani_ukolu_negativni(test_db_spojeni):
    # prázdný název
    new_id = db_pridat_ukol(test_db_spojeni, "", "Popis")
    assert new_id is None

    # prázdný popis
    new_id2 = db_pridat_ukol(test_db_spojeni, "Název", "")
    assert new_id2 is None

    ukoly = _select_all_ukoly(test_db_spojeni)
    assert len(ukoly) == 0


def test_aktualizace_stavu_pozitivni(test_db_spojeni):
    new_id = db_pridat_ukol(test_db_spojeni, "Úkol k aktualizaci", "Popis úkolu")
    assert new_id is not None

    ok = db_aktualizovat_stav(test_db_spojeni, new_id, "Probíhá")
    assert ok is True

    ukoly = _select_all_ukoly(test_db_spojeni)
    assert len(ukoly) == 1
    assert ukoly[0]["id"] == new_id
    assert ukoly[0]["stav"] == "Probíhá"


def test_aktualizace_stavu_negativni_neexistujici_id(test_db_spojeni):
    # do DB dáme jeden existující úkol
    existujici_id = db_pridat_ukol(test_db_spojeni, "Existující úkol", "Popis")
    assert existujici_id is not None

    # zkusíme ID, které určitě neexistuje
    ok = db_aktualizovat_stav(test_db_spojeni, existujici_id + 9999, "Hotovo")
    assert ok is False

    # ověř, že existující zůstal nezměněn
    ukoly = _select_all_ukoly(test_db_spojeni)
    assert len(ukoly) == 1
    assert ukoly[0]["id"] == existujici_id
    assert ukoly[0]["stav"] == "Nezahájeno"


def test_odstraneni_ukolu_pozitivni(test_db_spojeni):
    new_id = db_pridat_ukol(test_db_spojeni, "Mazací úkol", "Bude smazán")
    assert new_id is not None

    ok = db_odstranit_ukol(test_db_spojeni, new_id)
    assert ok is True

    ukoly = _select_all_ukoly(test_db_spojeni)
    assert len(ukoly) == 0


def test_odstraneni_ukolu_negativni_neexistujici_id(test_db_spojeni):
    existujici_id = db_pridat_ukol(test_db_spojeni, "Úkol k mazání", "Popis")
    assert existujici_id is not None

    ok = db_odstranit_ukol(test_db_spojeni, existujici_id + 9999)
    assert ok is False

    # existující musí pořád být v DB
    ukoly = _select_all_ukoly(test_db_spojeni)
    assert len(ukoly) == 1
    assert ukoly[0]["id"] == existujici_id
