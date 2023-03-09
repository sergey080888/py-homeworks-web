from werkzeug.security import safe_join

from upscale import upscale, celery_app
from flask import Flask, jsonify, request, send_file, abort
from flask.views import MethodView
import uuid
import os
from celery.result import AsyncResult


app = Flask("app")
app.config["UPLOAD_FOLDER"] = "files"
celery_app.conf.update(app.config)


class ContextTask(celery_app.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery_app.Task = ContextTask


class Upscale(MethodView):
    def get(self, task_id=None, file=None):
        if task_id:
            task = AsyncResult(task_id, app=celery_app)
            if task.status == "SUCCESS":
                path = os.path.abspath(r"files")
                files = os.listdir(path)
                if files:
                    files = [os.path.join(path, file) for file in files]
                    files = [file for file in files if os.path.isfile(file)]
                    file_link = max(files, key=os.path.getctime)

                    return jsonify({"status": task.status, "file_link": file_link})
            return jsonify({"status": task.status})
        elif file:
            file_name = os.path.basename(file)
            print('file_name-->', {file})
            safe_path = safe_join(app.config["UPLOAD_FOLDER"], file_name)
            try:
                return send_file(safe_path, as_attachment=True)
            except FileNotFoundError:
                abort(404)

    def post(self):
        image_id = self.save_image("image_1")

        task = upscale.delay(image_id, image_id)
        return jsonify({"task_id": task.id})

    def save_image(self, field):
        image = request.files.get(field)
        extension = image.filename.split(".")[-1]
        path = os.path.join("files", f"{uuid.uuid4()}.{extension}")
        image.save(path)
        return path


upscale_view = Upscale.as_view("upscale")
app.add_url_rule("/tasks/<string:task_id>", view_func=upscale_view, methods=["GET"])
app.add_url_rule("/processed/<path:file>", view_func=upscale_view, methods=["GET"])
app.add_url_rule("/upscale/", view_func=upscale_view, methods=["POST"])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
