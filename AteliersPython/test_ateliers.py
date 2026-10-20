import unittest

from AteliersPython import Partie1, Partie2


class AtelierPythonTests(unittest.TestCase):
    def test_partie_1_calculations_and_collections(self):
        self.assertEqual(Partie1.verifier_parite(4), "pair")
        self.assertEqual(Partie1.verifier_parite(7), "impair")
        self.assertEqual(Partie1.somme_de_un_a_cent(), 5050)
        self.assertEqual(
            Partie1.compter_visites(["Tunisie", "France", "Tunisie"]),
            ({"Tunisie": 2, "France": 1}, "Tunisie"),
        )
        achats = [
            {"product": "Mouse", "price": 25, "quantity": 5},
            {"product": "Mouse", "price": 25, "quantity": 2},
            {"product": "Keyboard", "price": 45, "quantity": 3},
        ]
        self.assertEqual(
            Partie1.resumer_achats(achats),
            (310, {"Mouse": 7, "Keyboard": 3}, "Mouse", {"Mouse": 175, "Keyboard": 135}),
        )

    def test_phrase_operations(self):
        result = Partie1.traiter_phrase("Python est un langage très puissant")
        self.assertEqual(result["mots"], ["Python", "est", "un", "langage", "très", "facile", "incroyable"])
        self.assertEqual(result["nombre_mots"], 7)
        self.assertEqual(result["phrase_avec_tirets"], "Python-est-un-langage-très-facile-incroyable")
        self.assertEqual(result["affichage_numerote"][0], "Mot 1 : PYTHON")

    def test_poo_examples_and_library_case_study(self):
        person = Partie2.Personne("Alice", 30)
        self.assertEqual(person.se_presenter(), "Je m'appelle Alice et j'ai 30 ans.")
        self.assertEqual(str(person), person.se_presenter())
        student = Partie2.Etudiant("Bob", 20, "Master")
        self.assertEqual(student.etudier(), "Je suis en Master et j'étudie dur !")

        basket = Partie2.Panier(["pomme", "banane"])
        self.assertEqual(len(basket), 2)
        self.assertEqual(basket[0], "pomme")
        self.assertTrue(Partie2.Produit("Livre", 10) == Partie2.Produit("Livre", 15))
        self.assertEqual(str(Partie2.Point(1, 2) + Partie2.Point(3, 4)), "(4, 6)")

        book = Partie2.Livre("Le Petit Prince", "Antoine de Saint-Exupéry", 1943)
        novel = Partie2.Roman("Les Misérables", "Victor Hugo", 1862, "Historique")
        library = Partie2.Bibliotheque()
        library.ajouter_livre(book)
        library.ajouter_livre(novel)
        self.assertEqual(library.emprunter_livre(book.titre), "Livre emprunté !")
        self.assertEqual(library.emprunter_livre(book.titre), "Indisponible.")
        self.assertEqual(len(library.lister_livres()), 2)
        self.assertIn("Genre : Historique", str(novel))
        self.assertEqual(book.retourner(), "Livre retourné.")
        self.assertEqual(library.emprunter_livre("inconnu"), "Livre non trouvé.")


if __name__ == "__main__":
    unittest.main()
