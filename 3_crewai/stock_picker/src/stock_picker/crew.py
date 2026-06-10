from pydantic import BaseModel, Field
from crewai import Agent, Crew, Process, Task, Memory
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerpApiGoogleSearchTool
from tools.email_sender import EmailSenderTool


class TrendingCompany(BaseModel):
    """A company that is in the news and attracting attention"""
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason this company is trending in the news")

class TrendingCompanyList(BaseModel):
    companies: list[TrendingCompany] = Field(description="List of companies trending in the news")

class TrendingCompanyResearch(BaseModel):
    """Detailed research on a company"""
    name: str = Field(description="Company name")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth prospects")
    investment_potential: str = Field(description="Investment potential and suitability for investment")
    risk_factor: str = Field(description="Potential risks and challenges")
    financial_health: str = Field(description="Financial health and key metrics")
    valuation: str = Field(description="Valuation metrics and analysis")
    key_growth_drivers: str = Field(description="Key growth drivers and competitive advantage")

class TrendingCompanyResearchList(BaseModel):
    companies_details: list[TrendingCompanyResearch] = Field(description="A list of trending companies with financial details")

@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['trending_company_finder'],  tools=[SerpApiGoogleSearchTool()],)

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'],  tools=[SerpApiGoogleSearchTool()])

    @agent
    def stock_picker(self) -> Agent:
        return Agent(config=self.agents_config['stock_picker'])


    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'],
            output_pydantic=TrendingCompanyList
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'],
            output_pydantic=TrendingCompanyResearchList
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
            tools=[EmailSenderTool()]
        )

    @crew
    def crew(self) -> Crew:

        manager = Agent(config=self.agents_config['manager'])
        """Creates the StockPicker crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            verbose=True,
            #memory=True,
            #embedder={"provider": "ollama", "config": {"model_name": "text-embedding-3-small"},},
            manager_agent=manager
        )
