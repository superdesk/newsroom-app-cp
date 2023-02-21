Feature: Management API - Users
    Scenario: Create a user
        Given empty "users"
        And "products"
        """
        [
            {"name": "test", "query": "test"}
        ]
        """
        When we post to "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com"
        }
        """
        Then we get error 400
        When we post to "/companies"
        """
        [{"name": "zzz company"}]
        """
        Then we get response code 201
        When we post to "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena@wwe.com",
            "company": "#companies._id#",
            "user_type": "company_admin",
            "sections": {
                "wire": true
            },
            "products": [
                {"section": "wire", "_id": "#products._id#"}
            ]
        }
        """
        Then we get response code 201
        When we post to "/users"
        """
        {
            "first_name": "John",
            "last_name": "Cena",
            "email": "johncena1@wwe.com",
            "user_type": "administrator"
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
                    "email": "johncena@wwe.com",
                    "company": "#companies._id#",
                    "user_type": "company_admin",
                    "sections": {
                        "wire": true
                    },
                    "products": [
                        {"section": "wire", "_id": "__objectid__"}
                    ]
                },
                {
                    "first_name": "John",
                    "last_name": "Cena",
                    "email": "johncena1@wwe.com",
                    "user_type": "administrator"
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
            "email": "johncena@wwe.com",
            "user_type": "administrator"
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
            "email": "johncena@wwe.com",
            "user_type": "administrator"
        }
        """
        When we delete latest
        Then we get ok response