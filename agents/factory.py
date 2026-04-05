from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from config.settings import settings

class BaseAgent:
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.llm = self._get_llm()

    def _get_llm(self):
        if settings.LLM_PROVIDER == "openai":
            return ChatOpenAI(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL, streaming=True)
        elif settings.LLM_PROVIDER == "anthropic":
            return ChatAnthropic(api_key=settings.ANTHROPIC_API_KEY, model=settings.ANTHROPIC_MODEL, streaming=True)
        elif settings.LLM_PROVIDER == "groq":
            return ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL, streaming=True)
        elif settings.LLM_PROVIDER == "google":
            # Some versions of LangChain default to v1beta, try v1 for better compatibility
            return ChatGoogleGenerativeAI(
                google_api_key=settings.GOOGLE_API_KEY, 
                model=settings.GOOGLE_MODEL, 
                streaming=True,
                convert_system_message_to_human=True # Helpful for some Gemini models
            )
        else:
            return Ollama(base_url=settings.OLLAMA_BASE_URL, model=settings.LLM_MODEL)

    def get_prompt_template(self, system_message: str):
        global_instructions = "You are part of the HYPER-Agent system. You have a shared memory and history of past tasks. Use the provided context to inform your responses."
        # Escape curly braces for LangChain prompt template
        clean_system = system_message.replace("{", "{{").replace("}", "}}")
        return ChatPromptTemplate.from_messages([
            ("system", f"Role: {self.role}\nGoal: {self.goal}\nBackstory: {self.backstory}\n\n{global_instructions}\n\n{clean_system}"),
            ("human", "{input}")
        ])

    def call(self, input_text: str, context: Optional[str] = None, streaming_cb: Optional[Any] = None) -> str:
        prompt = self.get_prompt_template(context or "Use the provided context to answer.")
        
        try:
            return self._execute_call(prompt, self.llm, input_text, streaming_cb)
        except Exception as e:
            err_str = str(e).lower()
            if any(x in err_str for x in ["429", "rate_limit", "404", "not_found", "quota"]):
                # FALLBACK LOGIC
                backup_provider = "groq" if settings.LLM_PROVIDER == "google" else "google"
                print(f"\n[bold yellow][SYSTEM]: Primary failed ({err_str[:40]}...). Trying backup: {backup_provider}...[/bold yellow]")
                
                # Setup backup LLM
                old_provider = settings.LLM_PROVIDER
                settings.LLM_PROVIDER = backup_provider
                
                # If falling back to Groq, try to use the faster/free-er 8B model specifically if the 70B failed
                old_groq_model = settings.GROQ_MODEL
                if backup_provider == "groq" and "70b" in old_groq_model:
                    settings.GROQ_MODEL = "llama3-8b-8192"
                
                try:
                    backup_llm = self._get_llm()
                    return self._execute_call(prompt, backup_llm, input_text, streaming_cb)
                except Exception as e2:
                    # Final attempt: try Groq 8B regardless of previous set if we haven't already
                    if backup_provider != "groq":
                         try:
                            print(f"\n[bold red][SYSTEM]: Gemini also failed. Emergency fallback to Groq 8B...[/bold red]")
                            settings.LLM_PROVIDER = "groq"
                            settings.GROQ_MODEL = "llama-3.1-8b-instant"
                            emergency_llm = self._get_llm()
                            return self._execute_call(prompt, emergency_llm, input_text, streaming_cb)
                         except Exception as e3:
                            raise e3
                    raise e2 # Re-raise fallback error if all fallbacks fail
                finally:
                    settings.LLM_PROVIDER = old_provider
                    settings.GROQ_MODEL = old_groq_model
            else:
                raise e

    def _execute_call(self, prompt, llm, input_text, streaming_cb):
        chain = prompt | llm
        if streaming_cb:
            full_response = ""
            for chunk in chain.stream({"input": input_text}):
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                streaming_cb(content)
                full_response += content
            return full_response
        else:
            response = chain.invoke({"input": input_text})
            return response.content if hasattr(response, "content") else str(response)

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Lead Architect & Planner",
            goal="Dynamically route the HYPER-Agent team for optimal task resolution.",
            backstory="You are the strategic brain. \n1. If a user asks a pure social greeting (e.g., 'hi'), include 'ROUTE: CONVERSATION'. \n2. DYNAMIC ROUTING: You must decide if the task needs active web research, active coding, or both. \n- If the user asks for ANY general knowledge, links, URLs, or real-time data, YOU MUST include EXACTLY the tag '[REQUIRE: RESEARCH]'.\n- If the user asks for code, include EXACTLY the tag '[REQUIRE: CODER]'. \n- If both are needed, include both tags. Provide clear instructions. Do not let the team hallucinate."
        )

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Intelligence Researcher",
            goal="Provide deep, data-driven context for the team.",
            backstory="You find facts and technical specifications. If you find multiple meanings for a term (like VLM), provide all of them (e.g. Vision Language Models vs PGPEX-VLM). If no data is found, report MISSING_DATA."
        )

class CodingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Systems Engineer & Coder",
            goal="Translate research findings into functional code and simulations.",
            backstory="You create pristine proof-of-concept Python scripts. Focus purely on writing functional, safe logic."
        )

class DataAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Data Intelligence Analyst",
            goal="Extract deep insights from complex datasets.",
            backstory="You specialize in finding patterns and anomalies in data, providing the team with clear visualizations and statistical proof."
        )

class ExecutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Verification & Test Engineer",
            goal="Validate all code outputs in a secure local environment.",
            backstory="You are a meticulous tester. You run the Coder's scripts, verify their output, and report any errors back to the team for revision."
        )

class EvaluatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Lead Editor & Quality Gatekeeper",
            goal="Synthesize all agent outputs into a premium final response.",
            backstory="You are the final reviewer. You synthesize Researcher findings and Coder implementations into a single, cohesive response. STRICT RULES: \n1. If the user asks who made you or how you work, you must state that you were made by 'Suman Kar'. You are a collective of 6 agents (Planner, Researcher, Coder, Data Analyst, Executor, Evaluator).\n2. DO NOT adopt 'Suman Kar' as your own name or sign off with it.\n3. Never hallucinate links or data if the Researcher provided none. State that you lack real-time data."
        )

class AgentFactory:
    @staticmethod
    def get_agent(role: str) -> BaseAgent:
        agents = {
            "planner": PlannerAgent,
            "research": ResearchAgent,
            "coding": CodingAgent,
            "data": DataAgent,
            "executor": ExecutorAgent,
            "evaluator": EvaluatorAgent
        }
        return agents[role.lower()]()
