from flask import Flask, request, Response, send_from_directory, stream_with_context, jsonify
import requests
from urllib.parse import unquote_plus
import os
import webbrowser

app = Flask(__name__, template_folder="templates")

@app.route("/demo/<path:filename>")
def static_file(filename):
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), "templates"), filename
    )


@app.route("/proxy", methods=["GET", "POST"])
def proxy():
    """
    Proxy endpoint. Client sends the external URL as query parameter `url`.
    Example: GET /proxy?url=https://api.github.com/zen
    """
    raw_url = request.args.get("url", "")
    print(raw_url)
    if not raw_url:
        return jsonify({"error": "Missing 'url' query parameter"}), 400

    # Support URLs that are passed URL-encoded
    url = unquote_plus(raw_url)

    # Forward method, some headers and body
    method = request.method
    headers = {}

    # Forward Content-Type if present
    if request.content_type:
        headers["Content-Type"] = request.content_type

    try:
        # Stream the remote response back to the client
        remote_resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=request.args.to_dict(),  # will include 'url' param too; remote servers will ignore unknown params in many cases
            data=request.get_data(),
            stream=True,
            timeout=10,
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Upstream request failed", "detail": str(e)}), 502

    # Build Flask response streaming the body
    resp_headers = remote_resp.headers
    excluded_status = remote_resp.status_code

    def generate():
        try:
            for chunk in remote_resp.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        finally:
            remote_resp.close()

    return Response(stream_with_context(generate()), status=excluded_status, headers=resp_headers)


if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5137/demo/index.html")
    app.run(host="127.0.0.1", port=5137, debug=True)
