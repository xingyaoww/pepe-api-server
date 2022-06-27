from config import (
    GIF_ID_TO_GIPHY_ID_MAPPING_FILE,
    OSCAR_PRETRAINED_MODEL_DIR,
    PEPE_MODEL_CKPT,
    INFERRED_FEATURE_PATH,
    BANNED_GIPHY_GIFS,
    FILTER_WORDS,
)
from utils import normalizeTweet, lemmatize, text_satisfy_constaint
from retrieval import load_inferred_feature, PEPERetrieval
import flask_monitoringdashboard as dashboard

import flask
import pandas as pd
import logging
import sys
import os

logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO
)

app = flask.Flask(__name__, template_folder="templates")
dashboard.bind(app)

# Load ID mapping
GIF_ID_TO_GIPHY_ID = dict(pd.read_csv(GIF_ID_TO_GIPHY_ID_MAPPING_FILE)[
                          ["gif_id", "giphy_id"]].to_numpy())
logging.info("GIPHY ID mapping loaded.")

# Load lemmatized filter words
LEMMATIZED_FILTER_WORDS = set([lemmatize(i) for i in FILTER_WORDS])
logging.info("Lemmatized filter words loaded.")

# Load PEPE Model
inferred_gif_features = load_inferred_feature(
    feature_path=INFERRED_FEATURE_PATH, banning_gifs=BANNED_GIPHY_GIFS)
logging.info("Inferred GIF features loaded.")

PEPE_retrieval = PEPERetrieval(
    PEPE_MODEL_CKPT, OSCAR_PRETRAINED_MODEL_DIR, inferred_gif_features)
logging.info("PEPE retrieval loaded.")

def _gif_id_to_structured_path(gif_id):
    return os.path.join(gif_id[0], gif_id[1], gif_id[2], gif_id[3:])

def gif_id_to_filepath(
    gif_id, ext='.mp4', source=""
    ) -> str:
    return os.path.join(source, _gif_id_to_structured_path(gif_id)+ext)

def infer_text(text, num_resp_gifs) -> dict:
    """Infer text for replying GIF."""
    if not text_satisfy_constaint(text, LEMMATIZED_FILTER_WORDS):
        # filter check for input text
        ret = {
            "normalized_text": "",
            "gif_ids": [],
            "giphy_ids": [],
            "internal_links": [],
            "msg": "huh, I'm not sure how to respond to that."
            #"No reply is generated. Your input contains sensitive keywords that are filtered by our system.",
        }
    else:
        normalized_text = normalizeTweet(text)
        # retrieve GIFs when text satisfies constraint
        gif_ids = PEPE_retrieval.retrieve(
            normalized_text, k=num_resp_gifs
        )

        giphy_ids = list(map(lambda x: GIF_ID_TO_GIPHY_ID.get(x), gif_ids))
        internal_links = [gif_id_to_filepath(i, source="/file/gifs/") for i in giphy_ids]
        ret = {
            "normalized_text": normalized_text,
            "gif_ids": gif_ids,
            "giphy_ids": giphy_ids,
            "internal_links": internal_links,
            "msg": "",
        }
    return ret


@app.route('/api/v1/retrieve', methods=['POST'])
def retrieve():
    """Retrieve the comment/tweet from the given request.

    request.json format:
    {
        "text": "my heart actually hearts I'm so sad. I hate sad bitch hours :/",
        "num_resp_gifs": 5, // optional, default to 10
    }

    response:
    {
        "normalized_text": "my heart actually hearts I 'm so sad . I hate sad bitch hours :/",
        "gif_ids": ["[GIF ID 1]", ... ],
        "msg": "", // reserved in case of error
    }
    """
    data = flask.request.json
    text = data.get("text", None)
    num_resp_gifs = data.get("num_resp_gifs", 10)

    error = bool(not text)\
        or bool(num_resp_gifs <= 0)
    if error:
        flask.abort(400)

    return flask.jsonify(infer_text(text, num_resp_gifs))


@app.route('/', methods=['GET', 'POST'])
def pepe_demo_page():
    """Render the retrieval result by input.

    form content:
    {
        "text": "my heart actually hurts I'm so sad. I hate sad bitch hours :/",
    }

    context form:
    {
        "normalized_text": normalized_text,
        "gif_ids": gif_ids,
        "giphy_ids": giphy_ids,
        "msg": "",
    }
    """

    if flask.request.method == "POST":
        text = flask.request.form.get("text", None)
        if not text:
            flask.abort(400)

        context = infer_text(text, num_resp_gifs=5)
        context["gif_giphy_id_pairs"] = list(
            zip(context["gif_ids"], context["giphy_ids"]))
    else:
        context = {
            "normalized_text": "",
            "gif_ids": [],
            "giphy_ids": [],
            "gif_giphy_id_pairs": [],
            "msg": "",
        }
    return flask.render_template("retrieve.html", **context)

@app.route('/file/<path:filename>')
def get_file(filename):
    """Return files.
    Require files to be a local symlink points to the desired directory.
    """
    try:
        return flask.send_from_directory("data/file/", filename)
    except FileNotFoundError:
        flask.abort(404)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="9000", debug=False)
