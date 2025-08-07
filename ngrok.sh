#!/bin/bash

# Agrega el authtoken de ngrok (solo es necesario la primera vez)
ngrok config add-authtoken 30QorNduncj5jeESnfuWQxo9NSQ_mYeuve81PWBdzibgLg1A

# Inicia el túnel a localhost:8080
ngrok http http://localhost:8080
