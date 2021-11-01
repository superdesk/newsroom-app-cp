Feature: Management API

    Scenario: API is up and running
        When we get "/"
        Then we get OK response
