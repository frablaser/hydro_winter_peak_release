
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
![Ajout intégration](https://raw.githubusercontent.com/frablaser/hydro_winter_peak_release/refs/heads/main/AjoutIntergration.jpg)
    
4.  Cliquez sur le menu (3 points en haut à droite) > **Dépôts personnalisés**.
    
5.  Ajoutez l'URL de ce dépôt : `https://github.com/frablaser/hydro_winter_peak_release` 
   
6.  Catégorie : **Intégration**.
    
7.  Cliquez sur **Installer**.
    
8.  Redémarrez Home Assistant.
    

### Installation Manuelle

1.  Téléchargez le dossier `custom_components/hydro_winter_peak` depuis ce dépôt.
    
2.  Copiez ce dossier dans votre répertoire `/config/custom_components/` sur votre instance Home Assistant.

3.  Rechercher l'intégration :
	![enter image description here](https://raw.githubusercontent.com/frablaser/hydro_winter_peak_release/refs/heads/main/AjoutIntegrationSel.jpg)
    
4.  Redémarrez Home Assistant.




## ⚙️ Configuration

1.  Allez dans **Paramètres** > **Appareils et services**.
    
2.  Cliquez sur **Ajouter une intégration**.
    ![enter image description here](https://github.com/frablaser/hydro_winter_peak_release/blob/main/AjoutIntergration.jpg?raw=true)
    
3.  Recherchez **Hydro-Québec**.
    ![enter image description here](https://github.com/frablaser/hydro_winter_peak_release/blob/main/AjoutIntegrationSel.jpg?raw=true)
    

![enter image description here](https://github.com/frablaser/hydro_winter_peak_release/blob/main/AjoutIntegrationOptions.jpg?raw=true)

-   **URL de l'API :** (Laisser par défaut, sauf si vous avez un autre forfait que le Flex-D/TPC-DPC d'Hydro).

 -  **L'heure de coucher à Low (basse température)** : Le chauffage de nuit en mode ECO "Low" pour dormir plus au frais.
 
 -  **L'heure de lever (revenir à confort)** : Le chauffage reprendra à normalement à "***Confort***" cette heure.

 - **Préchauffage** : Le nombre d'heure pour préchauffer la maison avant une pointe hivernale et cesser passer à l'état "***Low***" (économique) pendant la pointe.



## Service Web Hydro-Québec (URL)
Les services Web (API) d'Hydro-Québec se trouvent sur: https://donnees.hydroquebec.com/pages/accueil/

Pour les Pointes Hivernales: https://donnees.hydroquebec.com/explore/dataset/evenements-pointe/information/

Les filtres de l'API Huwise Explore v2 utilisés par le service web d'HQ:  https://help.opendatasoft.com/apis/ods-explore-v2/#tag/Dataset/operation/getRecords

![HQ Filters](https://raw.githubusercontent.com/frablaser/hydro_winter_peak_release/refs/heads/main/HQFiltersjpg.jpg)

L'URL que j'ai créée, va filtrer à partir de maintenant les présentes et prochaines pointes hivernales, cela à le grand avantage à réduire énormément la quantité de données à recevoir  et à ne voir que ce qui nous importe vraiment:
https://donnees.hydroquebec.com/api/explore/v2.1/catalog/datasets/evenements-pointe/records?where=datedebut%3E%3Dnow(hours%3D-2)%20or%20datefin%3E%3Dnow(hours%3D-0.5)&order_by=datedebut&limit=20&refine=offre%3ATPC-DPC&refine=secteurclient%3AResidentiel&timezone=America%2FNew_York

Ceci nous donnera seulement les offres : **TPC-DPC** (Tarif Flex pour la clientèle au tarif D), il vous est possible de modifier votre url pour voir toutes autres offres. 



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

## 📇 Carte par défaut (Dashboard)

![Carte par défaut](https://github.com/frablaser/hydro_winter_peak_release/blob/main/DirectInt%C3%A9gration.jpg?raw=true)
La carte par défaut est la plus simple à mettre en oeuvre... Il suffit d'aller dans : 

 - ***Paramètres*** 
 - ***Appareils et Services*** 
 - L'intégration : ***Hydro-Québec Pointes Hivernales***
 - Cliquer le lien : ***Ajouter au tableau de bord***
	 ![Ajout de la carte](https://github.com/frablaser/hydro_winter_peak_release/blob/main/Int%C3%A9grationPanneau.jpg?raw=true)

## 🎨 Carte Lovelace (Dashboard)

Pour un affichage visuel de l'état (nécessite une carte de type `Markdown`) :

YAML

```
type: markdown
title: Hydro Québec Pointes Hivenales
content: |-
  {% set etat = states('sensor.hydro_quebec_hiver_etat') %}
  {% set debut = states('sensor.hydro_quebec_hiver_debut_pointe') %}
  {% set fin = states('sensor.hydro_quebec_hiver_fin_pointe') %}
  {% set prochain = states('sensor.hydro_quebec_hiver_prochaine_pointe') %}
  <center>
  {% if etat == 'Confort' %}
    <font color="green"><ha-icon icon="mdi:sofa" style="color: green; --mdc-icon-size: 60px;"></ha-icon>
    <h1 style="color: green;">MODE CONFORT</h1></font>
    Chauffage normal autorisé.
  {% elif etat == 'OverHeat' %}
    <font color="red"><ha-icon icon="mdi:fire" style="color: red; --mdc-icon-size: 60px;"></ha-icon>
    <h1 style="color: red;">PRÉCHAUFFAGE</h1></font>
    Augmentation de la consigne !
  {% elif etat == 'Low' %}
    <font color="blue"><ha-icon icon="mdi:snowflake" style="color: deepskyblue; --mdc-icon-size: 60px;"></ha-icon>
    <h1 style="color: deepskyblue;">RÉDUCTION (LOW)</h1></font>
    <b>Pointe ou Nuit :</b> Consigne réduite.
  {% else %}
    <h1>{{ etat }}</h1>
  {% endif %}
  ----------------------------------------------
  {% if etat != 'Confort' and debut not in ['unknown', 'unavailable', 'None'] %}
  **⚠️ Événement en cours :**
  * **Fin prévue :** {{ as_timestamp(fin) | timestamp_custom('%H:%M', true) }}
  {% endif %}
  **📅 Prochain événement :** {{ prochain }}
  </center>


```

## ⚠️ Avertissement

Cette intégration n'est pas affiliée à Hydro-Québec. Elle utilise les données ouvertes disponibles publiquement. Utilisez-la à vos propres risques. Assurez-vous que vos systèmes de chauffage sont sécuritaires pour les températures de consigne utilisées.

----------

_Développé avec ❤️ au Québec._

----------

