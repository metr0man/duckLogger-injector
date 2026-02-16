import os
from microdot import Microdot, send_file, Response

app = Microdot()

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
    body {
      margin: 0;
      display: flex;
      justify-content: center; /* Horizontal centering */
      align-items: center;     /* Vertical centering */
      min-height: 100vh;       /* Full screen height */
      font-family: sans-serif;
    }

    button {
      padding: 12px 24px;      /* Better "tap target" for fingers */
      font-size: 16px;         /* Prevents iOS zoom-on-focus */
      width: auto;
      max-width: 90%;          /* Ensures it doesn't hit screen edges */
      cursor: pointer;
    }
  </style>
</head>
<body>
  <a href="/log">
    <button>Download Log</button>
  </a>
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
