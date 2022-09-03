"""Noise augmentation classes"""
import functools
import random
from typing import Union, Tuple
import numpy as np
from arc.interface import BoardPair, Riddle
from arc.augmentations import functional
from arc.augmentations.classes.helpers import same_aug_for_all_pairs_helper


class Noise(object):
    def __init__(self, p: float, same_aug_for_all_pairs: bool = True, noise_level: float = 0.03, noise_size: Tuple = (1, 1)):
        self.p = p
        self.same_aug_for_all_pairs = same_aug_for_all_pairs
        self.noise_level = noise_level
        self.noise_size = noise_size

    @staticmethod
    def get_params(seed, **kwargs):
        """
        Get parameters for this augmenter. Must use the seed provided
        """
        # random.seed(seed)
        #noise_dist = random.choice(kwargs['noise_dist'])
        noise_level = kwargs['noise_level']
        assert noise_level >= 0.0 and noise_level <= 1.0, "noise_level must be a percentage (between 0 and 1)"
        noise_size = kwargs['noise_size']
        return noise_level, noise_size

    def __call__(self, inp: Union[BoardPair, list[BoardPair], Riddle]) -> Union[BoardPair, list[BoardPair]]:
        func = functional.noiseInput
        # Make sure we are getting a riddle as input
        assert isinstance(inp, Riddle), "Please input a Riddle"
        # Find all colors that are not any input or output board
        all_bps = [i for i in inp.train] + [i for i in inp.test]
        unused_colors = set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        for bp in all_bps:
            unused_colors -= set(np.unique(bp.inp.np).tolist())
            unused_colors -= set(np.unique(bp.out.np).tolist())

        # Pick a random color (TODO allow for multiple color noise)
        color = random.choice(list(unused_colors))
        param_list = []
        param_list.append(color)
        if random.random() < self.p:
            get_params_method = functools.partial(
                self.get_params, noise_level=self.noise_level, noise_size=self.noise_size)
            return same_aug_for_all_pairs_helper(input, get_params_method=get_params_method, same_aug_for_all_pairs=self.same_aug_for_all_pairs, transformation_function=func, params_in=param_list)
        else:
            return input

    def __repr__(self):
        return self.__class__.__name__
