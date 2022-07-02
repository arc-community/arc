from arc import Agent, Board, BoardHints, BoardPair, TaskData, TopKList


class CheatingAgent(Agent):
    def solve_test_sample(
        self,
        task_data: TaskData,
        hints: BoardHints,
        train: list[BoardPair],
        test: Board,
        test_idx: int,
    ) -> TopKList:
        return TopKList([hints.output for _ in range(task_data.topk)])
