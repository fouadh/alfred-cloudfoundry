alfred-cloudfoundry
===================

This workflow should work with any platform exposing the [Clound Foundry API](https://apidocs.cloudfoundry.org/5.1.0/).

Note that *version 2* of the API is used by this workflow.

# To start

1. Download and install [Cloud-Foundry.alfred3workflow](https://github.com/fouadh/alfred-cloudfoundry/raw/master/Cloud-Foundry-0.1.0.alfred3workflow)

2. Configure the endpoint and your Cloud Foundry credentials (see in the **How to use** section)

3. Enjoy !

# How to use

Type cf to get a list of all the available commands.

When a list is presented, you can search for a specific element.

For any selected resource, press **Cmd+C** and get its JSON value copied in the clipboard.

A cache per resource (applications, routes, services, ...) is used to keep the resources obtained from Cloud Foundry: it is useful when you are looking for a specific resource
in a list. The data in a cache expire after 15 seconds. 

- Setup Cloud Foundry endpoint

```
  cf setendpoint <endpoint>
```

- Setup Cloud Foundry credentials

```
  cf setcredentials <login> <password>
```

*Note:* the password is stored in the Keychain, not in clear.

- List applications

![image](./doc/images/cf-apps.gif)

- Start/Stop an application

Press **Cmd** and select an application to start (or stop) it depending on its state.

Note that starting an application may take a few moment so just be patient.

- Remove an application

Press **Shift** and select the application to remove.

- Restage an application

Press **Ctrl** and select the application to restage.

Note that this can be a lenghty operation since a droplet must be recreated on the platform.

- List routes

![image](./doc/images/cf-routes.gif)

- List services

![image](./doc/images/cf-services.gif)

- List services plans

- List services instances

![image](./doc/images/cf-services-instances.gif)

- List services bindings

- List shared domains

- List private domains

- List spaces

![image](./doc/images/cf-spaces.gif)

- List organizations

- List stacks

- List buildpacks

- List user provided services

- List service brokers

# Testing

To execute the end to end tests for this workflow:

1. Install [nodejs](https://nodejs.org/en/) (tested with version 8.12.0). You can eventually use 
[nvm](https://github.com/creationix/nvm) to manage your node version.

2. Install and run [mountebank](http://www.mbtest.org) on port 2525 (which is normally the default)

```
npm install -g mountebank
mb
```

Ports 3001 and 4001 must also be available since they are used to stub UAA and the Cloud Foundry API server.

3. Execute the following commands:

```javascript
cd src/test
npm install
npm run cucumber
```