from datetime import datetime
import api.crud as crud
from database.models import Magasin, Produit, Client, Promotion


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


def test_increment_fidelite_client(db_session):
    client = crud.insert_client(
        db=db_session,
        id_client=1,
        nom_client="test client",
        type_client="test type",
        adresse="test address",
        telephone="5555555",
        point_fidelite=50,
    )
    client_from_db = (
        db_session.query(Client).filter(Client.id_client == client.id_client).first()
    )
    assert client_from_db.points_fidelite == 50
    affected = crud.increment_fidelite_client(
        db=db_session, id_client=1, increment_value=1000
    )
    db_session.refresh(client_from_db)

    assert affected == 1
    assert client_from_db.points_fidelite == 1050


def test_decrement_fidelite_client(db_session):
    client = crud.insert_client(
        db=db_session,
        id_client=1,
        nom_client="test client",
        type_client="test type",
        adresse="test address",
        telephone="5555555",
        point_fidelite=50,
    )
    client_from_db = (
        db_session.query(Client).filter(Client.id_client == client.id_client).first()
    )
    assert client_from_db.points_fidelite == 50
    affected = crud.decrement_fidelite_client(
        db=db_session, id_client=1, decrement_value=1000
    )
    db_session.refresh(client_from_db)

    assert affected == 1
    assert client_from_db.points_fidelite == 0


def test_fetch_client_by_id(db_session):
    client = crud.insert_client(
        db=db_session,
        id_client=1,
        nom_client="test client",
        type_client="test type",
        adresse="test address",
        telephone="5555555",
        point_fidelite=50,
    )

    client_from_db = crud.fetch_client_by_id(db_session, 1)
    assert client.id_client == client_from_db.id_client  # type: ignore
    assert client.nom_client == client_from_db.nom_client  # type: ignore


def test_fetch_client_by_fidelite(db_session):
    crud.insert_client(
        db=db_session,
        id_client=1,
        nom_client="test client1",
        type_client="test type",
        adresse="test address",
        telephone="5555555",
        point_fidelite=0,
    )
    client2 = crud.insert_client(
        db=db_session,
        id_client=2,
        nom_client="test client2",
        type_client="test type",
        adresse="test address",
        telephone="5555555",
        point_fidelite=50,
    )
    client3 = crud.insert_client(
        db=db_session,
        id_client=3,
        nom_client="test client3",
        type_client="test type",
        adresse="test address",
        telephone="5555555",
        point_fidelite=50,
    )
    client4 = crud.insert_client(
        db=db_session,
        id_client=4,
        nom_client="test client4",
        type_client="test type",
        adresse="test address",
        telephone="5555555",
        point_fidelite=50,
    )

    clients_from_db = crud.fetch_client_by_fidelite(db_session, 50)
    assert len(clients_from_db) == 3
    assert client2.nom_client == clients_from_db[0].nom_client  # type: ignore
    assert client3.nom_client == clients_from_db[1].nom_client  # type: ignore
    assert client4.nom_client == clients_from_db[2].nom_client  # type: ignore


def test_fetch_client_by_type(db_session):
    crud.insert_client(
        db=db_session,
        id_client=1,
        nom_client="test client1",
        type_client="Epicerie",
        adresse="test address",
        telephone="5555555",
        point_fidelite=0,
    )
    client2 = crud.insert_client(
        db=db_session,
        id_client=2,
        nom_client="test client2",
        type_client="Individu",
        adresse="test address",
        telephone="5555555",
        point_fidelite=50,
    )
    client3 = crud.insert_client(
        db=db_session,
        id_client=3,
        nom_client="test client3",
        type_client="Individu",
        adresse="test address",
        telephone="5555555",
        point_fidelite=50,
    )
    client4 = crud.insert_client(
        db=db_session,
        id_client=4,
        nom_client="test client4",
        type_client="Individu",
        adresse="test address",
        telephone="5555555",
        point_fidelite=50,
    )

    clients_from_db = crud.fetch_client_by_type(db_session, "Individu")
    assert len(clients_from_db) == 3
    assert client2.nom_client == clients_from_db[0].nom_client  # type: ignore
    assert client3.nom_client == clients_from_db[1].nom_client  # type: ignore
    assert client4.nom_client == clients_from_db[2].nom_client  # type: ignore


def test_delete_client_id(db_session):
    crud.insert_client(
        db=db_session,
        id_client=1,
        nom_client="test client1",
        type_client="Epicerie",
        adresse="test address",
        telephone="5555555",
        point_fidelite=0,
    )
    crud.insert_client(
        db=db_session,
        id_client=2,
        nom_client="test client2",
        type_client="Individu",
        adresse="test address",
        telephone="5555555",
        point_fidelite=50,
    )

    deleted = crud.delete_client_by_id(db_session, 2)

    clients = db_session.query(Client).all()

    assert deleted == 1
    assert len(clients) == 1


def test_fetch_produit_by_condition(db_session):
    crud.insert_produit(
        db=db_session,
        id_produit=1,
        nom_produit="Test product",
        categorie="Cheese",
        prix_unitaire=600,
        stock_central=50,
    )
    crud.insert_produit(
        db=db_session,
        id_produit=2,
        nom_produit="Test product",
        categorie="Cheese",
        prix_unitaire=40,
        stock_central=100,
    )
    crud.insert_produit(
        db=db_session,
        id_produit=3,
        nom_produit="Test product",
        categorie="Cheese",
        prix_unitaire=100,
        stock_central=200,
    )
    crud.insert_produit(
        db=db_session,
        id_produit=4,
        nom_produit="Test product",
        categorie="Cheese",
        prix_unitaire=600,
        stock_central=300,
    )

    produits = crud.fetch_produit_by_condition(
        db_session, [Produit.stock_central >= 100, Produit.prix_unitaire == 600]
    )

    assert len(produits) == 1


def test_fetch_promotion(db_session):
    crud.insert_produit(
        db=db_session,
        id_produit=3,
        nom_produit="Test product",
        categorie="Cheese",
        prix_unitaire=100,
        stock_central=200,
    )
    promo = crud.insert_promotion(
        db_session,
        None,
        3,
        "Description",
        datetime(2024, 12, 27, 12, 30),
        datetime(2024, 12, 27, 12, 30),
        "0.5",
    )

    promotions = db_session.query(Promotion).all()

    assert promo.description == promotions[0].description
