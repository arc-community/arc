import numpy as np

from arc.interface import BoardPair


def noiseInput(inputPair: BoardPair, noise_level, noise_size, color) -> BoardPair:
    input_np_board = inputPair.input.np
    output_np_board = inputPair.output.np
    height, width = input_np_board.shape

    rng = np.random.default_rng(28)

    N = int(width * height * noise_level)
    nx = rng.integers(low=0, high=width, size=N)
    ny = rng.integers(low=0, high=height, size=N)
    noise = np.zeros((height, width))
    mask = np.ones((height, width))
    for x, y in zip(nx, ny):
        for i in range(x, x + noise_size[0]):
            for j in range(y, y + noise_size[1]):
                if (0 <= i < width) and (0 <= j < height):
                    noise[i, j] = color
                    mask[i, j] = 0
    res = mask * input_np_board + noise

    return BoardPair(input=res.tolist(), output=output_np_board.tolist())
