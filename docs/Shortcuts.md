# Apple Shortcuts: Voice Label Printer

This guide walks you through creating an Apple Shortcut that lets you dictate a label and print it to your DYMO LabelWriter 450 via the local API.

Prereqs:
- The Flask app is running on your Mac or Raspberry Pi.
- You’re on the same network as the printer host.
- You have the token from `.label_token` on the host.

## 1) Get your token and host

On the host running the Flask app:
- Find your token: open `.label_token` in the repo root and copy its contents.
- Find your host address: use your LAN IP or mDNS name (e.g., `http://printer-host.local:5000`).

Optional: visit `http://<host>:5000/api/config` in a browser to confirm config and detected media.

## 2) Create the Shortcut (iPhone or Mac)

Actions to add in order:

1. Dictate Text
   - Result variable: `Text`
2. Ask for Input
   - Prompt: `Copies?`  
   - Input type: Number  
   - Default answer: 1  
   - Result variable: `Copies`
3. Choose from Menu
   - Prompt: `Size preset`  
   - Items: `Large`, `Small`  
   - In each menu branch, set a variable `Size` to `large` or `small` respectively (lowercase)
4. Text (build JSON body)
   - Content:
```
{
  "text": "[[Text]]",
  "copies": [[Copies]],
  "size": "[[Size]]"
}
```
   Replace `[[Text]]`, `[[Copies]]`, `[[Size]]` with your variables.
5. Get Contents of URL
   - URL: `http://<host>:5000/api/print` (replace `<host>` with your host/IP)  
   - Method: POST  
   - Request Body: JSON  
   - Request Body: use the Text from step 4  
   - Headers:  
     - `Content-Type: application/json`  
     - `X-Label-Token: <paste-your-token>`
6. Show Result (optional)

Name the Shortcut: `Print Label`.

## 3) Use it hands-free

- Trigger with Siri: “Hey Siri, Print Label” → Dictate the text when prompted.  
- On Apple Watch: run the Shortcut from your watch and dictate/enter copies quickly.

## 4) Reprint Shortcut (optional)

Create a second Shortcut:
1. Ask for Input → `Copies` (default 1)
2. Text body:
```
{
  "copies": [[Copies]]
}
```
3. Get Contents of URL
   - URL: `http://<host>:5000/api/reprint`
   - Method: POST  
   - Request Body: JSON  
   - Request Body: the text from step 2  
   - Headers:  
     - `Content-Type: application/json`  
     - `X-Label-Token: <paste-your-token>`
4. Show Result (optional)

## Tips

- If you change rolls, set the CUPS media in `config.json` or let the app auto-detect it the next time you print.
- If text is too long, it will be wrapped to two lines and truncated with an ellipsis.
- To specify a custom media for a single request, add `"media": "<cups-media>"` in the JSON.

## Troubleshooting

- 401 unauthorized: the token header is missing or wrong.
- 409 print failed: printer is offline or CUPS options not accepted; verify `lpstat -p` and try a simple test page.
- Nothing printed: check that the service is reachable (try `/api/health`) and that the printer is your default or configured with `printer_name`.
