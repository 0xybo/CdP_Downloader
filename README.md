<div align="center">
  <h1>CdP Downloader</h1>
  <span>Programme Python de téléchargement des fichiers d'un compte sur <a href="https://cahier-de-prepa.fr/">Cahier de Prépa</a> basé sur le projet d'<a href="https://github.com/Azuxul/cahier-de-prepa-downloader">Azuxul</a>.</span>
</div>

--------

**⚠️ Ce programme n'est pas destiné à nuire à la plateforme et aux professeurs, mais à aider les étudiants.**

## Comment fonctionne le programme ?

- Commence par faire une requête d'authentification au serveur
- Charge la page de documents présente à l'URL `/docs` afin de récupérer une liste des matières
- Charge la page de documents d'une matière pour récupérer les sous-dossiers et les fichiers
- Réitère la dernière étape avec les sous-dossiers pour déterminer l'arborescence des fichiers
- Télécharge les fichiers à partir des liens récupérés

## Requis

- Python installé

## Usage

> Pour les utilisateurs de Windows, vous pouvez utiliser l'exécutable [`CdP_Downloader.exe`](https://github.com/0xybo/CdP_Downloader/releases/latest/download/CdP_Downloader.exe) (Il inclut Python et les librairies nécessaires à son fonctionnement, d'où sa taille, mais n'apporte rien de plus que le script Python).

- Télécharger [`CdP_Downloader.py`](https://github.com/0xybo/CdP_Downloader/releases/latest/download/CdP_Downloader.py).
- Ouvrir une fenêtre de terminal (cmd, shell) et exécuter `python CdP_Downloader.py` ou `py CdP_Downloader.py`

## Projets similaires

- [cdpDumpingUtils](https://github.com/Azuxul/cahier-de-prepa-downloader) par Azuxul en Python
- [CDP-Parser](https://github.com/piirios/cdp-parser) par Piirios en Rust.
- [cahier_de_prepa_archiveur 1.0](https://github.com/Loatchi/cahier_de_prepa_archiveur) par Loatchi en Java (il y a aussi un projet en Python non maintenu).
