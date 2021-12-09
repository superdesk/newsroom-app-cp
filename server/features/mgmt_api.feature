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


    Scenario: Get company products
		Given empty "companies"
		When we post to "/companies"
		"""
		[{"name": "zzz company"}]
		"""
        Then we get response code 201

		Given empty "products"
		When we post to "/products"
		"""
		[{
            "name": "A fishy Product",
		    "description": "a product for those interested in fish",
		    "query": "fish",
		    "product_type": "news_api"
		}]
		"""
        Then we get response code 201
    
		When we post to "companies/#companies._id#/products"
        """
        {"product_ids": ["#products._id#"]}
        """
        Then we get response code 201

		When we get "companies/#companies._id#/products"
        Then we get existing resource
		"""
        {"_items": [
            {
		        "name": "A fishy Product",
		        "description": "a product for those interested in fish",
		        "query": "fish",
		        "product_type": "news_api"
            }
        ]}
		"""
		When we delete "companies/#companies._id#/products/#products._id#"
		Then we get ok response
        
        When we get "companies/#companies._id#/products"
        Then we get existing resource
		"""
        {"_items": []}
		"""
      
        When we get "products/#products._id#"
        Then we get existing resource
		"""
        {"name": "A fishy Product"}
        """


    Scenario: manage user topics
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
        Given empty "companies"
        When we post to "/companies"
        """
        [
            {
                "name": "zzz company"
            }
        ]
        """
        Then we get response code 201
        When we post to "users/#users._id#/topics"
        """
        {
            "label": "new topic",
            "company": "#companies._id#"
        }
        """
        Then we get response code 201
        When we get "users/#users._id#/topics"
        Then we get existing resource
        """
        {
            "_items": [
                {
                    "label": "new topic",
                    "company": "#companies._id#"
                }
            ]
        }
        """
        When we delete "users/#users._id#/topics"
        Then we get ok response
        When we get "users/#users._id#/topics"
        Then we get existing resource
        """
        {
            "_items": []
        }
        """
