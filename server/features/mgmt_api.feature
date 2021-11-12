Feature: Management API

    Scenario: API is up and running
        When we get "/"
        Then we get OK response

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


    Scenario: Create a user
        Given empty "users"
        When we post to "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com"
        }
        """
        Then we get response code 201
        When we get "/users"
        Then we get existing resource
        """
        {
        "_items" :
            [
                {
                    "first_name": "John",
                    "last_name": "Cena",
                    "email": "johncena@wwe.com"
                }
            ]
        }
        """


    Scenario: Update a user
        Given empty "users"
        When we post to "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com"
        }
        """
        When we patch latest
        """
        {"last_name": "wick"}
        """
        Then we get updated response
        """
        {"last_name": "wick"}
        """


    Scenario: Delete a user
        Given empty "users"
        When we post to "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com"
        }
        """
        When we delete latest
        Then we get ok response



    Scenario: Create a product
        Given empty "products"
        When we post to "/products"
        """
        {
            "name": "Product1"
        }
        """
        Then we get response code 201
        When we get "/products"
        Then we get existing resource
        """
        {
        "_items" :
            [
                {
                    "name": "Product1"
                }
            ]
        }
        """


    Scenario: Update a product
        Given empty "products"
        When we post to "/products"
        """
        {
            "name": "product1"
        }
        """
        When we patch latest
        """
        {"description": "good product"}
        """
        Then we get updated response
        """
        {"description": "good product"}
        """


    Scenario: Delete a product
        Given empty "products"
        When we post to "/products"
        """
        {
            "name": "John",
            "description": "good product"
        }
        """
        When we delete latest
        Then we get ok response

