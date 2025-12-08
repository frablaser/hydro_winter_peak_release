
# Hydro-Québec Hiver (Gestion des Pointes)

**Hydro-Québec Pointe Hivernales** est une intégration personnalisée (Custom Component) pour Home Assistant qui permet d'automatiser la gestion du chauffage durant les événements de pointe hivernale d'Hydro-Québec (Tarification dynamique, Crédits hivernaux, Flex D).

Elle interroge l'API de données ouvertes d'Hydro-Québec et gère intelligemment les états de votre maison (Confort, Préchauffage, Réduction) sans dépendre du cloud officiel d'Hydro-Québec (Hilo/Espace Client).

## ✨ Fonctionnalités

-   **API Publique :** Récupération automatique des événements de pointe via l'API Open Data (pas besoin de mot de passe Hydro).
    
-   **Gestion du Préchauffage (OverHeat) :** Activez le chauffage _avant_ la pointe pour accumuler de la chaleur.
    
-   **Mode Nuit Automatique :** Réduit la consigne la nuit (heures configurables) si aucune pointe n'est active.
    
-   **Entièrement Configurable :** Paramétrez les durées et les heures directement via l'interface de Home Assistant.
    
-   **Indépendant :** Fonctionne localement après récupération des données JSON.
    
-   **Robuste :** Continue de fonctionner en mode "Sécurité" même si l'API est temporairement indisponible.
    

## 📦 Installation

### Via HACS (Recommandé)

1.  Assurez-vous d'avoir [HACS](https://hacs.xyz/) installé.
    
2.  Allez dans **HACS** > **Intégrations**.
    
3.  Cliquez sur le menu (3 points en haut à droite) > **Dépôts personnalisés**.
    
4.  Ajoutez l'URL de ce dépôt : `https://github.com/TON_USER_GITHUB/hydro_winter_peak` (Remplace par ton vrai lien).
    
5.  Catégorie : **Intégration**.
    
6.  Cliquez sur **Installer**.
    
7.  Redémarrez Home Assistant.
    

### Installation Manuelle

1.  Téléchargez le dossier `custom_components/hydro_winter_peak` depuis ce dépôt.
    
2.  Copiez ce dossier dans votre répertoire `/config/custom_components/` sur votre instance Home Assistant.
    
3.  Redémarrez Home Assistant.


## Service Web Hydro-Québec (URL)
Les services Web (API) d'Hydro-Québec se trouvent sur: https://donnees.hydroquebec.com/pages/accueil/

Pour les Pointes Hivernales: https://donnees.hydroquebec.com/explore/dataset/evenements-pointe/information/

Les filtres de l'API Huwise Explore v2:  https://help.opendatasoft.com/apis/ods-explore-v2/#tag/Dataset/operation/getRecords

L'URL que j'ai créée, va filtrer à partir de maintenant les présentes et prochaines pointes hivernales, cela à le grand avantage à réduire énormément la quantité de données à recevoir  et à ne voir que ce qui nous importe vraiment:
https://donnees.hydroquebec.com/api/explore/v2.1/catalog/datasets/evenements-pointe/records?where=datedebut%3E%3Dnow(hours%3D-2)%20or%20datefin%3E%3Dnow(hours%3D-0.5)&order_by=datedebut&limit=20&refine=offre%3ATPC-DPC&refine=secteurclient%3AResidentiel&timezone=America%2FNew_York

Ceci nous donnera seulement les offres : **TPC-DPC** (Tarif Flex pour la clientèle au tarif D), il vous est possible de modifier votre url pour voir toutes autres offres. 



## ⚙️ Configuration

1.  Allez dans **Paramètres** > **Appareils et services**.
    
2.  Cliquez sur **Ajouter une intégration**.
    
3.  Recherchez **Hydro-Québec Hiver**.
    
4.  Configurez vos préférences :
    
    -   **URL de l'API :** (Laisser par défaut, sauf changement d'Hydro).
        
    -   **Début mode nuit :** (Ex: `23:00`) Heure de baisse de température si aucune pointe.
        
    -   **Fin mode nuit :** (Ex: `06:00`).
        
    -   **Heures de préchauffage :** (Ex: `2`) Nombre d'heures avant le début d'une pointe pour surchauffer la maison.
        

## 🌡️ Entités et États

L'intégration crée les capteurs suivants :

**Entité**

**Description**

`sensor.hydro_quebec_hiver_etat`

L'état actuel de la gestion (voir ci-dessous).

`sensor.hydro_quebec_hiver_debut_pointe`

