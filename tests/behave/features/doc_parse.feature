@fixture.api
Feature: Doc Parsing

    Scenario: The server starts and I can retrieve some info
        Given the api is available
            When I access the server root
                Then I receive some data

    Scenario: I can upload a file for extraction
        Given the api is available
            When I send a file for extraction
                Then I receive a reference
