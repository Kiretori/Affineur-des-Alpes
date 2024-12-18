import api.crud as crud
from database.models import Magasin, Commande, Livraison


def test_insert_magasin(db_session):
    # Test the insert_magasin function
    magasin = crud.insert_magasin(
        db=db_session,
        id_magasin=None,  # Autoincremented in this case
        nom_magasin="Store1",
        adresse="123 Street",
        ville="City",
        telephone="123456789"
    )
    magasin_from_db = db_session.query(Magasin).filter(Magasin.id_magasin == magasin.id_magasin).first()

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
            taux_reduction=10
        )
    except ValueError as exc:
        assert str(exc) == "Produit not found with filters {'id_produit': 999}"
