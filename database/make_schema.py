from datetime import datetime
from .models import Base
from .connect_db import engine
from .connect_db import get_db_connection
from api.crud import insert_magasin, insert_produit, insert_promotion


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

db = next(get_db_connection())  # This retrieves the session from the generator

insert_magasin(
    db=db,
    id_magasin=None,
    nom_magasin="Store1",
    adresse="123 Street",
    ville="City",
    telephone="123456789",
)

insert_produit(
    db=db,
    id_produit=1,
    nom_produit="Test product",
    categorie="Cheese",
    prix_unitaire=600,
    stock_central=50,
)

insert_promotion(
    db=db,
    id_promotion=None,
    id_produit=1,
    description="Invalid Promotion",
    date_debut=datetime(2024, 12, 27, 12, 30),
    date_fin=datetime(2024, 12, 27, 12, 30),
    taux_reduction=10,
)
