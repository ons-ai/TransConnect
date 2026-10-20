"""Solutions de l'Atelier Python — Partie 1 (syntaxe et structures de données)."""


def verifier_parite(nombre):
    return "pair" if nombre % 2 == 0 else "impair"


def somme_de_un_a_cent():
    total = 0
    for nombre in range(1, 101):
        total += nombre
    return total


def compter_visites(pays_visites):
    frequences = {}
    for pays in pays_visites:
        frequences[pays] = frequences.get(pays, 0) + 1
    pays_plus_visite = max(frequences, key=frequences.get) if frequences else None
    return frequences, pays_plus_visite


def resumer_achats(achats):
    montant_total = 0
    quantites = {}
    ventes_par_produit = {}

    for achat in achats:
        produit = achat["product"]
        prix = achat["price"]
        quantite = achat["quantity"]
        montant_total += prix * quantite
        quantites[produit] = quantites.get(produit, 0) + quantite
        ventes_par_produit[produit] = ventes_par_produit.get(produit, 0) + prix * quantite

    produit_plus_achete = max(quantites, key=quantites.get) if quantites else None
    return montant_total, quantites, produit_plus_achete, ventes_par_produit


def traiter_phrase(phrase):
    mots = phrase.split()
    affichage_initial = "Les mots saisis sont : {}".format(mots)
    mots.append("incroyable")
    mots = ["facile" if mot == "puissant" else mot for mot in mots]
    phrase_avec_tirets = "-".join(mots)
    affichage_final = "La nouvelle phrase est : {}".format(phrase_avec_tirets)
    affichage_numerote = [f"Mot {numero} : {mot.upper()}" for numero, mot in enumerate(mots, start=1)]
    return {
        "mots": mots,
        "affichage_initial": affichage_initial,
        "nombre_mots": len(mots),
        "phrase_avec_tirets": phrase_avec_tirets,
        "affichage_final": affichage_final,
        "affichage_numerote": affichage_numerote,
    }


def main():
    prenom = input("Quel est votre prénom ? ")
    age = int(input("Quel âge avez-vous ? "))
    print("Hello {}, you are {} years old.".format(prenom, age))

    nombre = int(input("Saisissez un nombre : "))
    print(f"{nombre} est {verifier_parite(nombre)}.")

    mot = input("Saisissez un mot : ")
    for lettre in mot:
        print(lettre)
    print(f"Somme des entiers de 1 à 100 : {somme_de_un_a_cent()}")

    notes = [12, 15, 9, 18, 14]
    print(f"Notes : {notes}")
    print(f"Moyenne : {sum(notes) / len(notes)}, maximum : {max(notes)}, minimum : {min(notes)}")

    student = {"name": "Ali", "age": 20, "study field": "computer science"}
    student["email"] = "ali@example.com"
    for cle, valeur in student.items():
        print(f"{cle} : {valeur}")

    animaux = {"cat", "dog", "bird", "cat"}
    print(f"Ensemble d'animaux (le doublon 'cat' a disparu) : {animaux}")
    personne = ("Ali", 20, "Sousse")
    for element in personne:
        print(element)

    visites = ["Tunisie", "France", "Italie", "Tunisie", "France", "Tunisie"]
    frequences, pays_plus_visite = compter_visites(visites)
    print(f"Visites par pays : {frequences}")
    print(f"Pays le plus visité : {pays_plus_visite}")

    achats = [
        {"product": "Computer", "price": 1200, "quantity": 2},
        {"product": "Mouse", "price": 25, "quantity": 5},
        {"product": "Keyboard", "price": 45, "quantity": 3},
        {"product": "Monitor", "price": 300, "quantity": 2},
        {"product": "Mouse", "price": 25, "quantity": 2},
    ]
    total, quantites, meilleur_produit, ventes = resumer_achats(achats)
    print(f"Montant total dépensé : {total}")
    print(f"Quantités par produit : {quantites}")
    print(f"Produit le plus acheté : {meilleur_produit}")
    print(f"Valeur des ventes par produit : {ventes}")

    phrase = input('Saisissez une phrase (ex. « Python est un langage très puissant ») : ')
    resultat = traiter_phrase(phrase)
    print(resultat["affichage_initial"])
    print(f"Nombre total de mots : {resultat['nombre_mots']}")
    print(resultat["affichage_final"])
    for ligne in resultat["affichage_numerote"]:
        print(ligne)


if __name__ == "__main__":
    main()
