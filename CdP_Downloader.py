"""

===============================================================================
=                        Cahier de Prepa Downloader                           =
=                               De Albatros                                   =
=                     Basé sur cdpDumpingUtils de Azuxul                      =
=                                   v1.0                                      =
===============================================================================

- Github: https://github.com/0xybo/CdP_Downloader
- Github du projet initial: https://github.com/Azuxul/cahier-de-prepa-downloader
"""

"""
MIT License

Copyright (c) 2022 Alban G. Albatros

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# ============================== CONFIGURATION ================================

# Pré-remplissage (optionnel)
#  - Lien du cahier de prepa
pre_url = ""
#  - Chemin du dossier de téléchargement
pre_path = "download"
#  - Nom d'utilisateur
pre_user = ""
#  - Mot de passe
pre_password = ""
#  - Retélécharge tous les fichiers
pre_downloadAgain = False

# =========================== FIN DE CONFIGURATION ============================

# Installe les modules nécessaires


def installModules():
    from subprocess import Popen
    from sys import executable
    for i in ["requests", "bs4", "urllib3", "Pyside6"]:
        Popen([executable, "-m", "pip", "install", i]).wait()
        print(" => Module " + i + " installé")


try:
    # Importation des modules
    from requests import session
    from bs4 import BeautifulSoup
    from re import compile, search
    from os import path as osPath, mkdir, getcwd
    from time import time
    from datetime import datetime
    from urllib3 import disable_warnings, exceptions
    from urllib.request import urlopen
    from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QLineEdit, QCheckBox, QGridLayout, QPushButton, QPlainTextEdit, QSplitter, QProgressBar, QMessageBox, QTreeWidget, QTreeWidgetItem
    from PySide6.QtGui import QIcon, QPixmap, Qt
    from PySide6.QtCore import QThread, QObject, Signal
except ImportError:
    # Si un des modules ne peut pas être importé
    try:
        from tkinter.messagebox import askyesno, showerror, showinfo
    except ImportError:
        # Si le module tkinter n'est pas installé
        def done(): return print("Modules installés")

        def error(err):
            print("Une erreur s'est produite ... \n\n"+str(err))
            input("Appuyer sur entrer pour quitter...")

        def askInstall():
            print("Un ou plusieurs modules sont manquant, voulez vous les installer ? [o/n]")
            return input("? ") == "o"
    finally:
        # Si le module tkinter est installé
        def done(): return showinfo(title="Installer des modules", message="Modules installés")

        def error(err):
            showerror(title="Installer des modules", message="Une erreur s'est produite ..., Le programme va s'arrêter \n\n"+str(err))

        def askInstall(): return askyesno(title="Installer les modules", message="Un ou plusieurs modules sont manquant, voulez vous les installer ?")

    if askInstall():
        try:
            installModules()
            done()
            # Réimporte les modules
            from requests import session
            from bs4 import BeautifulSoup
            from re import compile, search
            from os import path as osPath, mkdir, getcwd
            from time import time
            from datetime import datetime
            from urllib3 import disable_warnings, exceptions
            from urllib.request import urlopen
            from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QLineEdit, QCheckBox, QGridLayout, QPushButton, QPlainTextEdit, QSplitter, QProgressBar, QMessageBox, QTreeWidget, QTreeWidgetItem
            from PySide6.QtGui import QIcon, QPixmap, Qt
            from PySide6.QtCore import QThread, QObject, Signal
        except BaseException as err:
            error(err)
            exit()
    else:
        exit()

# Désactive les messages d'alerte inutiles
disable_warnings(exceptions.InsecureRequestWarning)
# Définit un nom pour le processus pour permettre l'affichage de l'icon
try:
    from ctypes import windll
    windll.shell32.SetCurrentProcessExplicitAppUserModelID("Oxybo.CdP_Downloader")
except ImportError:
    pass


class App(QApplication):
    def __init__(self):
        super().__init__()

        # Définition de la fenêtre principale
        self.window = QMainWindow()
        # Définition de l'icon à partir de l'URI à la fin du fichier
        self.iconUri = iconUri
        data = urlopen(self.iconUri).read()
        self.iconPixmap = QPixmap()
        self.iconPixmap.loadFromData(data)
        self.icon = QIcon(self.iconPixmap)
        self.setWindowIcon(self.icon)
        # Définition du titre de la fenêtre
        self.window.setWindowTitle("CdP Downloader")

        # Définition de la mise en page => fenêtre séparé en 2 verticalement
        self.main = QSplitter(Qt.Vertical)

        # Définition de la première partie de la fenêtre => Le détail du téléchargement
        self.output = Output(self)
        self.main.addWidget(self.output)

        # Défintition de la deuxième partie de la fenètre => Le résumé du téléchargement notamment la barre de progression
        self.infos = Infos(self)
        self.main.addWidget(self.infos)

        self.main.setSizes([1000, 1])
        self.window.setCentralWidget(self.main)
        self.window.showMaximized()

        # Demande le lien du cahier de prépa, le chemin du dossier de téléchargement, le nom d'utilisateur (optionnel) et le mot de passe (optionnel)
        self.input = Input(self)
        self.input.show()

        self.exec()

    # Exécuté par la class Input => récupère les paramètres de téléchargement
    def start(self, url: str, path: str, username: str, password: str, downloadAgain: bool):
        self.url = url
        self.path = path
        self.username = username
        self.password = password
        self.downloadAgain = downloadAgain

        # Ouverture une session de navigation avec Requests
        self.session = session()
        self.session.get(url, verify=False)
        self.session.post(url, data={'login': username, 'motdepasse': password, 'connexion': '1'}, verify=False)

        # Récupèration des informations de la page principale
        self.page_soup = BeautifulSoup(self.connect(self.url + "/docs"), 'html.parser')
        self.title = BeautifulSoup(self.connect(self.url), 'html.parser').find('title').text

        self.downloadPath = self.createDir(self.path, self.title)
        self.links = []

        subjects = self.subjects()
        self.select = Selection(self, subjects)
        self.select.show()

    # Créé un dossier si celui-ci n'existe pas déjà
    def createDir(self, path, title):
        p = osPath.join(path, self.clear(title))
        if osPath.exists(p):
            pass
        else:
            mkdir(p)
        return p

    # Permet de créer des fichiers sans obtenir d'erreur à cause d'un nom contenant des caractères interdits
    def clear(self, text):
        for i in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            text = text.replace(i, '')
        return text

    # Récupère des différentes matières sur la page principale
    def subjects(self):
        out = {}
        subjects = self.page_soup.find_all("p", class_="rep")
        subjects = [subjects[i].find("a") for i in range(len(subjects))]

        for i in range(len(subjects)):
            out[subjects[i].text] = [self.url + "/docs" + subjects[i]["href"], osPath.join(self.downloadPath, self.clear(subjects[i].text))]

        return out

    # Récupère une page à partir du lien de celle-ci
    def connect(self, link):
        r = self.session.get(link, verify=False)
        if r.ok:
            return r.text
        else:
            QMessageBox.critical(title="Erreur de connection", message="Un problème avec l'adresse ou un soucis de connexion s'est produit . Veuillez réessayer : " + link)
            exit()

    # Executé par la class Selection
    def startDownload(self, subs):
        self.start_time = time()
        # Permet de récupérer le temps d'execution des téléchargements
        self.tmp_time = self.start_time
        # Permet de donner la taille totale téléchargée
        self.fullSize = 0
        # Permet de suivre la progression du téléchargement
        self.fileCounter = 0

        # Liste des matières
        self.subjects = subs
        for k in list(self.subjects):
            if not osPath.exists(self.subjects[k][1]):
                mkdir(self.subjects[k][1])
            # Récupère les dossiers et fichiers de la matière
            self.extract(subs[k][0], subs[k][1])
            d_time = time() - self.tmp_time
            unit = (86400 if (d_time / (86400)) > 0.5 else
                    3600 if (d_time / (3600)) > 0.5 else
                    60 if (d_time / 60) > 0.5 else
                    1)
            self.output.print("📜 Liens de téléchargement récupérés (" + str(round(d_time/unit, 2)) + (
                ' Jours' if unit == 86400 else
                ' Heures' if unit == 3600 else
                ' Minutes' if unit == 60 else
                ' Secondes')+") : "+k)
            self.tmp_time = time()

        # Démarre le téléchargement dans un processus parallèle pour éviter un bloquage de l'interface du à l'attente du téléchargement
        self.linksLenght = len(self.links)
        if self.linksLenght != 0:
            self.downloadThread = QThread()
            self.download = Download(self.links, self.session)
            self.downloadThread.started.connect(self.download.run)
            self.download.finished.connect(self.downloadDone)
            self.download.progress.connect(self.downloadProgress)
            self.download.started.connect(self.downloadStarted)
            self.download.error.connect(self.downloadError)
            self.download.moveToThread(self.downloadThread)
            self.downloadThread.start()
        else:
            self.downloadDone()

    # Récupère les fichiers dans un dossier et ses sous dossiers
    def extract(self, link, path):
        pattern = r'\((.*?),'

        sp = BeautifulSoup(self.connect(link), "html.parser")

        section = sp.find('section')

        recents = section.find("h3", text="Documents récents")
        if(recents):
            docs = recents.find_previous_siblings('p', class_='doc')
            reps = section.find_all('p', class_='rep')
        else :
            docs = section.find_all('p', class_='doc')
            reps = section.find_all('p', class_='rep')

        # Dans le cas d'un fichier
        for doc in docs:
            name = self.clear(doc.find('span', class_='nom').text)
            donnee = doc.find('span', class_='docdonnees')
            doc_link = doc.find('a')

            sec = doc.find('span', class_='icon-minilock')

            if (doc_link and donnee) is not None and sec is None:
                ext = search(pattern, donnee.text).group(1)
                doc_link = self.url + doc_link['href']
                if ext in ['mp4', 'avi', 'mkv']:
                    doc_link += '&dl'
                # Teste si le fichier est déjà téléchargé et si le programme doit le retélécharger
                if not osPath.exists(path + '\\' + name + '.' + ext) or self.downloadAgain:
                    self.output.print("🔗 Nouveau lien : " + path + '\\' + name + '.' + ext + " (" + doc_link + ")")
                    self.links.append({"link": doc_link, "name": name, "ext": ext, "path": path})
                    self.infos.updateFoundFiles()
                else:
                    self.output.print("📄 Fichier extiste déjà : "+path + '\\' + name + '.' + ext)

        # Dans le cas d'un dossier
        for rep in reps:
            name = self.clear(rep.find('span', class_='nom').text)
            rep_link = rep.find('a')

            sec = rep.find('span', class_='icon-minilock')

            if rep_link is not None and sec is None:
                rep_path = self.createDir(path, name)
                rep_link = self.url + 'docs' + rep_link['href']
                # Relance l'extraction des fichiers pour le dossier courant
                self.extract(rep_link, rep_path)

    # Exécuté par la class Download quand un fichier a été téléchargé
    def downloadProgress(self, size):
        unit = (1000000000 if (size / (1000000000)) > 0.5 else
                1000000 if (size / (1000000)) > 0.5 else
                1000 if (size / (1000)) > 0.5 else
                1)
        d_time = round(time()-self.tmp_time, 2)
        self.output.print(
            "✅ Fichier téléchargé : (" + str(d_time) +
            "s / "+(str(round(size / unit, 2)) + (" Go" if unit == 1000000000 else
                                                  " Mo" if unit == 1000000 else
                                                  " Ko" if unit == 1000 else
                                                  " o"))+")"
        )
        self.fileCounter += 1
        self.fullSize += size
        self.infos.newFile()

    # Exécuté par la class Download quand un fichier va être téléchargé
    def downloadStarted(self, path):
        self.output.print(f"⬇️ Téléchargement de : "+path+" ...")
        self.tmp_time = time()

    # Executé par la class Download quand tous les fichiers ont été téléchargé
    def downloadDone(self):
        self.end_time = time()

        d_time = round(self.end_time - self.start_time, 2)

        sizeUnit = (1000000000 if (self.fullSize / (1000000000)) > 0.5 else
                    1000000 if (self.fullSize / (1000000)) > 0.5 else
                    1000 if (self.fullSize / (1000)) > 0.5 else
                    1)
        timeUnit = (86400 if (d_time / (86400)) > 0.5 else
                    3600 if (d_time / (3600)) > 0.5 else
                    60 if (d_time / 60) > 0.5 else
                    1)

        time_ = str(round(d_time / timeUnit, 2)) + (
            ' Jours' if timeUnit == 86400 else
            ' Heures' if timeUnit == 3600 else
            ' Minutes' if timeUnit == 60 else
            ' Secondes')
        size = str(round(self.fullSize / sizeUnit, 2)) + (
            ' Go' if sizeUnit == 1000000000 else
            ' Mo' if sizeUnit == 1000000 else
            ' Ko' if sizeUnit == 1000 else
            ' o')

        self.output.print(f"💯 Téléchargement terminé ({time_} / {size})")
        self.infos.progress.setValue(100)
        with open(self.downloadPath + "/infos.txt", "w", encoding="utf-8") as f:
            now = datetime.now()
            f.write("\n".join([
                f"==================================================",
                f"=                 CdP Downloader                 =",
                f"=                   By Alban G.                  =",
                f"==================================================",
                f"",
                f"Dernière mise à jour : {str(now.day)}/{str(now.month)}/{str(now.year)} {str(now.hour)}:{str(now.minute)}:{str(now.second)}",
                f"Temps écoulé : {time_}",
                f"Données téléchargées : {size}"
            ]))

    # Exécuté par la class Download quand il y a une erreur de téléchargement
    def downloadError(self):
        self.output.print("❌ Erreur de téléchargement ("+str(round(time()-self.app.tmp_time, 2))+"s / 0 o)")

    # Arrête le programme si la fenêtre est fermée
    def closeEvent(self, *args, **kwargs):
        exit()

# Permet de télécharger tous les fichiers


class Download(QObject):
    finished = Signal()
    progress = Signal(int)
    started = Signal(str)
    error = Signal()

    def __init__(self, links, session):
        super().__init__()
        self.links = links
        self.session = session

    def run(self):
        link = self.links[0]["link"]
        name = self.links[0]["name"]
        ext = self.links[0]["ext"]
        path = self.links[0]["path"]
        self.links.pop(0)

        self.started.emit(path+"\\"+name + "." + ext)
        try:
            response = self.session.get(link, verify=False)
            with open(path + '\\' + name + '.' + ext, 'wb') as f:
                f.write(response.content)
            size = len(response.content)
            self.progress.emit(size)
        except:
            self.error.emit()
        if len(self.links) > 0:
            self.run()
        else:
            self.finished.emit()


# Récolte les paramètres
class Input(QWidget):
    def __init__(self, app: App):
        super().__init__()
        self.app = app
        self._layout = QGridLayout()
        self.setWindowTitle("Paramètres")
        self.setMinimumWidth(600)

        self.WUrl = QLineEdit()
        self.WUrl.setPlaceholderText("Lien du cahier de prepa (ex: https://cahier-de-prepa.fr/bcpst")
        self.WUrl.setText(pre_url)
        self.WUrl.returnPressed.connect(self.submit)

        self.WPath = QLineEdit()
        self.WPath.setPlaceholderText("Chemin du dossier de téléchargement")
        self.WPath.setText(pre_path)
        self.WPath.returnPressed.connect(self.submit)

        self.WUsername = QLineEdit()
        self.WUsername.setPlaceholderText("Utilisateur")
        self.WUsername.setText(pre_user)
        self.WUsername.returnPressed.connect(self.submit)

        self.WPassword = QLineEdit()
        self.WPassword.setPlaceholderText("Mot de passe")
        self.WPassword.setEchoMode(QLineEdit.Password)
        self.WPassword.setStyleSheet('lineedit-password-character: 9679')
        self.WPassword.setText(pre_password)
        self.WPassword.returnPressed.connect(self.submit)

        self.downloadAgain = QCheckBox()
        self.downloadAgain.setText("Remplacer les fichiers existants")
        self.downloadAgain.setChecked(bool(pre_downloadAgain))

        self.WSubmit = QPushButton("Valider")
        self.WSubmit.clicked.connect(self.submit)

        self._layout.addWidget(self.WUrl, 0, 0)
        self._layout.addWidget(self.WPath, 1, 0)
        self._layout.addWidget(self.WUsername, 2, 0)
        self._layout.addWidget(self.WPassword, 3, 0)
        self._layout.addWidget(self.downloadAgain, 4, 0)
        self._layout.addWidget(self.WSubmit, 5, 0)

        self.setLayout(self._layout)

    def closeEvent(self, *args, **kwargs):
        exit()

    def submit(self):
        url = self.WUrl.text()
        path = self.WPath.text()
        username = self.WUsername.text()
        password = self.WPassword.text()
        if not path:
            path = getcwd()
            self.destroy(True)
        elif not osPath.exists(path):
            QMessageBox.critical(self, "Erreur", "Le chemin du dossier de téléchargement ne pointe vers rien")
        else:
            self.destroy(True)
        self.app.start(url, path, username, password, self.downloadAgain.isChecked())


class Infos(QWidget):
    def __init__(self, app: App):
        super().__init__()
        self.app = app
        self._layout = QGridLayout()
        self.progress = QProgressBar()
        # Définit le minimum et le maximum de la barre de progression pour l'utiliser avec des pourcentages
        self.progress.setRange(0, 100)
        # Définit la progression au minimum pour que la barre de soit pas vide
        self.progress.setValue(0)

        self.foundFiles = QTreeWidgetItem(["Fichiers trouvés", "0"])
        self.files = QTreeWidgetItem(["Fichiers téléchargés", "0"])
        self.data = QTreeWidgetItem(["Données téléchargées", "0 o"])
        self.time = QTreeWidgetItem(["Temps écoulé", "0 s"])
        self.speed = QTreeWidgetItem(["Vitesse de téléchargement", "0 o/s"])

        self.table = QTreeWidget()
        self.table.setHeaderLabels(["Nom", "Valeur"])
        self.table.setColumnCount(2)
        self.table.resizeColumnToContents(0)
        self.table.addTopLevelItem(self.foundFiles)
        self.table.addTopLevelItem(self.files)
        self.table.addTopLevelItem(self.data)
        self.table.addTopLevelItem(self.time)
        self.table.addTopLevelItem(self.speed)
        self.table.resizeColumnToContents(0)

        self._layout.addWidget(self.progress)
        self._layout.addWidget(self.table)
        self.setLayout(self._layout)
        self.setMinimumHeight(170)

    def newFile(self):
        fullSizeUnit = (1000000000 if (self.app.fullSize / 1000000000) > 1 else
                        1000000 if (self.app.fullSize / 1000000) > 1 else
                        1000 if (self.app.fullSize / 1000) > 1 else
                        1)
        d_fullTime = time() - self.app.start_time
        fullTimeUnit = (86400 if (d_fullTime / 86400) > 1 else
                        3600 if (d_fullTime / 3600) > 1 else
                        60 if (d_fullTime / 60) > 1 else
                        1)
        speedUnit = (1000000000 if (self.app.fullSize / d_fullTime / 1000000000) > 1 else
                     1000000 if (self.app.fullSize / d_fullTime / 1000000) > 1 else
                     1000 if (self.app.fullSize / d_fullTime / 1000) > 1 else
                     1)
        self.files.setText(1, str(self.app.fileCounter))
        self.data.setText(1, str(round(self.app.fullSize / fullSizeUnit, 2)) + (
            ' Go' if fullSizeUnit == 1000000000 else
            ' Mo' if fullSizeUnit == 1000000 else
            ' Ko' if fullSizeUnit == 1000 else
            ' o'))
        self.time.setText(1, str(round(d_fullTime / fullTimeUnit, 2)) + (
            ' Jours' if fullTimeUnit == 86400 else
            ' Heures' if fullTimeUnit == 3600 else
            ' Minutes' if fullTimeUnit == 60 else
            ' Secondes'
        ))
        self.speed.setText(1, str(round(self.app.fullSize / d_fullTime / speedUnit, 2)) + (
            ' Go/s' if fullSizeUnit == 1000000000 else
            ' Mo/s' if fullSizeUnit == 1000000 else
            ' Ko/s' if fullSizeUnit == 1000 else
            ' o/s'
        ))
        self.progress.setValue(int(self.app.fileCounter/self.app.linksLenght*100))

    def updateFoundFiles(self):
        self.foundFiles.setText(1, str(len(self.app.links)))


class Output(QPlainTextEdit):
    def __init__(self, app: App):
        super().__init__()
        self.app = app
        # Empêche la modification
        self.setReadOnly(True)
        self.appendPlainText("📢 Bienvenue !")

    # Ajoute une ligne de texte dans la fenêtre
    def print(self, *text):
        self.appendPlainText(" ".join([str(i) for i in text]))
        # Défile la fenêtre jusqu'en bas
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        self.app.processEvents()

    # Arrête le programme si la fenêtre est fermée
    def closeEvent(self, *args, **kwargs):
        exit()

# Permet la séléction des matières à télécharger, éxécute ensuite la fonction startDownload de l'application


class Selection(QWidget):
    def __init__(self, app: App, out: dict):
        super().__init__()
        self.out = out
        self.app = app
        self._layout = QGridLayout()
        self.checkBoxes = []
        self.setWindowTitle("Sélection")
        self.setMinimumWidth(600)

        # Botton correspondant aux différentes matières
        for (i, j) in enumerate(list(out)):
            checkBox = QCheckBox()
            checkBox.setText(j)
            self.checkBoxes.append(checkBox)
            self._layout.addWidget(checkBox)

        # Valide la séléction de matières
        self.WSubmit = QPushButton("Valider")
        self.WSubmit.clicked.connect(self.submit)
        # Valide toutes les matières
        self.WSelectAll = QPushButton("Tout sélectionner")
        self.WSelectAll.clicked.connect(self.submitAll)
        # Quit le programme
        self.WCancel = QPushButton("Annuler")
        self.WCancel.clicked.connect(quit)

        self._layout.addWidget(self.WSelectAll)
        self._layout.addWidget(self.WCancel)
        self._layout.addWidget(self.WSubmit)
        self.setLayout(self._layout)

    # Valide la séléction de matières
    def submit(self):
        out = {}
        for i in self.checkBoxes:
            if i.isChecked():
                out[i.text()] = self.out[i.text()]
        self.destroy(True)
        self.app.startDownload(out)

    # Valide toutes les matières
    def submitAll(self):
        self.destroy(True)
        self.app.startDownload(self.out)

    # Arrête le programme si la fenêtre est fermée
    def closeEvent(self, *args, **kwargs):
        exit()


# Icon pour la fenêtre de l'application
iconUri = "data:image/png;base64,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UwFF5NhUAIg0j81AEBhtIlgkEuH9ZUtYuXIZF5w/lNat25gI22g7d5Zx68QJTHnpBSIRo+vz/hP4m8mAInJsWgQo0rz+AnzbZMDsbC/jr7mR7z3wI9q3j+9Wwaqqg/z3355hyovPEQwGTYefgtXeV0SagQoAkeblBeYBI00Hzs9vwU033s4NN9xGzyKzBwftKNvO69Om8uo/plBXV2s09hFLgG8CzhsQiEijqAAQaX7tgBXA6fEInpGRwQUXDOXyS69m+PCRts8O2L17J++9v5i3577BqlXLicXi1nl3K1YnxYPxuoCIfJ0KABF39AaWA4XxvlDPol6cffY59O7dl9N6nU6nTl3Iz29BixYtAaitraGurpbKynK2l5ZQUrKFtetWU1bWLD139gMXAsa2EIiIiCS6AVjfemNp+joMnOv4pygiIpKEhgA1uD8YN/erDig28PMTERFJWqOxDr9xe1BurlcQ65Q/ERGRtDcWqML9wTner0MYOgtBREQkVfTGWhHv9iAdr1cp0M/YT0tERCSFFABLcX+wNv1aAcT3lCIREZEklwv8Bojg/sDt9BUBngKO3UNYREREvmYI8CnuD+J2X6XARaZ/KCIiIumgBfAnIIz7A3pjX2Hgj0B+HH4eIiIiaeUMYBpWu1y3B/gTvRZiHXAkIiIiBg3Gapzj9kD/76/FwAVx/P8WERERrO10vwIO4N6gfxh4DhgY5/9XERER+TctgLuwngo0EP9BP4j1bf9ONMcvIiKSEFoCVwHPYnXXMzXob8VaiDgOq+AQkRSgdsAiqasl1uLB/kf+2RNoc+TV6sifA1RjNSSqOvIqBTYDG4EtR/5MRERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERERE5N/8f0UzglICHSnOAAAAAElFTkSuQmCC"

App()
