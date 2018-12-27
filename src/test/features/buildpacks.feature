Feature: Listing buildpacks hosted in Cloud Foundry

#Scenario: Empty list should return an informative message

#    Given no buildpack is available on Cloud Foundry
#    When Alice wants to list all the buildpacks
#    Then the workflow should contain an item with title 'No buildpack found' and no subtitle


Scenario: Buildpacks should be retrieved with their metadata

    Given buildpacks are installes on Cloud Foundry
    When Alice wants to list all the buildpacks
    Then the workflow should contain an item with title 'java_buildpack' and subtitle 'java-buildpack-offline-cflinuxfs3-v4.zip'