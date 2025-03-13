# mass_payement
Microservice de Paiements de Masse pour Next.mr

    TODO:
    -> the iniciator shouldnt be able to transfer money to his account


    DONE:
    ->The status of the recipiants in the POST /api/mass-payments/ endpoint still say pending when it should be saying succeess
    -> There is a endpoint for mass payement GET /api/mass-payments/ but there isnt one for each MassPayment like GET /api/mass-payments/{id}/
    -> Liste des Paiements de Masse d'un Utilisateur GET /api/accounts/{account_number}/mass-payments
    -> the 'success_count,failure_count,pendings_count' in the mass payment work but it should be indicating the reason why some of the transactions failed (they work but in "failure_reason" inside the GET /api/mass-payments/{id}/ endpoint)
    -> it should say "No user found with the provided phone number." when the phone number is not does not belong to an active account.
    -> didnt do the payement templates yet!
    ->  Done but dont know how yet! (When doing a mass payment its no getting the ammount out of the initiator's account) reponses:145services




    NOTES:
    ?: in the 'GET /api/mass-payments/' showing the status as completed but in the 'POST /api/mass-payments/ RESPONSE' showing processing.
    RESPONSE:
        This is actually the expected behavior for an asynchronous process. The POST endpoint creates the job and returns immediately with the initial status, while the background task updates the status as it processes.

        1.When you make a POST request to create a mass payment, the API returns a response immediately after creating the record, showing "status": "processing" because:

        The mass payment is created with initial status "pending"
        The process_mass_payment starts processing in a background thread
        The API response is returned before the background processing completes


        2.When you later make a GET request to view the mass payments, the processing has completed, so you see "status": "completed" because:

        The background thread had time to finish processing all payment items
        The database was updated with the final status.


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