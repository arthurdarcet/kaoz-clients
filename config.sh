#!/bin/sh
# kaoz client configuration

# Change these settings to match the configuration of the server

# Server password
LISTENER_PASSWORD='MyVerySecretPassword'

# Default channel to be used when no channel is specified on the command line
DEFAULT_CHANNEL='#default-channel'

# kaoz host (default: localhost)
#LISTENER_HOST='localhost'

# kaoz port (default: 9010)
#LISTENER_PORT=9010

# Use SSL to connect to the server (default: false)
#LISTENER_SSL=false

# Check the server identity with a certificate (default: no certificate check)
#LISTENER_CRT='/etc/ssl/kaoz/server.crt' #This file should only contain the certificate, not the key ;-)
