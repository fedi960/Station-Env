# 🌍 Station-Environnementale

Application Flask pour la gestion d’une **station environnementale IoT** permettant :
- L’enregistrement et la gestion des utilisateurs
- La gestion des devices (ESP32, capteurs…)
- La collecte et visualisation de mesures (température, humidité, pH, etc.)
- L’affichage de graphiques en temps réel
- L’envoi d’emails de confirmation avec template

---

## 📌 Fonctionnalités

### 🔑 Authentification & Utilisateurs
- Inscription avec email et mot de passe (hashés 🔒)
- Confirmation par email via lien sécurisé
- Connexion / Déconnexion
- Changement de mot de passe
- Gestion de session utilisateur

### 🛰️ Gestion des Devices
- Enregistrement de nouveaux appareils
- Génération de **sketch Arduino téléchargeable**
- Génération d’API key en **QR code** pour faciliter la configuration

### 📊 Visualisation des Données
- Réception en temps réel des mesures depuis les capteurs
- Affichage instantané des données sous forme de graphiques dynamiques
- Historique des mesures consultable en mode "charts"

### 📧 Emailing
- Système de confirmation d’email avec **template HTML personnalisé**
- Envoi d’emails via Gmail SMTP