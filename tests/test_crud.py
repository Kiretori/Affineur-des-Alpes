import api.crud as crud
from database.models import Magasin, Produit


def test_insert_magasin(db_session):
    # Test the insert_magasin function
    magasin = crud.insert_magasin(
        db=db_session,
        id_magasin=None,  # Autoincremented in this case
        nom_magasin="Store1",
        adresse="123 Street",
        ville="City",
        telephone="123456789",
    )
    magasin_from_db = (
        db_session.query(Magasin)
        .filter(Magasin.id_magasin == magasin.id_magasin)
        .first()
    )

    assert magasin_from_db.nom_magasin == "Store1"
    assert magasin_from_db.ville == "City"
    assert magasin_from_db.adresse == "123 Street"
    assert magasin_from_db.telephone == "123456789"


def test_insert_promotion_with_invalid_produit(db_session):
    # Test inserting promotion with invalid product
    try:
        crud.insert_promotion(
            db=db_session,
            id_promotion=None,
            id_produit=999,  # A non-existing product ID
            description="Invalid Promotion",
            date_debut="2024-06-01",
            date_fin="2024-06-30",
            taux_reduction=10,
        )
    except ValueError as exc:
        assert str(exc) == "Produit not found with filters {'id_produit': 999}"


def test_update_produit(db_session):
    produit = crud.insert_produit(
        db=db_session,
        id_produit=1,
        nom_produit="Test product",
        categorie="Cheese",
        prix_unitaire=600,
        stock_central=50,
    )
    produit_from_db = (
        db_session.query(Produit)
        .filter(Produit.id_produit == produit.id_produit)
        .first()
    )
    assert produit_from_db.prix_unitaire == 600
    affected = crud.update_produit_prix(db=db_session, id_produit=1, new_prix=800)
    db_session.refresh(produit_from_db)

    assert affected == 1
    assert produit_from_db.prix_unitaire == 800


def test_increment_produit_stock(db_session):
    produit = crud.insert_produit(
        db=db_session,
        id_produit=1,
        nom_produit="Test product",
        categorie="Cheese",
        prix_unitaire=600,
        stock_central=50,
    )
    produit_from_db = (
        db_session.query(Produit)
        .filter(Produit.id_produit == produit.id_produit)
        .first()
    )
    assert produit_from_db.stock_central == 50
    affected = crud.increment_produit_stock(
        db=db_session, id_produit=1, increment_value=100
    )
    db_session.refresh(produit_from_db)

    assert affected == 1
    assert produit_from_db.stock_central == 150


def test_decrement_produit_stock(db_session):
    produit = crud.insert_produit(
        db=db_session,
        id_produit=1,
        nom_produit="Test product",
        categorie="Cheese",
        prix_unitaire=600,
        stock_central=50,
    )
    produit_from_db = (
        db_session.query(Produit)
        .filter(Produit.id_produit == produit.id_produit)
        .first()
    )
    assert produit_from_db.stock_central == 50
    affected = crud.decrement_produit_stock(
        db=db_session, id_produit=1, decrement_value=50
    )
    db_session.refresh(produit_from_db)

    assert affected == 1
    assert produit_from_db.stock_central == 0


def test_decrement_produit_stock_neg(db_session):
    produit = crud.insert_produit(
        db=db_session,
        id_produit=1,
        nom_produit="Test product",
        categorie="Cheese",
        prix_unitaire=600,
        stock_central=50,
    )
    produit_from_db = (
        db_session.query(Produit)
        .filter(Produit.id_produit == produit.id_produit)
        .first()
    )
    assert produit_from_db.stock_central == 50
    affected = crud.decrement_produit_stock(
        db=db_session, id_produit=1, decrement_value=1000
    )
    db_session.refresh(produit_from_db)

    assert affected == 1
    assert produit_from_db.stock_central == 0
