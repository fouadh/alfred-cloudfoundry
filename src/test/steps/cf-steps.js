const { Given, Then, When, Before, BeforeAll } = require('cucumber');
const rp = require('request-promise');
const fs = require('fs');

const { createImposterFromFixture, 
        sleep, 
        setupCloudFoundryEndpoint, 
        cleanupCloudFoundryConfig, 
        clearCaches,
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
    await clearCaches();
    await sleep(500);
    await createImposterFromFixture('uaa-stubs');
    if (fs.existsSync(outputFile)) {
        fs.unlinkSync(outputFile);
    };
});

Given(/no (.*) is hosted on Cloud Foundry/, (resource) => {
    return createImposterFromFixture(`cf-no-${resource}-stubs`);
});

Given(/one (.*) named (.*) is hosted on Cloud Foundry/, (resource, appName) => {
    return createImposterFromFixture(`cf-${resource}s-stubs`);
});

When(/(.*) wants to list all the (.*)/, (user, resource) => {
    return executeAlfredCommand(user, `cf-${resource}`);
});

When(/(.*) wants to filter all the (.*) with the string '(.*)'/, (user, resource, query) => {
    return executeAlfredCommand(user, `cf-${resource}`, query);
});

Then(/the workflow should contain an item with title '(.*)' and no subtitle/, (title) => {
    return expectItemInOutput(title, "");
});

Then(/the workflow should contain an item with title '(.*)' and subtitle '(.*)'/, (title, subtitle) => {
    return expectItemInOutput(title, subtitle);
});

Then(/the number of items should be (\d+)/, (size) => {
    return expectTotalItems(size);
});