@fixture.api
Feature: Doc Pseudonymisation

    Scenario: I can upload text for pseudonymisation
        Given the api is available
        And some example text
            When I send text file for pseudonymisation
              Then I receive a pseudonymised text
