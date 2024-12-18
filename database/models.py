from sqlalchemy import Column, Integer, String, ForeignKey, Date, DECIMAL, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Magasin(Base):
    __tablename__ = "Magasins"

    id_magasin = Column(Integer, primary_key=True, autoincrement=True)
    nom_magasin = Column(String, nullable=False)
    adresse = Column(String, nullable=False)
    ville = Column(String, nullable=False)
    telephone = Column(String, nullable=False)

class Produits(Base):
    __tablename__ = "Produits"

    id_produit = Column(Integer, primary_key=True, autoincrement=True)
    nom_produit = Column(String, nullable=False)
    categorie = Column(String, nullable=False)
    prix_unitaire = Column(DECIMAL(10, 2), nullable=False)
    stock_central = Column(Integer, default=0)

class Clients(Base):
    __tablename__ = "Clients"

    id_client = Column(Integer, primary_key=True, autoincrement=True)
    nom_client = Column(String, nullable=False)
    type_client = Column(String, nullable=False)
    adresse = Column(String, nullable=True)
    telephone = Column(String, nullable=True)
    points_fidelite = Column(Integer, default=0)


class Promotion(Base):
    __tablename__ = 'Promotions'

    id_promotion = Column(Integer, primary_key=True, autoincrement=True)
    id_produit = Column(Integer, ForeignKey('Produits.id_produit'), nullable=False)
    description = Column(String(255))
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    taux_reduction = Column(DECIMAL(5, 2), nullable=False)

    produit = relationship("Produit", back_populates="promotions")

class Commande(Base):
    __tablename__ = 'Commandes'

    id_commande = Column(Integer, primary_key=True, autoincrement=True)
    id_client = Column(Integer, ForeignKey('Clients.id_client'), nullable=False)
    id_magasin = Column(Integer, ForeignKey('Magasins.id_magasin'), nullable=False)
    date_commande = Column(DateTime, nullable=False)
    statut_commande = Column(String(20), default='En cours')

    client = relationship("Client", back_populates="commandes")
    magasin = relationship("Magasin", back_populates="commandes")

class LigneCommande(Base):
    __tablename__ = 'Lignes_Commande'

    id_ligne = Column(Integer, primary_key=True, autoincrement=True)
    id_commande = Column(Integer, ForeignKey('Commandes.id_commande'), nullable=False)
    id_produit = Column(Integer, ForeignKey('Produits.id_produit'), nullable=False)
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(DECIMAL(10, 2), nullable=False)

    commande = relationship("Commande", back_populates="lignes")
    produit = relationship("Produit", back_populates="lignes_commande")

class Livraison(Base):
    __tablename__ = 'Livraisons'

    id_livraison = Column(Integer, primary_key=True, autoincrement=True)
    id_commande = Column(Integer, ForeignKey('Commandes.id_commande'), nullable=False)
    id_magasin = Column(Integer, ForeignKey('Magasins.id_magasin'), nullable=False)
    date_livraison = Column(DateTime, nullable=False)
    statut_livraison = Column(String(20), default='En attente')

    commande = relationship("Commande", back_populates="livraisons")
    magasin = relationship("Magasin", back_populates="livraisons")

class Facture(Base):
    __tablename__ = 'Factures'

    id_facture = Column(Integer, primary_key=True, autoincrement=True)
    id_commande = Column(Integer, ForeignKey('Commandes.id_commande'), nullable=False)
    montant_total = Column(DECIMAL(10, 2), nullable=False)
    date_facture = Column(DateTime, nullable=False)

    commande = relationship("Commande", back_populates="facture")

class StockMagasin(Base):
    __tablename__ = 'Stock_Magasins'

    id_magasin = Column(Integer, ForeignKey('Magasins.id_magasin'), primary_key=True)
    id_produit = Column(Integer, ForeignKey('Produits.id_produit'), primary_key=True)
    stock_disponible = Column(Integer, default=0)

    magasin = relationship("Magasin", back_populates="stocks")
    produit = relationship("Produit", back_populates="stocks_magasins")

class HistoriqueFidelite(Base):
    __tablename__ = 'Historique_Fidelite'

    id_historique = Column(Integer, primary_key=True, autoincrement=True)
    id_client = Column(Integer, ForeignKey('Clients.id_client'), nullable=False)
    date_operation = Column(DateTime, nullable=False)
    points_ajoutes = Column(Integer, nullable=False)
    description = Column(String(255))

    client = relationship("Client", back_populates="historique_fidelite")

