import requests

resp = requests.get("http://localhost:4040/api/tunnels")
url = resp.json()['tunnels'][0]['public_url']

# vamos a formatear la salida en json
print(f'ngrok_url: {url}')
print('stripe_webhook:', f"{url}/api/v1/boletos/stripe/webhook/")
