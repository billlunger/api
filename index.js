const fetch = require('isomorphic-fetch');
const queryString = require('query-string');

// Environment Variables
const DTOOLS_API = 'https://dtoolsad.b2clogin.com/dtoolsad.onmicrosoft.com/B2C_1_SigninSignup/SelfAsserted';
const STATE_PROPERTIES = 'eyJUSUQiOiJkNTk1ZjQyNS1mMTM3LTRmMWQtYTE5Yy1jMGJkMDczYzc2NGEifQ'

// API Arguments
const user = 'bill.lunger@brilliantav.com';
const password = 'Fr@nk3nPul$E';
const CSRF_TOKEN = 'V3pLZ211TXF3enlIYUtiREYrOEVFeEFmdVdzdkNLazhwRTNBQm1xZ0E1b3BjbXd5OVRKSzRzTUZER2JkR0pzR3pkcitMWFhWTzZGUXZGN2dTVjIrOVE9PTsyMDIxLTAyLTIxVDAyOjQ5OjQwLjc5MDEyNDRaO0RmQ1ZBUzFtR1JXMkR0UzJiWmVnZUE9PTt7Ik9yY2hlc3RyYXRpb25TdGVwIjoxfQ==';

const encodeFormData = (data) => {
    return Object.keys(data)
        .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(data[key]))
        .join('&');
}

const run = async () => {
	try {
		const response = await fetch(`${DTOOLS_API}?tx=StateProperties=${STATE_PROPERTIES}&p=B2C_1_SigninSignup`, {
			'method': 'POST',
			'headers': {
		    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		    'X-CSRF-TOKEN': CSRF_TOKEN,
		    'Cookie': `x-ms-cpim-csrf=${CSRF_TOKEN}; x-ms-cpim-cache|jfsv1tfxhu-hnmc9bzx2sg_0=m1.0yKLZz9Z+ca/b8h9.GCnvGYANNmWkUn931bmCzw==.0.TrLGsfhPN6H1/umpQubnrtiLgYDyIkubFDe9Zfpd6nws4iIPz41q2Fka9nDHKGQCIbYyinBJe1qo/4TQseM8LI1qbBEdBrzOUs2KeipE8CHN9GrRPYdxxr7fYCZgzP2UdrWpeadaNaSnNA/eS8EubZ0U2kzGDNug3PrUIaPkfthpj6lPRwb4MXnFJS/xV8UkO6Jem11Un0VENcfI0rgM163HnBjX3/uORnS6+uB6negezLwbthxgl0uxYYjKSHkIOyGzEpLEY2namg8wxYr9Tkd6xVWhJbnW1WUyboflZKw5BEkqqC52GK9clReFqvCm144wvrGhB5PTHcGvMf+uMy4s2inDZydwSwhMK7nOPYUEsnikYNDzuc6lmw/RhUsb1WMThpstwKLeTj0Q/paNZDK3okHcD7fvzEn4+q/WicvdanlTC9TTuV/zE5QTHCnw1TP45woaOBv7cTvKtUaPo6ByrCr3iFmTs6iOaEgCGPuuh8nOrBlsm+320/jgdatpXHZeIWll3neiGnkTAxu5yhuJB0dmUXcgfHpiHs7coRHyUnG3kSXydwbxfZxufd2kPKx4MQvVLDRyhHdrYFcAqLiMpeIsQPSfJt8ITFMyPyZBRq+qPin+m8NbkU7Ak5uvBFJrZeNM3w7QjS8LOmfQHk+u7vZlPXbrQhK4llnFv58llIbTgPgX4u64bJXmNLdsQM0WjfaOi0D1GIrOStEPSV7Q9c3p21axY1I9TYNEJLjBC0ggQHur/Jzf14aRkF/odiXlAy5qYjTcW4hnDtzHqbDD0XCpuwJebeDHEqN01Dctf1r5jOg27M6Z7sC6j7684/GpUg==; x-ms-cpim-trans=eyJUX0RJQyI6W3siSSI6ImQ1OTVmNDI1LWYxMzctNGYxZC1hMTljLWMwYmQwNzNjNzY0YSIsIlQiOiJkdG9vbHNhZC5vbm1pY3Jvc29mdC5jb20iLCJQIjoiYjJjXzFfc2lnbmluc2lnbnVwIiwiQyI6Ijc1Zjk4YjhhLTNjNzQtNDViZC04NDhjLWRkYjk1NzFkNGM5MSIsIlMiOjEsIk0iOnt9LCJEIjowfV0sIkNfSUQiOiJkNTk1ZjQyNS1mMTM3LTRmMWQtYTE5Yy1jMGJkMDczYzc2NGEifQ==`
		  },
		  'body': encodeFormData({
		  	'request_type': 'RESPONSE',
				'logonIdentifier': user,
				'password': password
		  })
		})

		const result = await response.json();

		console.log(response.headers);

		if (response.status >= 400) {
			console.error(result);
		  throw new Error("Bad response from server");
		}	

		console.log(result);
	} catch (error) {
		console.error(error);
	}
};

(() => {
	run();
})();
