alfred-cloudfoundry
===================

# To start

1. Download and install [Cloud-Foundry.alfredworkflow]()

2. Configure the endpoint and your Cloud Foundry credentials (see in the **How to use** section)

3. Enjoy !

# How to use

- Setup Cloud Foundry endpoint

```
  cf setendpoint <endpoint>
```

- Setup Cloud Foundry credentials

```
  cf setcredentials <login> <password>
```

- List applications

- List routes

- List services

- List services instances

- List services bindings

- List shared domains

- List spaces

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