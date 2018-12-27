const { Given, Then, When, Before, BeforeAll } = require('cucumber');
const rp = require('request-promise');
const fs = require('fs');
const runJxa = require('run-jxa');
const expect = require('chai').expect;
const waitOn = require('wait-on');

const mtb = 'http://localhost:2525';
const outputFile = `${__dirname}/../output.json`;

createImposterFromFixture = ((fixtureName) => {
    const uaa = fs.readFileSync(`./fixtures/${fixtureName}.json`, 'utf-8');
    return rp.post(`${mtb}/imposters`, { body: uaa });
});

sleep = (milliseconds) => {
    return new Promise(resolve=>{
        setTimeout(resolve,milliseconds)
    })
}

setupCloudFoundryEndpoint = () => {
    return runJxa(() => {
        const alfred = Application("Alfred 3");
        alfred.runTrigger("cf-setendpoint", { "inWorkflow": "com.fouadhamdi.alfred.cloudfoundry", "withArgument": "https://localhost:3001" });
    });
}

setupCloudFoundryCredentials = (login, password) => {
    return runJxa((login, password) => {
        const alfred = Application("Alfred 3");
        alfred.runTrigger("cf-setcredentials", { "inWorkflow": "com.fouadhamdi.alfred.cloudfoundry", "withArgument": `${login} ${password}` });
    }, [login, password]);
}

cleanupCloudFoundryConfig = () => {
    return runJxa(() => {
        const alfred = Application("Alfred 3");
        alfred.runTrigger("cf-cleanup", { "inWorkflow": "com.fouadhamdi.alfred.cloudfoundry" });
    });
}

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

When(/(.*) wants to list all the apps/, async (user) => {
    await setupCloudFoundryCredentials(`${user}@acme.com`, `${user.toLowerCase()}123`);
    await sleep(600);
    await runJxa((outputFile) => {
        const alfred = Application("Alfred 3");
        alfred.runTrigger("cf-apps", { "inWorkflow": "com.fouadhamdi.alfred.cloudfoundry", "withArgument": outputFile });
    }, [outputFile]);
});

expectItemInOutput = async (title, subtitle) => {
    await waitOn({
        resources: [ `file:${outputFile}` ],
        timeout: 3000
    });

    const items = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));

    const data = items.filter((item) => item.title === title && item.subtitle === subtitle);
    expect(data.length).to.equal(1);
}

Then(/the workflow should contain an item with title '(.*)' and no subtitle/, async (title) => {
    await expectItemInOutput(title, "");
});

Then(/the workflow should contain an item with title '(.*)' and subtitle '(.*)'/, async (title, subtitle) => {
    await expectItemInOutput(title, subtitle);
});