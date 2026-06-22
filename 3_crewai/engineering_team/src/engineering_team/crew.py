from crewai import Agent, Crew, Process, Task, TaskOutput
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field
from typing import List
import json

class EngineeringSubTask(BaseModel):
    task_id: int = Field(description="Unique incremental sequence ID")
    title: str = Field(description="Component layer name")
    backend_instructions: str = Field(description="Functional requirements")
    expected_output: str = Field(description="What constitutes code completion")

class UnifiedProjectPlan(BaseModel):
    architecture_layers: List[EngineeringSubTask] = Field(Description="List of tasks identified")

class FileCode(BaseModel):
    file_code: str = Field(description="Code implementation fulfilling the layer functionality")
    file_name: str = Field(description="The name of the class containing the code")

class Project(BaseModel):
    files: List[FileCode]
def on_code_complete_callback(task_output: TaskOutput):
    """
    Triggers automatically when the backend engineer finishes executing.
    Extracts the JSON data and writes the files.
    """
    print("\n⚡ [Task Callback Triggered]: Backend Engineer completed execution. Writing python files...")

    # Safely parse the structured JSON from the Coder's output payload
    try:
        project = json.loads(task_output.raw)
        print(f"coder task output - {project}")
    except Exception:
        # Fallback if raw JSON formatting requires sanitization
        project = json.loads(task_output.json_dict)
    print(len(project['files']))

    for code in project['files']:
        class_name = code['file_name']
        with open(f"output/{class_name}.py", "w") as b_file:
            b_file.write(code['file_code'])

@CrewBase
class EngineeringTeam():
    """EngineeringTeam crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    #@agent
    def design_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['design_lead'],
            verbose=True
        )

    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['engineering_lead'],
            verbose=True
        )

    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_engineer'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=250,
            max_retry_limit=5
        )

    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['frontend_engineer'],
            verbose=True
        )

    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_engineer'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=90,
            max_retry_limit=5
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task'],
        )

    #@task
    def plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['plan_task'],
            output_pydantic=UnifiedProjectPlan
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task'],
            output_pydantic=Project,
            callback=on_code_complete_callback
        )

    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_task'],
        )

    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the EngineeringTeam crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
