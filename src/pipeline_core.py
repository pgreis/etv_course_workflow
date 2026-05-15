import time
import random
from typing import List, Optional
from abc import ABC, abstractmethod

from src.models import PlaywrightPipelineContext

class PlaywrightPipelineStep(ABC):
    name : str
    add_wait_time: Optional[float] = random.randint(2, 3)

    @abstractmethod
    def execute(self, ctx: PlaywrightPipelineContext) -> PlaywrightPipelineContext:
        pass

class PlaywrightPipelineEngine:
    def __init__(self, steps: List[PlaywrightPipelineStep]):
        self.steps = steps

    def run(self, ctx: PlaywrightPipelineContext) -> PlaywrightPipelineContext:
        for step in self.steps:
            print(f"[STEP] {step.name}")

            start = time.time()
            try:
                ctx = step.execute(ctx)
            except Exception as e:
                ctx.error = f"{step.name}: {e}"
                break

            print(f"done in {(time.time()-start)*1000:.2f}ms")

        return ctx