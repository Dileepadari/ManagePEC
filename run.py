"""Development entrypoint: python run.py

Equivalent to `flask --app managepec.web run`.  Production should use a WSGI
server (`gunicorn 'managepec.web:create_app()'`) instead.
"""

from managepec.web import create_app

app = create_app()

if __name__ == "__main__":
    import os

    app.run(
        host=os.environ.get("MANAGEPEC_HOST", "127.0.0.1"),
        port=int(os.environ.get("MANAGEPEC_PORT", "5000")),
        debug=os.environ.get("MANAGEPEC_DEBUG", "1") == "1",
    )
