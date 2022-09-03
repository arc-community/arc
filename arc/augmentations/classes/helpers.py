import functools
import random
from typing import Union, Callable
from arc.interface import BoardPair, Riddle

def same_aug_for_all_pairs_helper(input:Union[BoardPair,list[BoardPair],Riddle], transformation_function:Callable, same_aug_for_all_pairs:bool, get_params_method=None, params_in=None):
    if type(input) == list:
        return _same_aug_boardpair_list_helper(input, transformation_function, same_aug_for_all_pairs, get_params_method, params_in)
    elif type(input) == BoardPair:
            assert params_in is not None or get_params_method is not None, "params_in or get_params_method must be provided"
            params = get_params_method(seed=random.random()) if params_in is None else params_in
            return transformation_function(input,*params)
    elif type(input) == Riddle:
        all_bps = [i for i in input.train] + [i for i in input.test]
        train_len = len(input.train)
        transformed_bps = _same_aug_boardpair_list_helper(all_bps, transformation_function, same_aug_for_all_pairs, get_params_method, params_in)
        input.train, input.test = transformed_bps[:train_len],transformed_bps[train_len:]
        return input
    else:
        raise Exception("Input must be a BoardPair, list of BoardPairs or a riddle")


def _same_aug_boardpair_list_helper(input:list[BoardPair], transformation_function:Callable, same_aug_for_all_pairs:bool, get_params_method=None, params_in=None):
    if same_aug_for_all_pairs:
        assert params_in is not None or get_params_method is not None, "params_in or get_params_method must be provided"
        if get_params_method is not None:
            params = get_params_method( seed=random.random())
            if params_in is not None:
                params = list(params)
                params = params + params_in
                params = tuple(params)
        else:
            params = params_in
        params = params if hasattr(params, "__iter__") else [params]
        output = [transformation_function(input_pair,*params) for input_pair in input]
        return output
    else:
        assert get_params_method is not None, "get_params_method must be provided if same_aug_for_all_pairs is False"
        output = []
        for i in range(len(input)):
            params = get_params_method(seed=random.random())
            output.append(transformation_function(input[i],*params))
        return output

def p_and_same_aug_helper(input, func, p, same_aug_for_all_pairs, get_params, **params):
        if random.random() < p:
            get_params_method = functools.partial(get_params, **params)
            return same_aug_for_all_pairs_helper(input, func, same_aug_for_all_pairs, get_params_method)
        else:
            return input
