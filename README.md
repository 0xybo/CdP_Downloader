<div align="center">
  <h1>CdP Downloader</h1>
  <span>Programme Python de téléchargement des fichiers d'un compte sur <a href="https://cahier-de-prepa.fr/">Cahier de Prépa</a> basé sur le projet d'<a href="https://github.com/Azuxul/cahier-de-prepa-downloader">Azuxul</a>.</span>
</div>

--------

**⚠️ Ce programme n'est pas destiné à nuire à la plateforme et aux professeurs, mais à aider les étudiants.**

## Comment fonctionne le programme ?

- On commence par faire une requête d'authentification au serveur
- On charge la page de documents présente à l'URL `/docs` afin de récupérer une liste des matières
- On charge la page de documents d'une matière pour récupérer les sous-dossiers et les fichiers
- On réitère la dernière étape avec les sous-dossiers pour déterminer l'arborescence des fichiers
- On télécharge les fichiers à partir des liens récupérés

## Requis

- Python installé

## Usage

- Télécharger `CdP_Downloader.py`.
- Ouvrir une fenêtre de terminal (cmd, shell) et exécuter `python CdP_Downloader.py` ou `py CdP_Downloader.py`

## Projets similaires

- [cdpDumpingUtils](https://github.com/Azuxul/cahier-de-prepa-downloader) par Azuxul en Python
- [CDP-Parser](https://github.com/piirios/cdp-parser) par Piirios en Rust.
- [cahier_de_prepa_archiveur 1.0](https://github.com/Loatchi/cahier_de_prepa_archiveur) par Loatchi en Java (il y a aussi un projet en Python non maintenu).
