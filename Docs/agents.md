## Agentic systems - 2 Types
Workflows - are systems where LLM's and tools are orchestrated through predefined code paths
Agents - are systems where LLM's dynamically direct their oen processes and tool usage, maintaining control over how they accomplish tasks

### Workflows design patters:
1. Prompt chaining - decompose into fixed sub tasks
   ![img.png](media/img.png)
2. Routing - Direct an input into a specialized sub-task, ensuring separation of concerns <br>
   ![img_1.png](media/img_1.png)       
3. Parallelization - Breaking down tasks and running multiple subtasks concurrently
   ![img_2.png](media/img_2.png)
4. Orchestrator worker - Complex tasks are broken down dynamically and combined.
   ![img_3.png](media/img_3.png)
5. Evaluator-optimizer - LLM output is validated by another
   ![img_4.png](media/img_4.png)

### Agents Design pattern:
Are open-ended, have feedback loops and have no fixed path. Hence the output in unpredictable, have no clear path and time limit and may impact costs
    ![img_5.png](media/img_5.png)

Risks - Unpredictable path, Unpredictable output, Unpredictable costs
<br>Mitigations: Monitor (Langsmith), Guardrails ensure agents behave safely, consistently and within intended boundaries

### Agentic AI frameworks
**Base** - No framework, MCP
<br>**Level1** - OpenAI agents SDK, Crew AI  
**Level2** - LangGraph, AutoGen

##Openai Agent SDK
### Terminology
- Agents - represent LLMs
- Handoffs - represent interactions
- Guardrails - represent controls

Create an instance of agent, use 'with trace()' to track the agent and call 'runner.run()' to run the agent

### Vibe coding tips
- Good vibes - prompt well - ask for short answers and latest APIs
- Vibe but Verify - ask 2 llms the same question and verify
- Step up the vibe - ask to break down the request into smaller testable steps
- Vibe and validate - ask one LLM and get another LLM to check
- Vibe with variety - ask for multiple possible solutions to the same problem

Send email free - http://sendgrid.com
