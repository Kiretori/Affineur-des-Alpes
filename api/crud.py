from datetime import datetime
from sqlalchemy.sql import and_, or_
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import (
    User,
    UserType,
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


def _get_foreign_key_record(db: Session, model, **filters):
    record = db.query(model).filter_by(**filters).first()
    if not record:
        raise ValueError(f"{model.__name__} not found with filters {filters}")
    return record


def _update_fields(db: Session, model, filters: dict, updates: dict) -> int:
    query = db.query(model).filter_by(**filters)

    if query.count() == 0:
        raise ValueError(
            f"No records found for {model.__name__} with filters {filters}"
        )

    try:
        # Update record(s) with new values
        num_rows_updated = query.update(updates, synchronize_session="fetch")
        db.commit()
        return num_rows_updated
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Error updating {model.__name__}: {e}")


def _increment_field(
    db: Session, model, filters: dict, field_to_increment: str, increment_value: float
) -> int:
    query = db.query(model).filter_by(**filters)
    if query.count() == 0:
        raise ValueError(
            f"No records found for {model.__name__} with filters {filters}"
        )
    try:
        # Update record(s) with new values
        num_rows_updated = query.update(
            {field_to_increment: getattr(model, field_to_increment) + increment_value},
            synchronize_session="fetch",
        )
        db.commit()
        return num_rows_updated
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(
            f"Error incrementing {field_to_increment} for {model.__name__}: {e}"
        )


def _decrement_field(
    db: Session, model, filters: dict, field_to_decrement: str, decrement_value: float
) -> int:
    query = db.query(model).filter_by(**filters)
    if query.count() == 0:
        raise ValueError(
            f"No records found for {model.__name__} with filters {filters}"
        )

    try:
        # Update record(s) with new values
        num_rows_updated = query.update(
            {
                field_to_decrement: func.max(
                    getattr(model, field_to_decrement) - decrement_value, 0
                )
            },
            synchronize_session="fetch",
        )
        db.commit()
        return num_rows_updated
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(
            f"Error incrementing {field_to_decrement} for {model.__name__}: {e}"
        )


def _fetch_by(db: Session, model, filters: dict) -> list:
    query = db.query(model).filter_by(**filters)
    return query.all()


def _fetch_by_conditions(db: Session, model, conditions: list, logic: str) -> list:
    if not conditions:
        return db.query(model).all()

    logic_func = and_ if logic == "and" else or_ if logic == "or" else None
    if logic_func is None:
        raise ValueError(f"Unsupported logic: {logic}")

    try:
        query = db.query(model).filter(logic_func(*conditions))
        return query.all()
    except SQLAlchemyError as e:
        raise ValueError(
            f"Error fetching with {logic} conditions {conditions}. Error: {e}"
        )


def _delete_by(db: Session, model, filters: dict) -> int:
    try:
        num_deleted = db.query(model).filter_by(**filters).delete()
        db.commit()
        return num_deleted
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Error deleting {model.__name__} with {filters}: {e}")


# AUTH
def insert_regular_user(
    db: Session, id_user: int | None, username: str, password: str
) -> User:
    user = User(
        id_user=id_user,
        username=username,
        hashed_password=password,
        role=UserType.regular,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def insert_admin_user(
    db: Session, id_user: int | None, username: str, password: str
) -> User:
    user = User(
        id_user=id_user,
        username=username,
        hashed_password=password,
        role=UserType.admin,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


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
    stock_central: int | None,
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
    produit = _get_foreign_key_record(db, Produit, id_produit=id_produit)

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
    client = _get_foreign_key_record(db, Client, id_client=id_client)
    magasin = _get_foreign_key_record(db, Magasin, id_magasin=id_magasin)

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
    commande = _get_foreign_key_record(db, Commande, id_commande=id_commande)
    produit = _get_foreign_key_record(db, Produit, id_produit=id_produit)

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
    commande = _get_foreign_key_record(db, Commande, id_commande=id_commande)
    magasin = _get_foreign_key_record(db, Magasin, id_magasin=id_magasin)

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
    commande = _get_foreign_key_record(db, Commande, id_commande=id_commande)

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
    magasin = _get_foreign_key_record(db, Magasin, id_magasin=id_magasin)
    produit = _get_foreign_key_record(db, Produit, id_produit=id_produit)

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
    client = _get_foreign_key_record(db, Client, id_client=id_client)

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


def update_produit_prix(db: Session, id_produit: int, new_prix: float) -> int:
    return _update_fields(
        db, Produit, {"id_produit": id_produit}, {"prix_unitaire": new_prix}
    )


def update_produit_nom(db: Session, id_produit: int, new_nom: str) -> int:
    return _update_fields(
        db, Produit, {"id_produit": id_produit}, {"nom_produit": new_nom}
    )


def update_produit_categorie(db: Session, id_produit: int, new_categorie: str) -> int:
    return _update_fields(
        db, Produit, {"id_produit": id_produit}, {"categorie": new_categorie}
    )


def fetch_produit_by_id(db: Session, id_produit: str) -> Produit:
    return _fetch_by(db, Produit, {"id_produit": id_produit})[0]


def fetch_produit_by_nom(db: Session, nom_produit: str) -> list[Produit]:
    return _fetch_by(db, Produit, {"nom_produit": nom_produit})


def fetch_produit_by_categorie(db: Session, categorie: str) -> list[Produit]:
    return _fetch_by(db, Produit, {"categorie": categorie})


def fetch_produit_by_condition(db: Session, conditions: list) -> list[Produit]:
    return _fetch_by_conditions(db, Produit, conditions, "and")


def delete_produit_by_id(db: Session, id_produit: int) -> int:
    return _delete_by(db, Produit, {"id_produit": id_produit})


def increment_produit_stock(
    db: Session, id_produit: int, increment_value: float
) -> int:
    return _increment_field(
        db, Produit, {"id_produit": id_produit}, "stock_central", increment_value
    )


def decrement_produit_stock(
    db: Session, id_produit: int, decrement_value: float
) -> int:
    return _decrement_field(
        db, Produit, {"id_produit": id_produit}, "stock_central", decrement_value
    )


def increment_fidelite_client(
    db: Session, id_client: int, increment_value: float
) -> int:
    return _increment_field(
        db, Client, {"id_client": id_client}, "points_fidelite", increment_value
    )


def decrement_fidelite_client(
    db: Session, id_client: int, decrement_value: float
) -> int:
    return _decrement_field(
        db, Client, {"id_client": id_client}, "points_fidelite", decrement_value
    )


# Rechercher client par id
def fetch_client_by_id(db: Session, id_client: int) -> Client:
    return _fetch_by(db, Client, {"id_client": id_client})[0]


# Rechercher client par nom
def fetch_client_by_name(db: Session, nom_client: int) -> list[Client]:
    return _fetch_by(db, Client, {"nom_client": nom_client})


# Rechercher client par points de fidelité
def fetch_client_by_fidelite(db: Session, points_fidelite: int) -> list[Client]:
    return _fetch_by(db, Client, {"points_fidelite": points_fidelite})


# Rechercher client par type
def fetch_client_by_type(db: Session, type_client: str) -> list[Client]:
    return _fetch_by(db, Client, {"type_client": type_client})


def fetch_client_by_conditions(db: Session, conditions: list) -> list[Client]:
    return _fetch_by_conditions(db, Client, conditions, "and")


def delete_client_by_id(db: Session, id_client: int) -> int:
    return _delete_by(db, Client, {"id_client": id_client})


def fetch_commande_by_id(db: Session, id_commande: int) -> Commande:
    return _fetch_by(db, Commande, {"id_commande": id_commande})[0]


def fetch_commande_by_conditions(
    db: Session, conditions: list, logic: str
) -> list[Commande]:
    return _fetch_by_conditions(db, Commande, conditions, logic)


def modify_commande_status(db: Session, id_commande: int, new_status: str) -> int:
    return _update_fields(
        db, Commande, {"id_commande": id_commande}, {"status_commande": new_status}
    )
