Feature: Listing routes hosted in Cloud Foundry

#Scenario: Empty list should return an informative message

#    Given no route is hosted on Cloud Foundry
#    When Alice wants to list all the routes
#    Then the workflow should contain an item with title 'No route found' and no subtitle


Scenario: Routes should be retrieved with their metadata

    Given one route with host name roster-host is created on Cloud Foundry
    When Alice wants to list all the routes
    Then the workflow should contain an item with title 'roster-host' and no subtitle