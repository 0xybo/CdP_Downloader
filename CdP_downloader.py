# importation des modules ('pip install XXX' dans le cmd pour les modules manquants)
import os
import re
import shutil
import time

import requests
import urllib3
from bs4 import BeautifulSoup

# désactivation du message d'erreur lors d'une connexion https non vérifiée
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# déclaration des variables
url = ''
data_login = {}
path = ''
forb_char = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
video_ext = ['mp4', 'avi', 'mkv']

session = requests.Session()


# # définition des fonctions
# def init():
#     """Permet d'initialiser les variables de départ url, data_login et path. Ouvre une session sur CdP."""

#     global url
#     global data_login
#     global path

#     url = input("Lien du Cahier de Prépa à télécharger (sous la forme 'https://cahier-de-prepa.fr/XXX/') :\n")
#     if url[len(url) - 1] != '/':
#         url += '/'
#     username = input("Nom d'utilisateur : ")
#     password = input("Mot de passe : ")

#     data_login = {'login': username, 'motdepasse': password, 'connexion': '1'}

#     path = input("Dossier où télécharger les fichiers (sous la forme 'C:\\XXX') :\n")
#     while not (os.path.exists(path)):
#         answer = input("Le chemin d'accès n'existe pas. Le créer ? (laisser vide pour le changer)\n")
#         if answer != '':
#             os.makedirs(path)
#         else:
#             path = input("Dossier où télécharger les fichiers (sous la forme 'C:\\XXX') :\n")

#     session.get(url, verify=False)
#     session.post(url, data=data_login, verify=False)

#     print()


# def connect(link, s):
#     """Renvoie le code source de la page en texte."""

#     r = s.get(link, verify=False)

#     if r.ok:
#         return r.text
#     else:
#         print("Problème avec l'adresse ou soucis de connexion. Veuillez réessayer : " + link)
#         exit()


def stop(s):
    """Permet de fermer la session."""

    s.close()


# def soup(r):
#     """Permet de créer une instance BS avec une page html (texte)."""

#     return BeautifulSoup(r, 'html.parser')


# def clear(c):
#     """Permet de retirer les caractères interdits par Windows de la chaîne de caractère."""

#     for i in forb_char:
#         c = c.replace(i, '')

#     return c


# def create_dir(t, p):
#     """Permet de créer un dossier pour télécharger les fichiers."""

#     t = clear(t)

#     p = os.path.join(p, t)
#     if os.path.exists(p):
#         shutil.rmtree(p, ignore_errors=True)

#     os.mkdir(p)

#     return p


# def ext_title(sp):
#     """Permet d'extraire le titre du CdP"""

#     return sp.find('title').text


# def ext_subjects(sp):
#     """Permet d'extraire les matières du CdP + leur lien | leur path Windows"""

#     out = {}
#     nav = sp.find('div', id='menu')

#     tmp = nav.find_all('h3')
#     subjects = ['Documents à télécharger']
#     subjects = subjects + [tmp[i].text for i in range(len(tmp))]

#     urls = nav.find_all(text=re.compile('Documents à télécharger'))
#     urls = [urls[i].parent for i in range(len(urls))]
#     urls = [(url + urls[i]['href']) for i in range(len(urls))]

#     for i in range(len(subjects)):
#         out[subjects[i]] = [urls[i], os.path.join(path, clear(subjects[i]))]

#     rep = " "
#     while rep != "":
#         print("Pour supprimer une matière, entrez son numéro. Pour conserver cette liste, appuyez sur Entrée :")
#         print()
#         for (i, j) in enumerate(list(out)):
#             print("- {} ({})".format(j, i+1))
#         rep = input()

#         if rep != "":
#             if 1 <= int(rep) <= len(list(out)):
#                 del out[list(out)[int(rep) - 1]]
#             else:
#                 rep = ""

#     return out


def download(link, name, ext, p, s):
    """Permet de télécharger un fichier."""

    response = s.get(link, verify=False)

    with open(p + '\\' + name + '.' + ext, 'wb') as f:
        f.write(response.content)


def extract(link, p, s):
    """Permet d'extraire les liens d'une page puis les télécharge.
    S'il s'agit d'un dossier, extrait son nom, créer le dossier et itère sur le lien nouveau lien.
    S'il s'agit d'un fichier, extrait son nom et son extension puis le télécharge"""

    pattern = r'\((.*?),'

    response = connect(link, s)
    sp = soup(response)

    section = sp.find('section')

    docs = section.find_all('p', class_='doc')
    reps = section.find_all('p', class_='rep')

    for doc in docs:
        name = clear(doc.find('span', class_='nom').text)
        donnee = doc.find('span', class_='docdonnees')
        doc_link = doc.find('a')

        sec = doc.find('span', class_='icon-minilock')

        if (doc_link and donnee) is not None and sec is None:
            ext = re.search(pattern, donnee.text).group(1)
            doc_link = url + doc_link['href']
            if ext in video_ext:
                doc_link += '&dl'
            download(doc_link, name, ext, p, s)

    for rep in reps:
        name = clear(rep.find('span', class_='nom').text)
        rep_link = rep.find('a')

        sec = rep.find('span', class_='icon-minilock')

        if rep_link is not None and sec is None:
            rep_p = create_dir(name, p)
            rep_link = url + 'docs' + rep_link['href']
            extract(rep_link, rep_p, s)


###-CODE PRINCIPAL-###

# init()

# # on extrait le code source de la page principale
# page = connect(url, session)

# # on crée une objet BS
# page_soup = soup(page)

# # on extrait le titre
# title = ext_title(page_soup)

# on crée le dossier racine du CdP + maj de path
# create_dir(title, path)
# path = os.path.join(path, clear(title))

# # on extrait toutes les matières du CdP
# subs = ext_subjects(page_soup)

# démarrage du chrono
start_time = time.time()
tmp_time = start_time

print()
print("- - - TÉLÉCHARGEMENT - - -")
print()

# extraction + téléchargement des fichiers
keys_list = list(subs)

for k in keys_list:
    os.mkdir(subs[k][1])
    extract(subs[k][0], subs[k][1], session)

    print(k + " : téléchargé ({}s)".format(round(time.time() - tmp_time, 2)))
    tmp_time = time.time()

# fin du chrono
end_time = time.time()

# fermeture de la session
stop(session)

# fin du programme
tps = end_time - start_time
tps = time.strftime('%H:%M:%S', time.gmtime(tps))

print()
print("- - - - - - - - - - - - - - - ")
print()

time.sleep(1.5)

print("Votre Cahier de Prépa a pu être téléchargé sans problème")
print("Temps total pour le téléchargement : " + tps)

'''
Pierre GIEN - Prépa MP lycée Pothier
'''
