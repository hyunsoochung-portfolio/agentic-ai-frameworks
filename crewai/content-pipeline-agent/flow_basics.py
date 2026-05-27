"""Standalone demo of CrewAI Flow primitives (from the first Flow post).

Shows @start / @listen / @router and the and_ / or_ combinators, plus a typed
Flow state via a Pydantic BaseModel. Run with: python flow_basics.py
"""

from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel


class MyFirstFlowState(BaseModel):
    user_id: int = 1
    is_admin: bool = False


# Using a typed (Pydantic) state is safer than a plain dict.
class MyFirstFlow(Flow[MyFirstFlowState]):
    # @start()
    # def first(self):  # error: state is not a dict here
    #     self.state["whatever"] = 1
    #     print('hello')
    @start()
    def first(self):
        print(self.state.user_id)
        print("hello")

    @listen(first)
    def second(self):
        self.state.user_id = 2
        print("world")

    @listen(first)
    def third(self):
        print(":")

    @listen(and_(second, third))
    def final(self):
        print(":)")

    @router(final)
    def route(self):
        if self.state.is_admin:
            return "even"
        else:
            return "odd"

    @listen("even")
    def handle_even(self):
        print("even")

    @listen("odd")
    def handle_odd(self):
        print("odd")


if __name__ == "__main__":
    flow = MyFirstFlow()
    flow.kickoff()
