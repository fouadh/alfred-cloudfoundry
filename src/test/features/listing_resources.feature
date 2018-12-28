Feature: Listing resources hosted in Cloud Foundry

  Scenario Outline: Unauthenticated users should get an error message

    Given one <resource> named <name> is hosted on Cloud Foundry
    When John wants to list all the <resource>s
    Then the workflow should contain an item with title 'You are not identified: please provide your credentials' and no subtitle

  Examples:
    | resource    |
    | application |
    | route       |
    | service     |
    | buildpack   |

  Scenario Outline: Empty list should return an informative message

    Given no <resource> is hosted on Cloud Foundry
    When Alice wants to list all the <resource>s
    Then the workflow should contain an item with title '<expectedTitle>' and no subtitle

  Examples:
    | resource    | expectedTitle        |
    | application | No application found |
    | route       | No route found       |
    | service     | No service found     |
    | buildpack   | No buildpack found   |


  Scenario Outline: <resource>s should be retrieved with their metadata

    Given one <resource> named <name> is hosted on Cloud Foundry
    When Alice wants to list all the <resource>s
    Then the workflow should contain an item with title '<name>' and subtitle '<expectedSubtitle>'


  Examples:
    | resource    | name           | expectedSubtitle                         |
    | application | roster         | STARTED                                  |
    | route       | roster-host    |                                          |
    | service     | roster-service | This is the roster service !!!!          |
    | buildpack   | java_buildpack | java-buildpack-offline-cflinuxfs3-v4.zip |


  Scenario Outline: Applications can be filtered by their name

    Given one <resource> named <name> is hosted on Cloud Foundry
    When Alice wants to filter all the <resource>s with the string '<query>'
    Then the workflow should contain an item with title '<name>' and subtitle '<subtitle>'
    And the number of items should be <totalItems>

  Examples:
    | resource    | query          | name           |  subtitle                                | totalItems |
    | application | rost           | roster         | STARTED                                  | 1          |
    | route       | roster         | roster-host    |                                          | 1          |
    | service     | service        | roster-service | This is the roster service !!!!          | 1          |
    | buildpack   | buildpack      | java_buildpack | java-buildpack-offline-cflinuxfs3-v4.zip | 1          |
    | application | nam            | name-2431      | STOPPED                                  | 2          |