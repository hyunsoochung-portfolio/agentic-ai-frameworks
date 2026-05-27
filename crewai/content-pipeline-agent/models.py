"""Shared Pydantic models for the content pipeline Flow and its scoring crews.

In the blog posts these models were declared inline in `main.py`. They are
factored out here so the helper crews (SeoCrew, ViralityCrew) can import `Score`
without creating a circular import with `main.py`.
"""

from typing import List

from pydantic import BaseModel


class BlogPost(BaseModel):
    title: str
    subtitle: str
    sections: List[str]


class Tweet(BaseModel):
    content: str
    hashtags: str


class LinkedInPost(BaseModel):
    hook: str
    content: str
    call_to_action: str


class Score(BaseModel):
    score: int = 0
    reason: str = ""
