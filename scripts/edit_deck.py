#!/usr/bin/env python3
"""
Browser-based inline editor for reveal.js presentations.

Serves the presentation with contenteditable text and a save button.
Edit any text directly in the browser, then click Save to write changes
back to the HTML file.

Usage:
    python edit_deck.py presentation.html
    python edit_deck.py presentation.html --port 8080

Open the printed URL in your browser to start editing.
Press Ctrl+C to stop the server.
"""

import argparse
import http.server
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

EDITOR_SCRIPT = """
<style>
  #editor-toolbar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 99999;
    background: #111; color: #fff; padding: 6px 16px;
    display: flex; align-items: center; gap: 12px;
    font: 13px/1 -apple-system, sans-serif;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  }
  #editor-toolbar button {
    background: #2563eb; color: #fff; border: none;
    padding: 5px 14px; font: inherit; cursor: pointer;
  }
  #editor-toolbar button:hover { background: #1d4ed8; }
  #editor-toolbar .status { opacity: 0.7; margin-left: auto; }
  #editor-toast {
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    background: #111; color: #fff; padding: 8px 20px; z-index: 99999;
    font: 13px/1 -apple-system, sans-serif;
    opacity: 0; transition: opacity 0.3s;
  }
  #editor-toast.show { opacity: 1; }
  [contenteditable]:focus {
    outline: 2px solid #2563eb;
    outline-offset: 2px;
  }
</style>

<div id="editor-toolbar">
  <span>Deck Editor</span>
  <button onclick="saveDeck()">Save</button>
  <span class="status" id="editor-status">Click any text to edit</span>
</div>
<div id="editor-toast"></div>

<script>
(function() {
  // Make all text elements editable
  const editableSelectors = 'h1, h2, h3, h4, p, li, span, td, th, code, aside.notes';
  document.querySelectorAll('.reveal .slides ' + editableSelectors).forEach(el => {
    el.setAttribute('contenteditable', 'true');
    el.setAttribute('spellcheck', 'false');
  });

  // Escape deselects
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') document.activeElement.blur();
  });

  // Ctrl/Cmd+S saves
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      saveDeck();
    }
  });
})();

function toast(msg) {
  const t = document.getElementById('editor-toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2000);
}

function saveDeck() {
  const status = document.getElementById('editor-status');
  status.textContent = 'Saving...';

  // Remove editor UI before capturing HTML
  const toolbar = document.getElementById('editor-toolbar');
  const toastEl = document.getElementById('editor-toast');
  const editorScript = document.getElementById('editor-injected-script');
  toolbar.style.display = 'none';
  toastEl.style.display = 'none';

  // Remove contenteditable attributes
  document.querySelectorAll('[contenteditable]').forEach(el => {
    el.removeAttribute('contenteditable');
    el.removeAttribute('spellcheck');
  });

  // Capture clean HTML
  const html = '<!doctype html>\\n' + document.documentElement.outerHTML;

  // Restore editor UI
  document.querySelectorAll('.reveal .slides h1, .reveal .slides h2, .reveal .slides h3, .reveal .slides h4, .reveal .slides p, .reveal .slides li, .reveal .slides span, .reveal .slides td, .reveal .slides th, .reveal .slides code, .reveal .slides aside.notes').forEach(el => {
    el.setAttribute('contenteditable', 'true');
    el.setAttribute('spellcheck', 'false');
  });
  toolbar.style.display = '';
  toastEl.style.display = '';

  // Send to server
  fetch('/__save__', {
    method: 'POST',
    headers: { 'Content-Type': 'text/html' },
    body: html
  })
  .then(r => r.json())
  .then(data => {
    if (data.ok) {
      status.textContent = 'Saved!';
      toast('Saved successfully');
    } else {
      status.textContent = 'Save failed';
      toast('Error: ' + data.error);
    }
    setTimeout(() => { status.textContent = 'Click any text to edit'; }, 2000);
  })
  .catch(err => {
    status.textContent = 'Save failed';
    toast('Network error');
  });
}
</script>
"""


class EditorHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves the deck with editor UI and handles saves."""

    html_path = None  # Set by main()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.serve_editor()
        else:
            # Serve static files (styles.css, images, etc.)
            super().do_GET()

    def do_POST(self):
        if self.path == "/__save__":
            self.handle_save()
        else:
            self.send_error(404)

    def serve_editor(self):
        """Serve the HTML with editor script injected."""
        html = self.html_path.read_text()

        # Inject editor script before </body>
        inject = f'<div id="editor-injected-script">{EDITOR_SCRIPT}</div>\n</body>'
        html = html.replace("</body>", inject)

        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

    def handle_save(self):
        """Save the cleaned HTML back to disk."""
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")

        # Remove the editor-injected-script div
        body = re.sub(
            r'<div id="editor-injected-script">.*?</div>\s*',
            "",
            body,
            flags=re.DOTALL,
        )

        try:
            self.html_path.write_text(body)
            resp = json.dumps({"ok": True}).encode()
        except Exception as e:
            resp = json.dumps({"ok": False, "error": str(e)}).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(resp))
        self.end_headers()
        self.wfile.write(resp)

    def log_message(self, fmt, *args):
        """Suppress default logging for cleaner output."""
        pass


def main():
    parser = argparse.ArgumentParser(description="Browser-based deck editor.")
    parser.add_argument("html", help="Path to presentation.html")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    args = parser.parse_args()

    html_path = Path(args.html).resolve()
    if not html_path.exists():
        print(f"Error: file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    # Serve from the HTML file's directory
    os.chdir(html_path.parent)
    EditorHandler.html_path = html_path

    server = http.server.HTTPServer(("", args.port), EditorHandler)
    print(f"Deck editor running at http://localhost:{args.port}")
    print(f"Editing: {html_path}")
    print("Press Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
