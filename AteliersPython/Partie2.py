"""Solutions de l'Atelier Python — Partie 2 (POO et bibliothèque)."""


class Personne:
    def __init__(self, nom, age):
        self.nom = nom
        self.age = age

    def se_presenter(self):
        return f"Je m'appelle {self.nom} et j'ai {self.age} ans."

    def __str__(self):
        return self.se_presenter()

    def __del__(self):
        nom = getattr(self, "nom", "Cette personne")
        print(f"{nom} a été détruit")


class Etudiant(Personne):
    def __init__(self, nom, age, niveau):
        super().__init__(nom, age)
        self.niveau = niveau

    def etudier(self):
        return f"Je suis en {self.niveau} et j'étudie dur !"


class Panier:
    def __init__(self, articles):
        self.articles = articles

    def __len__(self):
        return len(self.articles)

    def __getitem__(self, index):
        return self.articles[index]


class Produit:
    def __init__(self, nom, prix):
        self.nom = nom
        self.prix = prix

    def __eq__(self, autre):
        if not isinstance(autre, Produit):
            return NotImplemented
        return self.nom == autre.nom


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, autre):
        if not isinstance(autre, Point):
            return NotImplemented
        return Point(self.x + autre.x, self.y + autre.y)

    def __str__(self):
        return f"({self.x}, {self.y})"


class Livre:
    def __init__(self, titre, auteur, annee, disponible=True):
        self.titre = titre
        self.auteur = auteur
        self.annee = annee
        self.disponible = disponible

    def emprunter(self):
        if not self.disponible:
            return "Indisponible."
        self.disponible = False
        return "Livre emprunté !"

    def retourner(self):
        self.disponible = True
        return "Livre retourné."

    def __str__(self):
        disponible = "Oui" if self.disponible else "Non"
        return (
            f"Titre : {self.titre}, Auteur : {self.auteur}, "
            f"Année : {self.annee}, Disponible : {disponible}"
        )


class Roman(Livre):
    def __init__(self, titre, auteur, annee, genre, disponible=True):
        super().__init__(titre, auteur, annee, disponible)
        self.genre = genre

    def __str__(self):
        return f"{super().__str__()}, Genre : {self.genre}"


class Bibliotheque:
    def __init__(self):
        self.livres = []

    def ajouter_livre(self, livre):
        self.livres.append(livre)

    def lister_livres(self):
        return [str(livre) for livre in self.livres]

    def emprunter_livre(self, titre):
        for livre in self.livres:
            if livre.titre == titre:
                return livre.emprunter()
        return "Livre non trouvé."


def main():
    p1 = Personne("Alice", 30)
    print(p1.se_presenter())
    print(p1)

    etudiant = Etudiant("Bob", 20, "Master")
    print(etudiant.se_presenter())
    print(etudiant.etudier())

    panier = Panier(["pomme", "banane"])
    print(f"Nombre d'articles : {len(panier)}")
    print(f"Premier article : {panier[0]}")

    produit1 = Produit("Livre", 10.0)
    produit2 = Produit("Livre", 15.0)
    print(f"Les deux produits ont le même nom : {produit1 == produit2}")

    point1 = Point(1, 2)
    point2 = Point(3, 4)
    print(f"Somme des points : {point1 + point2}")

    charlie = Personne("Charlie", 25)
    del charlie

    bibliotheque = Bibliotheque()
    livre = Livre("Le Petit Prince", "Antoine de Saint-Exupéry", 1943)
    roman = Roman("Les Misérables", "Victor Hugo", 1862, "Historique")
    bibliotheque.ajouter_livre(livre)
    bibliotheque.ajouter_livre(roman)
    print(bibliotheque.emprunter_livre("Le Petit Prince"))
    for description in bibliotheque.lister_livres():
        print(description)
    print(livre.retourner())
    for description in bibliotheque.lister_livres():
        print(description)


if __name__ == "__main__":
    main()
