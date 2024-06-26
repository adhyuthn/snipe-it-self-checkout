>[!Warning]
> Might not work on SSL enabled Snipe-IT setups.

# snipe-it-self-checkout

According to this ![issue](https://github.com/snipe/snipe-it/issues/5994#issuecomment-2126619141), self checkout for assets is a destined for v7 and that's a long way. This is a flask app that provides you with an interface to do the same, with the awesome API that Snipe-IT provides. 
- No additional login is required, uses the Oauth  from Snipe-IT. 
- Simply scan the QR code on the asset and you are good to go.

## Installation
- Assuming you have Snipe-IT installed and running
- Install flask using `pip install flask`
- Run the `runme.sh` script as `sudo`
- Get your API key from Snipe-IT (should be from an admin account)
- Get your Oauth token from Snipe-IT (should be from an admin account). The callback should be given as `<your base domain name>/self-checkout/callback` 
- Configure the `config.ini`
- Setup your apache server to serve the app using `mod_wsgi`.
- Restart apache server


