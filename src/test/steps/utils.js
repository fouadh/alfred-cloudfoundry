const util = require('util');
const fs = require('fs');
const readFile = util.promisify(fs.readFile);
const rp = require('request-promise');
const runJxa = require('run-jxa');
const chai = require('chai');
const chaiAsPromised = require("chai-as-promised");
chai.should();
chai.use(chaiAsPromised);

const waitOn = require('wait-on');
const mtb = 'http://localhost:2525';
const outputFile = `${__dirname}/../output.json`;

exports.mtb = mtb;
exports.outputFile = outputFile;

exports.createImposterFromFixture = (fixtureName) => {
  return readFile(`./fixtures/${fixtureName}.json`, 'utf-8')
    .then((data) => rp.post(`${mtb}/imposters`, { body: data }));
};

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
      alfred.runTrigger("cf-clear-credentials", { "inWorkflow": "com.fouadhamdi.alfred.cloudfoundry" });
  });
}

exports.clearCaches = () => {
  return runJxa(() => {
      const alfred = Application("Alfred 3");
      alfred.runTrigger("cf-clear-caches", { "inWorkflow": "com.fouadhamdi.alfred.cloudfoundry" });
  });
}

exports.expectTotalItems = (size) => {
  return readOutputFile()
      .then(items => items.length)
      .should.eventually.equal(size);
}

exports.expectItemInOutput = (title, subtitle) => {
  return readOutputFile()
            .then((items) => filterByTitleAndSubtitle(items, title, subtitle))
            .then(data => data.length)
            .should.eventually.equal(1);
}

filterByTitleAndSubtitle = (items, title, subtitle) => {
  return items.filter((item) => item.title === title && item.subtitle === subtitle);
}

readOutputFile = () => {
  return waitOn({
    resources: [ `file:${outputFile}` ],
    timeout: 3000
  }).then(() => readFile(outputFile, 'utf-8'))
    .then((contents) => JSON.parse(contents)); 
}

exports.executeAlfredCommand = (user, command, query) => {
  return setupCloudFoundryCredentials(`${user}@acme.com`, `${user.toLowerCase()}123`)
    .then(() => exports.sleep(600))
    .then(() => runJxa(callAlfred, [outputFile, command, query]));
}

callAlfred = (outputFile, command, query) => {
  const alfred = Application("Alfred 3");
  let arguments = outputFile;
  if (query) arguments = `${arguments}|${query}`
  alfred.runTrigger(command, { "inWorkflow": "com.fouadhamdi.alfred.cloudfoundry", "withArgument": arguments });
}