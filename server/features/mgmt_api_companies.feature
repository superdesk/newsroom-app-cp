Feature: Management API - Companies
    Scenario: Create a company
        Given empty "companies"
        When we post to "/companies"
        """
        {
            "name": "zzz company",
            "contact_name": "zzz company",
            "country": "Iceland",
            "contact_email": "contact@zzz.com",
            "phone": "99999999"
        }
        """
        Then we get response code 201
        When we get "/companies"
        Then we get existing resource
        """
        {
        "_items" :
            [
                {
                    "name": "zzz company",
                    "contact_name": "zzz company",
                    "country": "Iceland",
                    "contact_email": "contact@zzz.com",
                    "phone": "99999999"
                }
            ]
        }
        """

    Scenario: Delete a company
       Given empty "companies"
        When we post to "/companies"
        """
        [{"name": "zzz company"}]
        """
        When we delete latest
        Then we get response code 204

    Scenario: Update a compnay
        Given empty "companies"
        When we post to "/companies"
        """
        [{"name": "zzz company"}]
        """
        When we patch latest
        """
        {"name": "xyz company"}
        """
        Then we get updated response
        """
        {"name": "xyz company"}
        """

    Scenario: Create a company with default country
        Given empty "companies"
        When we post to "/companies"
        """
        {
            "name": "zzz company",
            "contact_name": "zzz company",
            "contact_email": "contact@zzz.com",
            "phone": "99999999"
        }
        """
        Then we get response code 201
        When we get "/companies"
        Then we get existing resource
        """
        {
        "_items" :
            [
                {
                    "name": "zzz company",
                    "contact_name": "zzz company",
                    "country": "CAN",
                    "contact_email": "contact@zzz.com",
                    "phone": "99999999"
                }
            ]
        }
        """

    Scenario: Validate company products section
        Given "products"
        """
        [
            {"name": "test", "query": "test", "product_type": "agenda"}
        ]
        """

        When we post to "/companies"
        """
        {
            "name": "zzz company",
            "contact_name": "zzz company",
            "contact_email": "contact@zzz.com",
            "phone": "99999999",
            "products": [
                {"_id": "#products._id#", "section": "wire"}
            ]
        }
        """
        Then we get error 400
        """
        {"code": 400, "message": "invalid product type for product #products._id#, should be agenda"}
        """

        When we post to "/companies"
        """
        {
            "name": "zzz company",
            "contact_name": "zzz company",
            "contact_email": "contact@zzz.com",
            "phone": "99999999",
            "products": [
                {"_id": "#products._id#", "section": "agenda"}
            ]
        }
        """
        Then we get response code 201

        When we patch "/companies/#companies._id#"
        """
        {
            "products": [
                {"_id": "#products._id#", "section": "wire"}
            ]
        }
        """
        Then we get error 400

        When we patch "/companies/#companies._id#"
        """
        {
            "products": [
                {"_id": "#products._id#", "section": "agenda"}
            ]
        }
        """
        Then we get response code 200
