import os
# Configs

DATA_DIR = os.environ.get("DATA_DIR")

# For actual deployment
INFERRED_FEATURE_PATH = os.path.join(DATA_DIR, "release", "gif-pepe-inferred-features.csv")
# For quick test and debug
# INFERRED_FEATURE_PATH = os.path.join(DATA_DIR, "release", "gif-pepe-inferred-features-top1k.csv")

PEPE_MODEL_CKPT = os.path.join(DATA_DIR, "release", "PEPE-model-checkpoint.pth")
GIF_ID_TO_GIPHY_ID_MAPPING_FILE = os.path.join(DATA_DIR, "release", "gif-id-to-giphy-id-mapping.csv")
OSCAR_PRETRAINED_MODEL_DIR = os.path.join(DATA_DIR, "oscar-pretrained-model", "base-vg-labels", "ep_67_588997/")

# Load filter words
with open("filter-words.txt", "r") as f:
    FILTER_WORDS = set(f.read().splitlines())
# Load banned gifs
with open("banned-giphy-gifs.txt", "r") as f:
    BANNED_GIPHY_GIFS = set(f.read().splitlines())
