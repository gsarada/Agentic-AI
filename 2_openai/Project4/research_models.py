from pydantic import BaseModel

class SearchItem(BaseModel):
    reason: str
    "Reason for why this search is important for the user query"
    search_query: str
    "The query to search for"

class SearchPlan(BaseModel):
    query_list: list[SearchItem]
    "The list of search queries to be executed"

class SearchQueries(BaseModel):
    query_list: list[str]
class Report(BaseModel):
    short_summary: str
    "A short 2-3 sentences summary of the topic"

    markdown_report: str
    "The final report"

    followup_resources: list[str]
    "Suggested resources to research further"
