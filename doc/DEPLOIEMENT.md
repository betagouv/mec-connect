# DEPLOIEMENT

- mettre à jour la branche `main`
```bash
git switch main
git pull
```

- obtenir le dernier numéro de version
```bash
git describe --tags --abbrev=0
```

- définir un nouveau numéro de version et créer un nouveau tag
```bash
git tag vx.x.x
```

- pousser le tag pour déclencher le déploiement
```bash
git push --tags
```

- vérifier le déploiement dans Scalingo
