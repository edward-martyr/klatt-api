from json import dumps
from types import SimpleNamespace

from flask import Flask, abort, request

from .utils import array_to_wav, create_klattgrid, klattgrid_to_sound, sound_to_array


class FloatNamespace(SimpleNamespace):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            try:
                kwargs[k] = float(v)
            except ValueError:
                pass
        super().__init__(**kwargs)

    def __getattr__(self, name):
        return self.__dict__.get(name, None)


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev")
    app.config.from_pyfile("config.py", silent=True)

    @app.route("/", methods=["GET"])
    def api():
        try:
            query = FloatNamespace(**request.args)
            klattgrid = create_klattgrid(**vars(query))
        except Exception as e:
            return abort(
                app.response_class(
                    response=dumps(
                        {"error": "Error when processing query parameters."}
                    ),
                    status=400,
                    headers={"Content-Type": "application/json"},
                )
            )

        try:
            sound = array_to_wav(sound_to_array(klattgrid_to_sound(klattgrid)))
        except Exception as e:
            # return abort(500, "Error when processing Praat objects.")
            return abort(
                app.response_class(
                    response=dumps({"error": "Error when processing Praat objects."}),
                    status=500,
                    headers={"Content-Type": "application/json"},
                )
            )

        res = app.response_class(
            response=sound,
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*.nyoeghau.com",
                "Content-Disposition": "attachment; filename=klatt.wav",
                "Content-Type": "audio/wav",
            },
        )
        return res

    return app
