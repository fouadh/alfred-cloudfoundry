Feature: Listing applications hosted in Cloud Foundry
  Scenario: Unauthenticated users should get an error message

    Given one application named roster is started on Cloud Foundry
    When John wants to list all the apps
    Then the workflow should contain an item with title 'You are not identified: please provide your credentials' and no subtitle


  Scenario: Empty list should return an informative message

    Given no application is hosted on Cloud Foundry
    When Alice wants to list all the apps
    Then the workflow should contain an item with title 'No application found' and no subtitle

  Scenario: Applications should be retrieved with their metadata

    Given one application named roster is started on Cloud Foundry
    When Alice wants to list all the apps
    Then the workflow should contain an item with title 'roster' and subtitle 'STARTED'


  Scenario: Applications can be filtered by their name

    Given one application named roster is started on Cloud Foundry
    When Alice wants to filter all the apps with the string 'roster'
    Then the workflow should contain an item with title 'roster' and subtitle 'STARTED'
    And the number of items should be 1

