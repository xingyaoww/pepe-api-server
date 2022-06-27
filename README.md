# About

This is a repo contains code necessary to deploy GIF Reply model released at [here](https://github.com/xingyaoww/gif-reply).

It is based on work described in the Findings of EMNLP 2021 paper [An animated picture says at least a thousand words: Selecting Gif-based Replies in Multimodal Dialog](https://arxiv.org/abs/2109.12212)
by [Xingyao Wang](https://xingyaoww.github.io/) and [David Jurgens](https://jurgens.people.si.umich.edu/):

```
@inproceedings{
  author = {Wang, Xingyao and Jurgens, David},
  year = 2021,
  title = {{An Animated Picture Says at Least a Thousand Words: Selecting Gif-based Replies in Multimodal Dialog}},
  booktitle = {Proceedings of the Findings of the 2021 Conference on Empirical Methods in Natural Language Processing (Findings of EMNLP)}
}  
```

# Dataset Preparation

Follow [here](https://github.com/xingyaoww/gif-reply/tree/main/data) to download all the data under `data/release`. Required data are:

- `gif-pepe-inferred-features.csv`
- `PEPE-model-checkpoint.pth`
- `gif-id-to-giphy-id-mapping.csv`

You also need to download `base-vg-labels` version of [Oscar Model](https://github.com/microsoft/Oscar/blob/master/DOWNLOAD.md), and put in under `data/oscar-pretrained-model`.

If you want to have a copy of all gifs locally (otherwise it is preferred to use `https://media.giphy.com/media/${GIPHY_ID}/giphy.mp4` to visualize GIFs): download gifs follow GIF IDs in `gif-pepe-inferred-features.csv`, and put them under `data/file/gifs` with hierarchical GIF ID naming (e.g. Original GIF ID `abcdef` convert to `a/b/c/def`, GIF File `abcdef.mp4` to `a/b/c/def.mp4`).

# Prepare Environment and Start the server

```bash
conda env create -n pepe-api-server --file environment.yml 
conda activate
python -m spacy download en_core_web_sm
./run-api-server.sh
```

# Inference through REST API

```bash
curl -X POST ${API_SERVER_URL}:${API_SERVER_PORT}/api/v1/retrieve -H 'Content-Type: application/json' -d '{"text": "Hello there!", "num_resp_gifs": 5}'
```

where `num_resp_gifs` is the number of reponse gif required.

Example response:

```json
{
  "gif_ids": [
    "ffdf5e5e60200006ffdf5f5e60200002dfdf5e5e60200002",
    "ffede0c00083c3c7fee6e4c00206c686fff6e4e00083c2c3",
    "c6e6c0d6cfcbc0c3c6e6c0decfcbc0c3c6e6c0decfcbc0c3",
    "7f1f0f0f1c1c18101f5b1f0f0702081c1f9f1f1f07031a18",
    "ffffcf830f0d0100ffff8f030f010100bf1f0f030f01013c"
  ],
  "giphy_ids": [
    "rx3flR1eNqciQ",
    "11Dkb1VvEib7fW",
    "3oriO04qxVReM5rJEA",
    "3o6Zt2PMtvg1hKOrh6",
    "FhDgTdtbXSRnW"
  ],
  "internal_links": [
    "/file/gifs/r/x/3/flR1eNqciQ.mp4",
    "/file/gifs/1/1/D/kb1VvEib7fW.mp4",
    "/file/gifs/3/o/r/iO04qxVReM5rJEA.mp4",
    "/file/gifs/3/o/6/Zt2PMtvg1hKOrh6.mp4",
    "/file/gifs/F/h/D/gTdtbXSRnW.mp4"
  ],
  "msg": "",
  "normalized_text": "Hello there !"
}
```

And you can download each response gif from the `internal_links` field (e.g. `wget ${API_SERVER_URL}:${API_SERVER_PORT}/file/gifs/r/x/3/flR1eNqciQ.mp4`).

You can also monitor the request received by accessing `http://${API_SERVER_URL}:${API_SERVER_PORT}/dashboard/overview` (default username & password are both `admin`).
