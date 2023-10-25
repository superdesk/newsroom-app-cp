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
    