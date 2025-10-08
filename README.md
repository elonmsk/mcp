# MCP Indra Variants Server

Un serveur MCP (Model Context Protocol) qui récupère les variants DBSNP associés aux gènes via l'API Indra Discovery.

## Installation

1. Créer et activer l'environnement virtuel :
```bash
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate     # Sur Windows
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

Lancer le serveur :
```bash
python server.py
```

Le serveur sera disponible sur `ws://localhost:8000`.

## Outils disponibles

- `get_variants_for_gene` : Récupère les variants DBSNP associés à un gène
  - Paramètre : `gene` (array de strings) - Tuple [namespace, id], ex: ["HGNC", "9896"]
