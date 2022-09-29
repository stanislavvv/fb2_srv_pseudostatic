# -*- coding: utf-8 -*-

from flask import Blueprint, Response, send_file, request, current_app
from .get_fb2 import fb2_out, html_out
from .validate import redir_invalid, validate_zip, validate_fb2

# import json

dl = Blueprint("dl", __name__)

redir_all = "html.html_root"


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@dl.route("/fb2/<zip_file>/<filename>")
def fb2_download(zip_file=None, filename=None):
    zip_file = validate_zip(zip_file)
    filename = validate_fb2(filename)
    if zip_file is None or filename is None:
        return redir_invalid(redir_all)
    data = fb2_out(zip_file, filename)
    if data is not None:
        return send_file(data, attachment_filename=filename, as_attachment=True)
    else:
        return Response("Book not found", status=404)


@dl.route("/read/<zip_file>/<filename>")
def fb2_read(zip_file=None, filename=None):
    zip_file = validate_zip(zip_file)
    filename = validate_fb2(filename)
    if zip_file is None or filename is None:
        return redir_invalid(redir_all)
    data = html_out(zip_file, filename)
    if data is not None:
        return Response(data, mimetype='text/html')
    else:
        return Response("Book not found", status=404)


@dl.route("/XaiJee6Fexoocoo1")
def debug_exit():
    if current_app.config['DEBUG']:
        shutdown_server()
        return 'Server shutting down...'
    else:
        return Response("", status=404)