Date et heure du début de la prochaine (ou actuelle) pointe.

`sensor.hydro_quebec_hiver_fin_pointe`

Date et heure de la fin de la pointe.

`sensor.hydro_quebec_hiver_prochaine_pointe`

Texte lisible du prochain événement (ex: `08 Dec 06:00 à 10:00`).

### Les États possibles (`sensor.hydro_quebec_hiver_etat`)

Utilisez ces états dans vos automatisations :

-   **`Confort`** (Vert) : Aucun événement, il fait jour. Chauffage normal.
    
-   **`OverHeat`** (Rouge) : Nous sommes X heures avant une pointe. Augmentez la température (ex: +2°C ou +3°C) pour stocker de l'énergie thermique.
    
-   **`Low`** (Bleu) :
    
    -   Soit une **Pointe** est en cours (tarif élevé).
        
    -   Soit c'est la **Nuit** (mode éco).
        
    -   Action : Baissez les thermostats.
        

## 🤖 Exemple d'Automatisation

La logique de l'intégration vous retourne trois États: 
 - **Confort**, 
 - **Low**, 
 - **Overheat**

Cependant, vous pouvez ajouter des conditions, comme vérifier si vous êtes à la maison par exemple en utilisant l'application mobile Home Assistant pour savoir si vous êtes bien à la maison [*device_tracker*] et ainsi empêcher de chauffer inutilement si vous n'êtes pas à la maison. 

Voici un exemple simple pour gérer vos thermostats automatiquement :

YAML

```
alias: "Hydro - Gestion Chauffage Intelligente"
description: "Ajuste les thermostats selon les pointes et la nuit"
trigger:
  - platform: state
    entity_id: sensor.hydro_quebec_hiver_etat
action:
  - choose:
      # CAS 1 : PRÉCHAUFFAGE (Avant la pointe)
      - conditions:
          - condition: state
            entity_id: sensor.hydro_quebec_hiver_etat
            state: "OverHeat"
        sequence:
          - service: climate.set_temperature
            target:
              entity_id: climate.thermostat_salon
            data:
              temperature: 24

      # CAS 2 : ÉCONOMIE (Pendant la pointe OU la nuit)
      - conditions:
          - condition: state
            entity_id: sensor.hydro_quebec_hiver_etat
            state: "Low"
        sequence:
          - service: climate.set_temperature
            target:
              entity_id: climate.thermostat_salon
            data:
              temperature: 18

      # CAS 3 : RETOUR À la NORMALE
      - conditions:
          - condition: state
            entity_id: sensor.hydro_quebec_hiver_etat
            state: "Confort"
        sequence:
          - service: climate.set_temperature
            target:
              entity_id: climate.thermostat_salon
            data:
              temperature: 21

```

## 🎨 Carte Lovelace (Dashboard)

Pour un affichage visuel de l'état (nécessite une carte de type `Markdown`) :

YAML

```
type: markdown
title: ❄️ Hydro-Québec Hiver
content: >-
  {% set etat = states('sensor.hydro_quebec_hiver_etat') %}
  {% set prochain = states('sensor.hydro_quebec_hiver_prochaine_pointe') %}

  <center>
  {% if etat == 'Confort' %}
    <ha-icon icon="mdi:sofa" style="color: green; --mdc-icon-size: 60px;"></ha-icon>
    <h2 style="color: green;">MODE CONFORT</h2>
    Chauffage normal.
  {% elif etat == 'OverHeat' %}
    <ha-icon icon="mdi:fire" style="color: red; --mdc-icon-size: 60px;"></ha-icon>
    <h2 style="color: red;">PRÉCHAUFFAGE</h2>
    Stockage de chaleur en cours !
  {% elif etat == 'Low' %}
    <ha-icon icon="mdi:snowflake" style="color: deepskyblue; --mdc-icon-size: 60px;"></ha-icon>
    <h2 style="color: deepskyblue;">RÉDUCTION (LOW)</h2>
    Pointe active ou Nuit.
  {% else %}
    <h2>{{ etat }}</h2>
  {% endif %}
  </center>
  
  ---
  **📅 Prochain événement :** {{ prochain }}

```

## ⚠️ Avertissement

Cette intégration n'est pas affiliée à Hydro-Québec. Elle utilise les données ouvertes disponibles publiquement. Utilisez-la à vos propres risques. Assurez-vous que vos systèmes de chauffage sont sécuritaires pour les températures de consigne utilisées.

----------

_Développé avec ❤️ au Québec._

----------

