# mass_payement
Microservice de Paiements de Masse pour Next.mr


# Documentation de l'API de l'Application de Paiement de Masse

Cette documentation se concentre sur les points d'accès de l'API et fournit des exemples JSON pour les tests.

## URL de base
Tous les points d'accès sont relatifs à l'URL de base :

```
http://localhost:8000/api/
```

## Points d'accès

### 1. Groupes de Bénéficiaires

#### Lister tous les groupes de bénéficiaires
**GET** `/recipient-groups/`

**Réponse :**
```json
[
  {
    "id": 1,
    "name": "Groupe 1",
    "is_active": true,
    "created_at": "2023-10-01T12:00:00Z",
    "recipient_count": 5,
    "status": "complété"
  }
]
```

#### Créer un groupe de bénéficiaires
**POST** `/recipient-groups/`

**Requête :**
```json
{
  "name": "Groupe 1",
}
```

#### Récupérer un groupe de bénéficiaires
**GET** `/recipient-groups/{id}/`


#### Ajouter un bénéficiaire à un groupe
**POST** `/recipient-groups/{id}/add_recipient/`

**Requête :**
```json
{
  "phone_number": "1234567890",
  "bank_code": "001",
  "default_amount": "100.00",
  "motive": "Salaire"
}
```

#### Créer un paiement de masse à partir d'un groupe
**POST** `/recipient-groups/{id}/create_mass_payment/`

**Requête :**
```json
{
  "initiator_account_number": "1234567890",
  "description": "Salaire mensuel",
  "reference": "SALAIRE001"
}
```

### 2. Paiements de Masse

#### Lister tous les paiements de masse
**GET** `/mass-payments/`



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