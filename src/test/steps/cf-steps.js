const { Given, Then, When, Before, BeforeAll } = require('cucumber');
const rp = require('request-promise');
const fs = require('fs');

const { createImposterFromFixture, 
        sleep, 
        setupCloudFoundryEndpoint, 
        cleanupCloudFoundryConfig, 
        expectItemInOutput,
        expectTotalItems,
        executeAlfredCommand,
        mtb,
        outputFile } = require('./utils');

BeforeAll(async () => {
    await cleanupCloudFoundryConfig();
    await sleep(600);
    await setupCloudFoundryEndpoint();
    await sleep(600);
});

Before(async () => {
    await rp.delete(`${mtb}/imposters`);
    await createImposterFromFixture('uaa-stubs');
    if (fs.existsSync(outputFile)) {
        fs.unlinkSync(outputFile);
    };
});

Given('no application is hosted on Cloud Foundry', async () => {
    await createImposterFromFixture('cf-noapp-stubs');
});

Given(/one application named (.*) is started on Cloud Foundry/, async (appName) => {
    await createImposterFromFixture('cf-apps-stubs');
});

Given('no route is hosted on Cloud Foundry', async () => {
    await createImposterFromFixture('cf-noroute-stubs');
});

Given(/one route with host name (.*) is created on Cloud Foundry/, async (host) => {
    await createImposterFromFixture('cf-routes-stubs');
});

Given('no services is hosted on Cloud Foundry', async () => {
    await createImposterFromFixture('cf-noservice-stubs');
});

Given('one service named roster-service is created on Cloud Foundry', async () => {
    await createImposterFromFixture('cf-services-stubs');
});

Given('no buildpack is available on Cloud Foundry', async () => {
    await createImposterFromFixture('cf-nobuildpacks-stubs');
});

Given('buildpacks are installes on Cloud Foundry', async () => {
    await createImposterFromFixture('cf-buildpacks-stubs');
});

When(/(.*) wants to list all the apps/, async (user) => {
    await executeAlfredCommand(user, "cf-apps");
});

When(/(.*) wants to filter all the apps with the string '(.*)'/, async (user, query) => {
    await executeAlfredCommand(user, "cf-apps", query);
});

When(/(.*) wants to list all the routes/, async (user) => {
    await executeAlfredCommand(user, "cf-routes");
});

When(/(.*) wants to list all the services/, async (user) => {
    await executeAlfredCommand(user, "cf-services");
});

When(/(.*) wants to list all the buildpacks/, async (user) => {
    await executeAlfredCommand(user, "cf-buildpacks");
});

Then(/the workflow should contain an item with title '(.*)' and no subtitle/, async (title) => {
    await expectItemInOutput(title, "");
});

Then(/the workflow should contain an item with title '(.*)' and subtitle '(.*)'/, async (title, subtitle) => {
    await expectItemInOutput(title, subtitle);
});

Then(/the number of items should be (\d+)/, async (size) => {
    await expectTotalItems(size);
});