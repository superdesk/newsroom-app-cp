Feature: Management API
    Scenario: API is up and running
        When we get "/"
        Then we get OK response

    Scenario: test auth without token
        Given empty auth token
        When we get "/"
        Then we get response code 401

        When we get "/users"
        Then we get response code 401
