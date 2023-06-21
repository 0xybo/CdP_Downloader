> ⚠️ Actuelement, cette version ne fonctionne pas, une erreur se produit lors de l'execution du programme .exe à cause de la fonction `QMessageBox.critical`.



Version du fichier `CdP_Downloader.py` présent dans le dossier parent avec les modifications:

- Retrait de l'installation automatique des modules manquants, les modules sont importés directement (lignes 57 à 122)
- Retrait du bloc `try` et ajout des lignes qu'il contient après la désactivation des messages d'erreurs (lignes 127 à 131)

Cette version est ensuite convertie en .exe grâce au module `auto-py-to-exe` utilisant `pyinstaller`.