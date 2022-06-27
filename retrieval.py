from models import PEPEModel
import torch
import numpy as np
import pandas as pd
import os
import ast
import logging

from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer
from pandarallel import pandarallel
pandarallel.initialize()


bertweet_tokenizer = AutoTokenizer.from_pretrained("vinai/bertweet-base")


def load_inferred_feature(feature_path: str, banning_gifs: set = set()):
    # load precomputed gif features
    _gif_ds = pd.read_csv(feature_path)
    _gif_ds["gif_feature"] = _gif_ds["gif_feature"].parallel_apply(
        ast.literal_eval).apply(np.array)
    # filter banning gifs
    _gif_ds = _gif_ds[_gif_ds["gif_id"].apply(lambda x: x not in banning_gifs)]

    # load gif_features into a dict
    gif_index_to_id = _gif_ds['gif_id'].to_list()
    return {
        "gif_features": np.stack(_gif_ds['gif_feature'].to_list()),
        "gif_index_to_id": gif_index_to_id,
        "gif_id_to_index": {gif_id: idx for idx, gif_id in enumerate(gif_index_to_id)}
    }


def _tokenize_tweet(tweet):
    # max_length=128 default for bertweet
    return bertweet_tokenizer.encode(tweet, max_length=128, truncation=True)


class PEPERetrieval():
    def __init__(self, checkpoint_path, pretrained_oscar_path, inferred_feature):
        self.model = PEPEModel(pretrained_oscar_path)
        if os.environ.get("CUDA_VISIBLE_DEVICES", None):
            self.model = self.model.cuda()
            map_location = None
        else:
            map_location = torch.device('cpu')

        logging.info(self.model.load_state_dict(
            torch.load(checkpoint_path, map_location=map_location)))

        self.gif_features = inferred_feature.get("gif_features")
        self.gif_index_to_id = inferred_feature.get("gif_index_to_id")
        self.gif_id_to_index = inferred_feature.get("gif_id_to_index")

    def _tweet_to_tweet_feature_PEPE(self, normalized_tweet: str):
        tweet_ids = _tokenize_tweet(normalized_tweet)
        tweet_ids = torch.Tensor(tweet_ids).long().unsqueeze(0)
        if os.environ.get("CUDA_VISIBLE_DEVICES", None):
            tweet_ids = tweet_ids.cuda()
        return self.model.extract_tweet_feature(tweet_ids).detach().cpu().squeeze().numpy()

    def retrieve(self, normalized_tweet: str, k=10):
        tweet_feature = self._tweet_to_tweet_feature_PEPE(normalized_tweet)
        _scores = tweet_feature @ self.gif_features.T
        recommended_indices = list(reversed((_scores).argsort()[-k:].tolist()))
        recommended_gifs = [self.gif_index_to_id[i]
                            for i in recommended_indices]
        return recommended_gifs

    def get_similarity(self, normalized_tweet: str, gif_id: str):
        tweet_feature = self._tweet_to_tweet_feature_PEPE(
            normalized_tweet)
        gif_idx = self.gif_id_to_index.get(gif_id)
        return cosine_similarity(tweet_feature.reshape(1, -1),
                                 self.PEPE_gif_features[gif_idx].reshape(1, -1)).tolist()[0][0]
