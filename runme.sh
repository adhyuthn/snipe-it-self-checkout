#!/bin/bash

git clone https://github.com/adhyuthn/snipe-it-self-checkout
sudo mv ./snipe-it-self-checkout /var/www/snipe-it-self-checkout
sudo chown -R www-data:www-data /var/www/snipe-it-self-checkout
sudo chmod -R 755 /var/www/snipe-it-self-checkout

## Need to update the apache config files