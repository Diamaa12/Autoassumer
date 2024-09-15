from django.test import TestCase
import pathlib
# Create your tests here.
p = pathlib.Path.cwd()
adherer = p.parent / 'Site/static/css/aappg/adherer.css'
webflow = p.parent / 'Site/static/css/aappg/aappg.webflow.css'
import cssutils

import cssutils
from colorama import Fore, Style, init

# Initialiser colorama
init(autoreset=True)

# Fonction pour lire le contenu d'un fichier CSS
def lire_css(fichier):
    feuille_de_style = cssutils.parseFile(fichier)
    regles = {}
    for regle in feuille_de_style:
        if isinstance(regle, cssutils.css.CSSStyleRule):
            selecteur = regle.selectorText.strip()
            styles = regle.style.cssText.strip()
            regles[selecteur] = styles
    return regles

# Fonction pour comparer deux dictionnaires de règles CSS
def comparer_regles(regles1, regles2):
    differences = {}
    for selecteur, styles in regles2.items():
        if selecteur not in regles1 or regles1[selecteur] != styles:
            differences[selecteur] = styles
    return differences

# Lire les fichiers CSS
fichier1 = adherer
fichier2 = webflow
regles1 = lire_css(fichier1)
regles2 = lire_css(fichier2)

# Debug: afficher les règles lues pour les deux fichiers
print(Fore.GREEN + "Règles fichier 1:")
for selecteur, styles in regles1.items():
    print(Fore.YELLOW + f"{selecteur}: {styles}")

print(Fore.GREEN + "\nRègles fichier 2:")
for selecteur, styles in regles2.items():
    print(Fore.YELLOW + f"{selecteur}: {styles}")

# Comparer les règles et trouver les différences
differences = comparer_regles(regles1, regles2)

# Debug: afficher les différences trouvées
print(Fore.GREEN + "\nDifférences trouvées:")
for selecteur, styles in differences.items():
    print(Fore.YELLOW + f"{selecteur}: {styles}")

# Écrire les règles restantes dans un nouveau fichier CSS
fichier_sortie = 'fichier2_sans_doublons.css'
with open(fichier_sortie, 'w') as f:
    for selecteur, styles in differences.items():
        f.write(f'{selecteur} {{ {styles} }}\n')

print(Fore.GREEN + f'\nDoublons supprimés. Le fichier résultant est {fichier_sortie}.')
