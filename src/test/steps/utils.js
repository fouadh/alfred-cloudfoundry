const fs = require('fs');
const rp = require('request-promise');
const runJxa = require('run-jxa');
const expect = require('chai').expect;
const waitOn = require('wait-on');

const mtb = 'http://localhost:2525';
const outputFile = `${__dirname}/../output.json`;

exports.mtb = mtb;
exports.outputFile = outputFile;

exports.createImposterFromFixture = ((fixtureName) => {
  const uaa = fs.readFileSync(`./fixtures/${fixtureName}.json`, 'utf-8');
  return rp.post(`${mtb}/imposters`, { body: uaa });
});

exports.sleep = (milliseconds) => {
  return new Promise(resolve=>{
      setTimeout(resolve,milliseconds)
  })
}

exports.setupCloudFoundryEndpoint = () => {
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

exports.cleanupCloudFoundryConfig = () => {
  return runJxa(() => {
      const alfred = Application("Alfred 3");
      alfred.runTrigger("cf-cleanup", { "inWorkflow": "com.fouadhamdi.alfred.cloudfoundry" });
  });
}

exports.expectTotalItems = async (size) => {
  await waitOn({
      resources: [ `file:${outputFile}` ],
      timeout: 3000
  });

  const items = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));
  expect(items.length).to.equal(size);
}

exports.expectItemInOutput = async (title, subtitle) => {
  await waitOn({
      resources: [ `file:${outputFile}` ],
      timeout: 3000
  });

  const items = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));
  const data = items.filter((item) => item.title === title && item.subtitle === subtitle);
  expect(data.length).to.equal(1);
}

exports.executeAlfredCommand = async (user, command, query) => {
  await setupCloudFoundryCredentials(`${user}@acme.com`, `${user.toLowerCase()}123`);
  await exports.sleep(600);
  await runJxa((outputFile, command, query) => {
      const alfred = Application("Alfred 3");
      let arguments = outputFile;
      if (query) arguments = `${arguments}|${query}`
      alfred.runTrigger(command, { "inWorkflow": "com.fouadhamdi.alfred.cloudfoundry", "withArgument": arguments });
  }, [outputFile, command, query]);
}