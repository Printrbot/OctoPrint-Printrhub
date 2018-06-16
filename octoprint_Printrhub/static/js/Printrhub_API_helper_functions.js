
/* ********************************************************** Query Request */
const TESTING = false;

const DEFAULT_RETURN_VALUE = '';
const DEFAULT_LOCATION_STL_PREVIEW_IMG = '/plugin/Printrhub/static/img/';

let __global_api__ = '';
let __username__ = '';
let __userApiKey__ = '';

const Printrhub = {
  /*
  async test() {
    const query = '/api/users';
    const response = await fetch(query, {
                                          method: 'POST'
                                        });
    if (response.ok) {
      const jsonResponse = await response.json();
      console.log(jsonResponse);

    } else {
      console.log('Something terrible has gone wrong!');
    }
  },
  */

  /*
  async authenticateHandShake() {
    let unverified_key = '';
    const query = `/apps/auth`;
    const response = await fetch(query, {
                                          method: 'GET'
                                        });
    if (response.ok) {
      const jsonResponse = await response.json();
      console.log('Unverified Key:');
      console.log(jsonResponse);

      unverified_key = jsonResponse.unverifiedKey;

      // Encrypt with the public key...
      const appid = "Printrhub"
      const version = "1.0"
      const message_to_sign = appid + ":" + version + ":" + unverified_key;

      var rsa = new RSAKey();
      const modulus = 'a5261939975948bb7a58dffe5ff54e65f0498f9175f5a09288810b8975871e99af3b5dd94057b0fc07535f5f97444504fa35169d461d0d30cf0192e307727c065168c788771c561a9400fb49175e9e6aa4e23fe11af69e9412dd23b0cb6684c4c2429bce139e848ab26d0829073351f4acd36074eafd036a5eb83359d2a698d3';
      rsa.setPublic( modulus, '00040');

      var res = rsa.encrypt(message_to_sign);
      if (res) {
        //do nothing
      } else {
        console.log('authenticateHandShake: Something went terribly wrong');
        return;
      }

      const encrypted = linebrk(hex2b64(res), 64);
      console.log(`Encrypted: ${encrypted}`);

      const query2 = '/apps/auth';
      const data = JSON.stringify(  {
                                      'appid': `${appid}`,
                                      'appversion': `${version}`,
                                      'key': `${unverified_key}`,
                                      '_sig': `${encrypted}`
                                    });
      console.log('Query:');
      console.log(`${data}`);
      const response2 = await fetch(query,  {
                                              method: 'POST',
                                              body: data
                                            });

      if (response2.ok) {
        const jsonResponse2 = await response2.json();
        console.log(jsonResponse2);

      }
    } else {
      console.log('Something has gone terribly wrong!');
    }
  },
  */

  async getGlobalApiKey() {
    //if global api is already discovered
    if (__global_api__ !== '') {
      return __global_api__;
    }

    const query = `/api/settings?apikey=`;
    const response = await fetch(query, {
                                          method: 'GET',
                                          credentials: "same-origin"
                                        });
    if (response.ok) {
      const jsonResponse = await response.json();
      if (TESTING) {
        console.log('Global Key:');
        console.log(jsonResponse);
      }

      if (jsonResponse.api.key === null) {
        console.log('Something went terribly wrong');
        return DEFAULT_RETURN_VALUE;
      }

      __global_api__ = jsonResponse.api.key;
      if (TESTING) {
          console.log(__global_api__);
      }
      return __global_api__;
    }

    console.log('Something went terribly wrong');
    return DEFAULT_RETURN_VALUE;
  },

  async getUserName() {
    //var usernameComponent = document.getElementById('username');

    // if username is already discovered
    if (__username__ !== '') {
      //usernameComponent.innerHTML = __username__;
      return __username__;
    }

    if (__global_api__ === DEFAULT_RETURN_VALUE) {
      __global_api__ = await Printrhub.getGlobalApiKey();
    }

    const query = `/api/users?apikey=${__global_api__}`;
    const response = await fetch(query, {
                                          method: 'GET'
                                        });
    if (response.ok) {
      const jsonResponse = await response.json();
      if (TESTING) {
        console.log("User Profile:");
        console.log(jsonResponse);
      }

      const users = jsonResponse.users;
      //cont numUsers = users.length;
      const activeUser = users.find( x => { return x.active == true; });

      if (activeUser === undefined) {
        // NEED TO LOGIN
        //usernameComponent.innerHTML = 'Please login';
        return 'Please login';

      } else {
        // SUCCESS!
        //usernameComponent.innerHTML = activeUser.name;
        __username__ = activeUser.name;
        __userApiKey__ = activeUser.apikey;
        return activeUser.name;
      }

    } else {
      console.log('Something terrible has gone wrong!');
    }
    return DEFAULT_RETURN_VALUE;
  },

  /*
  async getSystemCurrentSettings() {
    const user = await Printrhub.getUserName();
    if (user === undefined) {
      console.log('getSystemCurrentSettings: Something terrible has gone wrong!');
      return DEFAULT_RETURN_VALUE;
    }

    const query = `/api/settings?apikey=${__userApiKey__}`;
    console.log(`System Settings: ${query}`);

    const response = await fetch(query, {
                                          method: 'GET',
                                        });
    if (response.ok) {
      const jsonResponse = await response.json();
      console.log('System Settings:');
      console.log(jsonResponse);

    } else {
      console.log('Something terrible has gone wrong!');
    }
  },
  */

  async isPreviewImgExists(filename) {
    const query = `${DEFAULT_LOCATION_STL_PREVIEW_IMG}${filename}`;
    const response = await fetch(query, {
                                          method: 'GET'
                                        });
    if (response.ok) {
      const jsonResponse = await response.json();
      if (TESTING) {
        console.log("Preview STL:");
        console.log(jsonResponse);
      }
      return query;

    } else {
      console.log("Something went terribly wrong");
    }

  },
}

//export default Printrhub;

//document.onload = Printrhub.getGlobalApiKey();
window.onload = Printrhub.getUserName();
