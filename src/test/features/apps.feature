Feature: Listing applications hosted in Cloud Foundry

  Scenario: Empty list should return an informative message

    Given no application is hosted on Cloud Foundry
    When I want to list all of them
    Then the workflow should contain an item with title 'No application found' and no subtitle

  Scenario: Applications should be retrieved with their metadata

    Given one application named roster is started on Cloud Foundry
    When I want to list all of them
    Then the workflow should contain an item with title 'roster' and subtitle 'STARTED'

