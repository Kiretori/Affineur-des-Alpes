from datetime import datetime
from sqlalchemy.orm import Session
from database.models import (
    Magasin,
    Produit,
    Client,
    Promotion,
    Commande,
    LigneCommande,
    Livraison,
    Facture,
    StockMagasin,
    HistoriqueFidelite,
)


def get_foreign_key_record(db: Session, model, **filters):
    record = db.query(model).filter_by(**filters).first()
    if not record:
        raise ValueError(f"{model.__name__} not found with filters {filters}")
    return record



# Insert Magasin entry
def insert_magasin(
    db: Session,
    id_magasin: int | None,
    nom_magasin: str,
    adresse: str,
    ville: str,
    telephone: str,
) -> Magasin:
    magasin = Magasin(
        id_magasin=id_magasin,
        nom_magasin=nom_magasin,
        adresse=adresse,
        ville=ville,
        telephone=telephone,
    )

    db.add(magasin)
    db.commit()
    db.refresh(magasin)
    return magasin


# Insert Produit entry
def insert_produit(
    db: Session,
    id_produit: int | None,
    nom_produit: str,
    categorie: str,
    prix_unitaire: float,
    stock_central: str | None,
) -> Produit:
    produit = Produit(
        id_produit=id_produit,
        nom_produit=nom_produit,
        categorie=categorie,
        prix_unitaire=prix_unitaire,
        stock_central=stock_central,
    )

    db.add(produit)
    db.commit()
    db.refresh(produit)
    return produit


# Insert Client entry
def insert_client(
    db: Session,
    id_client: int | None,
    nom_client: str,
    type_client: str,
    adresse: str | None,
    telephone: str | None,
    point_fidelite: int | None,
) -> Client:
    client = Client(
        id_client=id_client,
        nom_client=nom_client,
        type_client=type_client,
        adresse=adresse,
        telephone=telephone,
        points_fidelite=point_fidelite,
    )

    db.add(client)
    db.commit()
    db.refresh(client)
    return client


# Insert Promotion entry
def insert_promotion(
    db: Session,
    id_promotion: int | None,
    id_produit: int,
    description: str,
    date_debut: str,
    date_fin: str,
    taux_reduction: float,
) -> Promotion:
    produit = get_foreign_key_record(db, Produit, id_produit=id_produit)

    if not produit:
        raise ValueError("Produit not found")

    promotion = Promotion(
        id_promotion=id_promotion,
        id_produit=produit.id_produit,
        description=description,
        date_debut=date_debut,
        date_fin=date_fin,
        taux_reduction=taux_reduction,
    )

    db.add(promotion)
    db.commit()
    db.refresh(promotion)
    return promotion


# Insert Commande entry
def insert_commande(
    db: Session,
    id_commande: int | None,
    id_client: int,
    id_magasin: int,
    date_commande: datetime,
    statut_commande: str,
) -> Commande:
    client = get_foreign_key_record(db, Client, id_client=id_client)
    magasin = get_foreign_key_record(db, Magasin, id_magasin=id_magasin)

    if not client or not magasin:
        if not client:
            raise ValueError("Client not found")
        if not magasin:
            raise ValueError("Magasin not found")

    commande = Commande(
        id_commande=id_commande,
        id_client=client.id_client,
        id_magasin=magasin.id_magasin,
        date_commande=date_commande,
        statut_commande=statut_commande,
    )

    db.add(commande)
    db.commit()
    db.refresh(commande)
    return commande


# Insert LigneCommande entry
def insert_ligne_commande(
    db: Session,
    id_ligne: int | None,
    id_commande: int,
    id_produit: int,
    quantite: int,
    prix_unitaire: float,
) -> LigneCommande:
    commande = get_foreign_key_record(db, Commande, id_commande=id_commande)
    produit = get_foreign_key_record(db, Produit, id_produit=id_produit)

    if not commande or not produit:
        if not commande:
            raise ValueError("Commande not found")
        if not produit:
            raise ValueError("Produit not found")

    ligne_commande = LigneCommande(
        id_ligne=id_ligne,
        id_commande=commande.id_commande,
        id_produit=produit.id_produit,
        quantite=quantite,
        prix_unitaire=prix_unitaire,
    )

    db.add(ligne_commande)
    db.commit()
    db.refresh(ligne_commande)
    return ligne_commande


# Insert Livraison entry
def insert_livraison(
    db: Session,
    id_livraison: int | None,
    id_commande: int,
    id_magasin: int,
    date_livraison: datetime,
    statut_livraison: str,
) -> Livraison:
    commande = get_foreign_key_record(db, Commande, id_commande=id_commande)
    magasin = get_foreign_key_record(db, Magasin, id_magasin=id_magasin)

    if not commande or not magasin:
        if not commande:
            raise ValueError("Commande not found")
        if not magasin:
            raise ValueError("Magasin not found")

    livraison = Livraison(
        id_livraison=id_livraison,
        id_commande=commande.id_commande,
        id_magasin=magasin.id_magasin,
        date_livraison=date_livraison,
        statut_livraison=statut_livraison,
    )

    db.add(livraison)
    db.commit()
    db.refresh(livraison)
    return livraison


# Insert Facture entry
def insert_facture(
    db: Session,
    id_facture: int | None,
    id_commande: int,
    montant_total: float,
    date_facture: datetime,
) -> Facture:
    commande = get_foreign_key_record(db, Commande, id_commande=id_commande)

    if not commande:
        raise ValueError("Commande not found")

    facture = Facture(
        id_facture=id_facture,
        id_commande=commande.id_commande,
        date_facture=date_facture,
        montant_total=montant_total,
    )

    db.add(facture)
    db.commit()
    db.refresh(facture)
    return facture


# Insert StockMagasin entry
def insert_stock_magasin(
    db: Session, id_magasin: int, id_produit: int, quantite: int | None
) -> StockMagasin:
    magasin = get_foreign_key_record(db, Magasin, id_magasin=id_magasin)
    produit = get_foreign_key_record(db, Produit, id_produit=id_produit)

    if not magasin or not produit:
        if not magasin:
            raise ValueError("Magasin not found")
        if not produit:
            raise ValueError("Produit not found")

    stock_magasin = StockMagasin(
        id_magasin=magasin.id_magasin,
        id_produit=produit.id_produit,
        quantite=quantite,
    )

    db.add(stock_magasin)
    db.commit()
    db.refresh(stock_magasin)
    return stock_magasin


# Insert HistoriqueFidelite entry
def insert_historique_fidelite(
    db: Session,
    id_historique: int | None,
    id_client: int,
    date_operation: datetime,
    point_ajoutes: int,
    description: str | None,
) -> HistoriqueFidelite:
    client = get_foreign_key_record(db, Client, id_client=id_client)

    if not client:
        raise ValueError("Client not found")

    historique_fidelite = HistoriqueFidelite(
        id_historique=id_historique,
        id_client=client.id_client,
        date_operation=date_operation,
        point_ajoutes=point_ajoutes,
        description=description,
    )

    db.add(historique_fidelite)
    db.commit()
    db.refresh(historique_fidelite)
    return historique_fidelite
