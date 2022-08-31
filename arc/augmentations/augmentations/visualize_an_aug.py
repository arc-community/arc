import functools
import random
import time
from arc.utils.dataset import get_riddles
from augmentations import functional
from augmentations.classes.color import RandomColor
from augmentations.classes.helpers import same_aug_for_all_pairs_helper
from augmentations.classes.spatial import Direction, RandomDoubleInputBoard, RandomPadInputOnly, RandomPad, RandomReflect, RandomRotate, RandomSuperResolution
from augmentations.vis_helpers import plot_task
from augmentations.classes import RandomCropInputAndOuput
from torchvision import transforms

if __name__ == "__main__":
    train_riddles = get_riddles(["training"])
    riddle = train_riddles[1]
    transform = transforms.Compose([
        # transforms.RandomOrder([
        #     RandomCropInputAndOuput(1, same_aug_for_all_pairs=True),
        #     # RandomDoubleInputBoard(1, same_aug_for_all_pairs=True),
        # ]),
	    RandomColor(1, same_aug_for_all_pairs=True, include_0=False),
        # RandomRotate(1, True),
        # RandomReflect(0.5, True),
        # RandomSuperResolution(1, same_aug_for_all_pairs=False, stretch_axis=[Direction.both]),
        RandomPad(1, same_aug_for_all_pairs=True, pad_sizes=[1,2], pad_values=[0]),

        RandomPadInputOnly(1, same_aug_for_all_pairs=True, pad_sizes=[1,2], pad_values=[1,2,3,4,5,6,7,8,9]),
    ])
    riddle = transform(riddle)
    
    plot_task(riddle)
    time.sleep(100000)

