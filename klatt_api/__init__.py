from json import dumps
from types import SimpleNamespace
from urllib.parse import quote

from flask import Flask, Response, request

from .utils import array_to_wav, create_klattgrid, klattgrid_to_sound, sound_to_array


class FloatNamespace(SimpleNamespace):
    """
    Try to convert all values to floats, since most of the parameters are floats.
    ``vowel_name`` will be left as a string.
    """

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
    API_KEYS = app.config.get("API_KEYS")

    @app.route("/", methods=["POST"])
    def api():
        """
        Main API endpoint.

        POST a JSON body and set the ``X-API-KEY`` header.

        Accepts JSON with the following parameters:
        ```
        vowel_name: str
        duration: float
        pitch: float
        f1: float
        b1: float
        f2: float
        b2: float
        f3: float
        b3: float
        f4: float
        bandwidth_fraction: float
        formant_frequency_interval: float
        ```
        """

        if API_KEYS:
            if request.headers.get("X-API-KEY") not in API_KEYS:
                return Response(
                    response=dumps({"error": "Invalid API key."}),
                    status=401,
                    headers={"Content-Type": "application/json"},
                )

        try:
            query = FloatNamespace(**request.get_json(force=True))
            vowel_name = (
                quote(query.vowel_name) if query.vowel_name else None
            ) or "vowel"
            klattgrid = create_klattgrid(**vars(query))
        except Exception:
            return Response(
                response=dumps({"error": "Error when processing query parameters."}),
                status=400,
                headers={"Content-Type": "application/json"},
            )

        try:
            sound = array_to_wav(sound_to_array(klattgrid_to_sound(klattgrid)))
        except Exception:
            return Response(
                response=dumps({"error": "Error when processing Praat objects."}),
                status=500,
                headers={"Content-Type": "application/json"},
            )

        res = app.response_class(
            response=sound,
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Disposition": f'attachment; filename="{vowel_name}.wav"',
                "Content-Type": "audio/wav",
            },
        )
        return res

    return app
