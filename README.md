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

### 1. Endpoints des paiements de masse

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

### 3. Endpoints des groupes de bénéficiaires

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

📥 Télécharger un exemple de fichier CSV
Vous pouvez télécharger un fichier CSV d'exemple pour tester l'importation de bénéficiaires :
[Télécharger le fichier CSV d'exemple](recipients.csv)




    API ENDPOINTS:

    User Endpoints:
    GET /api/users/ - List all users
    POST /api/users/ - Create a new user
    GET /api/users/{id}/ - Retrieve a specific user
    PUT /api/users/{id}/ - Update a user
    PATCH /api/users/{id}/ - Partially update a user
    DELETE /api/users/{id}/ - Delete a user

    Account Endpoints:
    GET /api/accounts/ - List all accounts
    POST /api/accounts/ - Create a new account
    GET /api/accounts/{account_number}/ - Retrieve a specific account
    PUT /api/accounts/{account_number}/ - Update an account
    PATCH /api/accounts/{account_number}/ - Partially update an account
    DELETE /api/accounts/{account_number}/ - Delete an account
    GET /api/accounts/{account_number}/mass_payments/ - Get mass payments for a specific account

    Bank Provider Endpoints:
    GET /api/bank-providers/ - List all bank providers
    POST /api/bank-providers/ - Create a new bank provider
    GET /api/bank-providers/{bank_code}/ - Retrieve a specific bank provider
    PUT /api/bank-providers/{bank_code}/ - Update a bank provider
    PATCH /api/bank-providers/{bank_code}/ - Partially update a bank provider
    DELETE /api/bank-providers/{bank_code}/ - Delete a bank provider

    Mass Payment Endpoints
    GET /api/mass-payments/ - List all mass payments
    POST /api/mass-payments/ - Create a new mass payment
    GET /api/mass-payments/{id}/ - Retrieve details of a specific mass payment

    Payment Templates Endpoints:
    • POST /api/payment-templates - Créer un nouveau template de paiement
    • GET /api/payment-templates - Lister tous les templates de paiement
    • GET /api/payment-templates/{template_id} - Récupérer un template de paiement
    spécifique
    • PUT /api/payment-templates/{template_id} - Mettre à jour un template de paiement
    • DELETE /api/payment-templates/{template_id} - Supprimer un template de paiement