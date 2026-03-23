import asyncio
import os
from microdot import Microdot, send_file, Response
import injector
from ducky_parser import parse

app = Microdot()

_kbd = None
_led = None


def init(kbd, led):
    """Called once from main.py after hardware objects are ready."""
    global _kbd, _led
    _kbd = kbd
    _led = led

FILE_PATH = "log.txt"
CHUNK_SIZE = 1024


def file_exists():
    try:
        os.stat(FILE_PATH)
        return True
    except OSError:
        return False


homepage = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 24px 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
      font-family: sans-serif;
      gap: 16px;
    }
    h2 { margin: 0; }
    textarea {
      width: 100%;
      max-width: 480px;
      height: 180px;
      font-family: monospace;
      font-size: 14px;
      padding: 8px;
      resize: vertical;
    }
    button {
      padding: 12px 24px;
      font-size: 16px;
      cursor: pointer;
      width: auto;
      max-width: 90%;
    }
    #status { font-size: 14px; min-height: 1.2em; }
    #status.ok  { color: green; }
    #status.err { color: red;   }
  </style>
</head>
<body>
  <h2>duckLogger</h2>

  <textarea id="ducky-script" placeholder="STRING whoami\nENTER"></textarea>
  <button id="inject-btn">Inject Payload</button>
  <div id="status"></div>

  <a href="/log"><button>Download Log</button></a>

  <script>
    document.getElementById('inject-btn').addEventListener('click', function() {
      var script = document.getElementById('ducky-script').value;
      var status = document.getElementById('status');
      status.textContent = 'Sending\u2026';
      status.className = '';
      fetch('/inject', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: script
      }).then(function(r) {
        if (r.ok) {
          status.textContent = 'Injected.';
          status.className = 'ok';
        } else {
          return r.text().then(function(t) {
            status.textContent = 'Error ' + r.status + ': ' + t;
            status.className = 'err';
          });
        }
      }).catch(function(e) {
        status.textContent = 'Request failed: ' + e;
        status.className = 'err';
      });
    });
  </script>
</body>
</html>
"""


@app.route("/")
async def index(request):
    # send HTML with proper content type
    return Response(body=homepage, headers={'Content-Type': 'text/html'})


@app.route("/log")
async def download_log(request):
    if not file_exists():
        return "<h3>404 Not Found</h3>", 404

    # send file as download
    return send_file(
        FILE_PATH,
        content_type="text/plain",
    )


@app.route("/inject", methods=["POST"])
async def inject(request):
    script = request.body.decode("utf-8") if request.body else ""
    if not script.strip():
        return "Empty script", 400

    # Validate synchronously before launching — surfaces unsupported
    # commands/characters immediately without touching the USB HID bus.
    try:
        list(parse(script, caps_lock=_led.caps_lock))
    except ValueError as e:
        return str(e), 400

    asyncio.create_task(injector.run_injection(script, _kbd, _led))
    return "OK", 200
