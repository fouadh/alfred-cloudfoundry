Feature: Listing services hosted in Cloud Foundry

Scenario: Empty list should return an informative message

    Given no services is hosted on Cloud Foundry
    When Alice wants to list all the services
    Then the workflow should contain an item with title 'No service found' and no subtitle


Scenario: Services should be retrieved with their metadata

    Given one service named roster-service is created on Cloud Foundry
    When Alice wants to list all the services
    Then the workflow should contain an item with title 'roster-service' and subtitle 'This is the roster service !!!!'