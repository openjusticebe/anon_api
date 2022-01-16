@fixture.api
Feature: Doc Parsing

    Scenario: The server starts and I can retrieve some info
        Given the api is available
            When I access the server root
                Then I receive some data

    Scenario: I can upload a file for extraction
        Given the api is available
            When I send a pdf text file for extraction
              Then I receive a reference
        Given I wait a bit
            When I use the reference to check file status
              Then I receive some meta data
            When I use the reference to check file status
              Then I receive the extracted text

    Scenario: I can send text and get extracted information back
        Given the api is available
          When I send some raw text with useful information
            Then I receive a response with data
            And field "year" has correct value "2020"
            And field "lang" has correct value "FR"
            And field "country" has correct value "BE"
            And field "appeal" has correct value "nodata"

