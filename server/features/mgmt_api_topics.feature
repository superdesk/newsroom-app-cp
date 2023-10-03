Feature: Management API - Topics
    Background: Setup companies and users
        Given empty "companies"
        When we post to "/companies"
        """
        [{"name": "zzz company"}]
        """
        Then we get response code 201
        When we post to "/users"
        """
        {
            "first_name": "Foo",
            "last_name": "Bar",
            "email": "foo@bar.org",
            "company": "#companies._id#",
            "user_type": "public"
        }
        """
        Then we get response code 201

    Scenario: Create a topic
        When we post to "/topics"
        """
        {
            "label": "topic1",
            "company": "#companies._id#",
            "topic_type": "wire",
            "query": "topic1",
            "is_global": true,
            "user": "#users._id#"
        }
        """
        Then we get response code 201
        When we get "/topics"
        Then we get existing resource
        """
        {
        "_items" :
            [
                {
                    "label": "topic1",
                    "company": "#companies._id#",
                    "topic_type": "wire",
                    "query": "topic1",
                    "is_global": true,
                    "user": "#users._id#"
                }
            ]
        }
        """

    Scenario: Delete a topic
        When we post to "/topics"
        """
        [{
            "label": "topic1",
            "company": "#companies._id#",
            "topic_type": "wire",
            "query": "topic1",
            "is_global": true,
            "user": "#users._id#"
        }]
        """
        When we delete latest
        Then we get response code 204

    Scenario: Update a topic
        When we post to "/topics"
        """
        [{
            "label": "topic1",
            "company": "#companies._id#",
            "topic_type": "wire",
            "query": "topic1",
            "is_global": true,
            "user": "#users._id#"
        }]
        """
        When we patch latest
        """
        {"label": "topic2"}
        """
        Then we get updated response
        """
        {"label": "topic2"}
        """

    Scenario: Topic with folder
        Given "topic_folders"
        """
        [
            {
                "name": "test",
                "section": "wire"
            }
        ]
        """
        Given "topics"
        """
        [
            {
                "label": "topic1",
                "company": "#companies._id#",
                "topic_type": "wire",
                "query": "topic1",
                "is_global": true,
                "user": "#users._id#",
                "folder": "#topic_folders._id#"
            }
        ]
        """
        When we get "/topics"
        Then we get list with 1 items
