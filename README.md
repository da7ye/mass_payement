# mass_payement
Microservice de Paiements de Masse pour Next.mr


# Documentation de l'API de l'Application de Paiement de Masse

Cette documentation se concentre sur les points d'accès de l'API et fournit des exemples JSON pour les tests.

## URL de base
Tous les points d'accès sont relatifs à l'URL de base :

```
http://localhost:8000/api/
```

---

## Endpoints


### 1. Endpoints des groupes de bénéficiaires

#### Lister tous les groupes de bénéficiaires
**GET** `/recipient-groups/`


#### Créer un groupe de bénéficiaires
**POST** `/recipient-groups/`

**Exemple de requête :**

```json
{
  "name": "Groupe 1",
}
```

#### Récupérer un groupe de bénéficiaires spécifique
**GET** `/recipient-groups/{id}/`


#### Ajouter un bénéficiaire à un groupe
**POST** `/recipient-groups/{id}/add_recipient/`

**Exemple de requête :**

```json
{
  "phone_number": "20593670",
  "bank_code": "SEDAD",
  "default_amount": "300.00",
  "motive": "Salary"
}
```

#### Créer un paiement de masse à partir d'un groupe
**POST** `/recipient-groups/{id}/create_mass_payment/`

**Exemple de requête :**

```json
{
  "initiator_account_number": "ACC002",
  "description": "Mars Salary(test my code update)"
}
```

#### Télécharger des bénéficiaires via un fichier CSV
**POST** `/recipient-groups/{id}/upload_recipients_csv/`

**Exemple de requête :**

```json
{
  "file": "recipients.csv"  // Téléverser un fichier CSV via form-data
}
```

📂 Exemple de fichier CSV pour l'importation des bénéficiaires
Un fichier CSV peut être utilisé pour ajouter plusieurs bénéficiaires en une seule requête. Le format attendu est le suivant :

```
phone_number,amount,motive
20593670,12000.00,Salary
42563512,5000.00
26456565,500.00
26594815,1500.00,Salaire
```

## 📥 Télécharger un exemple de fichier CSV
Vous pouvez télécharger un fichier CSV d'exemple pour tester l'importation de bénéficiaires :
[Télécharger le fichier CSV d'exemple](recipients.csv)

---

### 2. Endpoints des modèles de paiement

#### Créer un modèle de paiement
**POST** `/payment-templates/`

**Exemple de requête :**

```json
{
  "name": "Template Salaire de Paiement mentielle",
  "initiator_account_number": "ACC001",
  "recipients": [
    {
      "phone_number": "1234567890",
      "bank_code": "001",
      "default_amount": "100.00"
    },
    {
      "phone_number": "42563512",
      "bank_code": "SEDAD",
      "default_amount": 2500.00
    }
  ],
  "description": "test Payments Template"
}
```

#### Lister tous les modèles de paiement
**GET** `/payment-templates/`

#### Récupérer un modèle de paiement spécifique
**GET** `/payment-templates/{template_id}/`


#### Supprimer un modèle de paiement
**DELETE** `/payment-templates/{template_id}/`

---


### 3. Endpoints des paiements de masse

#### Lister tous les paiements de masse
**GET** `/mass-payments/`


#### Créer un paiement de masse
**POST** `/mass-payments/`

**Exemple de requête :**

```json
{
  "initiator_account_number": "ACC001",
  "recipients": [
    {
      "phone_number": "20593670",
      "bank_code": "SEDAD",
      "amount": 4500.00
    },
    {
      "phone_number": "42563512",
      "bank_code": "SEDAD",
      "amount": 2500.00
    }
  ],
  "description": "Salaire mensuel"
}
```

#### Récupérer les détails d'un paiement de masse spécifique
**GET** `/mass-payments/{id}/`



## Autres endpoints de l'API

### Endpoints des utilisateurs
- **GET** `/api/users/` - Lister tous les utilisateurs
- **POST** `/api/users/` - Créer un nouvel utilisateur
- **GET** `/api/users/{id}/` - Récupérer un utilisateur spécifique
- **PUT** `/api/users/{id}/` - Mettre à jour un utilisateur
- **PATCH** `/api/users/{id}/` - Mettre à jour partiellement un utilisateur
- **DELETE** `/api/users/{id}/` - Supprimer un utilisateur

### Endpoints des comptes
- **GET** `/api/accounts/` - Lister tous les comptes
- **POST** `/api/accounts/` - Créer un nouveau compte
- **GET** `/api/accounts/{account_number}/` - Récupérer un compte spécifique
- **PUT** `/api/accounts/{account_number}/` - Mettre à jour un compte
- **PATCH** `/api/accounts/{account_number}/` - Mettre à jour partiellement un compte
- **DELETE** `/api/accounts/{account_number}/` - Supprimer un compte
- **GET** `/api/accounts/{account_number}/mass_payments/` - Récupérer les paiements de masse d'un compte spécifique

### Endpoints des fournisseurs bancaires
- **GET** `/api/bank-providers/` - Lister tous les fournisseurs bancaires
- **POST** `/api/bank-providers/` - Créer un nouveau fournisseur bancaire
- **GET** `/api/bank-providers/{bank_code}/` - Récupérer un fournisseur bancaire spécifique
- **PUT** `/api/bank-providers/{bank_code}/` - Mettre à jour un fournisseur bancaire
- **PATCH** `/api/bank-providers/{bank_code}/` - Mettre à jour partiellement un fournisseur bancaire
- **DELETE** `/api/bank-providers/{bank_code}/` - Supprimer un fournisseur bancaire
