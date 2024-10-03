# DEPLOIEMENT

- Obtenir le dernier numéro de version avec la commande suivante:
```bash
git describe --tags --abbrev=0
```

- Définir un nouveau numéro de version, mettre à jour le fichier `pyproject.toml`, et merger les changements dans la branche `main`.
```
[project]
name = "mec-connect"
version = "x.x.x"
```

- Revenir sur la branche `main`, la mettre à jour, et créer un nouveau tag.
```bash
git switch main
git pull
git tag vx.x.x
```

- Pousser le tag pour déclencher le déploiement.
```bash
git push --tags
```

- Vérifier le déploiement dans Scalingo.
