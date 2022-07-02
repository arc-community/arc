from arc import Agent, Board, BoardHints, BoardPair, TaskData, TopKList


class CheatingAgent(Agent):
    """An agent that uses hints to directly output the real solution."""

    def solve_test_sample(
        self,
        task_data: TaskData,
        hints: BoardHints,
        train: list[BoardPair],
        test: Board,
        test_idx: int,
    ) -> TopKList:
        return TopKList([hints.output for _ in range(task_data.topk)])


class EchoAgent(Agent):
    """An agent that simply copies the input."""

    def solve_test_sample(
        self,
        task_data: TaskData,
        hints: BoardHints,
        train: list[BoardPair],
        test: Board,
        test_idx: int,
    ) -> TopKList:
        return TopKList([test for _ in range(task_data.topk)])
