from upscale import upscale, celery_app
from flask import Flask, jsonify, request
from flask.views import MethodView
import uuid
import os
from celery.result import AsyncResult
from upscale import celery_app

app = Flask('app')
app.config['UPLOAD_FOLDER'] = 'files'
celery_app.conf.update(app.config)

class ContextTask(celery_app.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery_app.Task = ContextTask
class Upscale(MethodView):
    def get(self, task_id):
        task = AsyncResult(task_id, app=celery_app)
        return jsonify({'status': task.status,
                        'result': task.result})

    def post(self):
        image_id = self.save_image("image_1")


        task = upscale.delay(image_id, '600px.png')
        return jsonify({"task_id": task.id})

    def save_image(self, field):
        image = request.files.get(field)
        extension = image.filename.split('.')[-1]
        path = os.path.join('files', f'{uuid.uuid4()}.{extension}')
        image.save(path)
        return path


upscale_view = Upscale.as_view("upscale")
app.add_url_rule("/tasks/<string:task_id>", view_func=upscale_view, methods=["GET"])
app.add_url_rule("/processed/{file}", view_func=upscale_view, methods=["GET"])
app.add_url_rule("/upscale/", view_func=upscale_view, methods=["POST"])







if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)