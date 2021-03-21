const puppeteer = require('puppeteer');
const fs = require('fs');
const { pick } = require('lodash');

const delay = (time) => {
   return new Promise(function(resolve) { 
       setTimeout(resolve, time)
   });
};

const getLocalStorage = async (page) => {
	const localStorageData = await page.evaluate(() => {
    let json = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      json[key] = localStorage.getItem(key);
    }
    return json;
  });

  return localStorageData || {};
}

const navigations = async () => {
	const user = 'bill.lunger@brilliantav.com';
	const password = 'Fr@nk3nPul$E';

  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  await delay(1000);

  await page.goto('https://d-tools.cloud/dashboard');

  await delay(10000);

  await page.$eval('#logonIdentifier', (el, user) => {
		return el.value = user;
	}, user);

  await page.$eval('#password', (el, password) => {
		return el.value = password;
	}, password);

	await page.$eval('button[id="next"]', button => {
		button.click();
	});

	await delay(25000);

	const localStorage = await getLocalStorage(page);
  const data = pick(localStorage, ['accessToken', 'dtToken']);
	
	fs.writeFileSync('./creds.json', JSON.stringify(data, null, 4));

  await browser.close();
};

try {
	(async () => {
		navigations();
	})();
} catch (error) {
	console.error(error);
}
