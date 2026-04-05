from typing import TypedDict, Annotated, List, Dict, Any, Union
from langgraph.graph import StateGraph, END
from agents.factory import AgentFactory
from tools.web import tools
from tools.plugins import plugins
from memory.database import ExperienceDatabase
from memory.vector import VectorMemory

# Define the state for the graph
class AgentState(TypedDict):
    input: str
    plan: Dict[str, Any]
    research_results: str
    code: str
    execution_result: Dict[str, Any]
    communication_result: str
    evaluation: Dict[str, Any]
    improvement_strategy: str
    current_agent: str
    messages: List[Dict[str, str]]

from rich.console import Console
from rich.panel import Panel
from langchain.memory import ConversationBufferMemory

class HYPERGraph:
    def __init__(self):
        self.db = ExperienceDatabase()
        self.vector_store = VectorMemory()
        self.console = Console()
        self.memory = ConversationBufferMemory(return_messages=False)
        self.graph = self._build_graph()

    def _safe_print(self, text, style=None, end="\n"):
        """Ensures text is safe for Windows terminal encoding."""
        try:
            clean_text = text.encode('ascii', 'ignore').decode('ascii')
            self.console.print(clean_text, style=style, end=end)
        except Exception:
            pass

    def _planner_node(self, state: AgentState):
        self.console.print("\n[bold purple][PLANNER]: Orchestrating team strategy...[/bold purple]")
        planner = AgentFactory.get_agent("planner")
        
        all_history = self.db.get_recent_experiences(limit=5)
        history_context = "\n".join([f"- Task: {h['query']}\n  Result: {h['result'][:150]}..." for h in all_history])
        
        chat_history = self.memory.load_memory_variables({}).get("history", "")
        
        full_input = f"CONTEXT:\n{history_context}\n\nRECENT CHAT HISTORY:\n{chat_history}\n\nUSER TASK: {state['input']}"
        response = planner.call(full_input)
        state["plan"] = {"instructions": response}
        return state

    def _researcher_node(self, state: AgentState):
        self.console.print("\n[bold cyan][RESEARCHER]: Architecting intelligence gathering...[/bold cyan]")
        
        # Smart Query Generation
        researcher = AgentFactory.get_agent("research")
        query_expansion_prompt = (
            f"Given the user prompt: '{state['input']}', generate 3 diverse search queries. "
            f"If the prompt contains acronyms (like VLM, RAG, etc.), include queries that specifically check for "
            f"Artificial Intelligence, Machine Learning, or Software Engineering contexts. "
            f"Format as a comma-separated list."
        )
        expanded_queries = researcher.call(query_expansion_prompt).split(",")
        
        all_results = []
        # Multi-step search
        for q in [state['input']] + [ext.strip() for ext in expanded_queries]:
            self.console.print(f"   [dim]Querying: {q.strip()}[/dim]")
            res = tools.web_search(q.strip())
            if res:
                all_results.extend(res)
                if len(all_results) >= 5: break

        if not all_results:
            self.console.print("   [bold red]Alert: No real-time data found for this task.[/bold red]")
            state["research_results"] = "MISSING_DATA: No research results found. DO NOT hallucinate. Request user clarification."
        else:
            # Format results into a clean string
            formatted_res = "\n\n".join([f"Source: {r['title']}\nSnippet: {r['snippet']}" for r in all_results[:5]])
            state["research_results"] = formatted_res
            snippet = (formatted_res[:250] + "...") if len(formatted_res) > 250 else formatted_res
            self._safe_print(f"   [dim]Validated Findings: {snippet}[/dim]")
        
        return state

    def _coder_node(self, state: AgentState):
        self.console.print("\n[bold yellow][CODER]: Building implementation/simulation...[/bold yellow]")
        coder = AgentFactory.get_agent("coding")
        
        # Anti-Hallucination Guard
        if "MISSING_DATA" in state["research_results"]:
            state["code"] = "ERROR: Insufficient research context provided. Coding halted to prevent hallucination."
            self.console.print("   [bold red]Alert: Coding halted - no research data to build upon.[/bold red]")
            return state

        context = f"Research: {state['research_results']}\nGoal: {state['input']}"
        code = coder.call(state["input"], context=context)
        
        if "```" in code:
            preview = code.split("```")[1].split("```")[0][:150] + "..."
            self._safe_print(f"   [dim]Code generated: {preview}[/dim]")
        
        state["code"] = code
        return state

    def _executor_node(self, state: AgentState):
        self.console.print("\n[bold green][EXECUTOR]: Validating system integrity...[/bold green]")
        if "ERROR:" in state["code"]:
            state["execution_result"] = {"error": "No code to execute due to missing context."}
            return state

        code = state["code"]
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
        execution_result = tools.python_code_execution(code)
        state["execution_result"] = execution_result
        self.console.print(f"   [dim]Logs captured (Exit Code: {execution_result.get('exit_code', 'N/A')})[/dim]")
        return state

    def _communicator_node(self, state: AgentState):
        lower_input = state["input"].lower()
        if not any(key in lower_input for key in ["whatsapp", "email", "gmail", "telegram"]):
            state["communication_result"] = "No communication requested."
            return state
            
        self.console.print("\n[bold cyan][COMMUNICATOR]: Executing cross-platform task...[/bold cyan]")
        comm = AgentFactory.get_agent("communicator")
        
        # Decide which tool to use
        decision_prompt = (
            f"User request: '{state['input']}'. "
            f"You MUST extract the target (phone number or email) and the service (WhatsApp, Email, or Telegram). "
            f"If the target is a name, just return the name. "
            f"RETURN ONLY the formatted string 'SERVICE|TARGET|MESSAGE' and NOTHING ELSE. No preamble, no explanation. "
            f"Example: 'WhatsApp|John|Hello!'"
        )
        decision = comm.call(decision_prompt)
        
        try:
            parts = decision.split("|")
            if len(parts) < 2:
                state["communication_result"] = f"Error: Could not parse target from '{decision}'."
                return state
                
            service = parts[0].strip().capitalize()
            target_name = parts[1].strip() if len(parts) > 1 else "Unknown"
            msg = parts[2].strip() if len(parts) > 2 else state["input"]
            
            # Resolve name to actual target (if applicable)
            target = plugins.resolve_contact(target_name)
            if target_name != target:
                self._safe_print(f"   [dim]Resolved {target_name} -> {target}[/dim]")
            
            if "Whatsapp" in service:
                state["communication_result"] = plugins.send_whatsapp(target, msg)
            elif "Email" in service or "Gmail" in service:
                if "check" in lower_input or "read" in lower_input:
                    state["communication_result"] = plugins.check_emails()
                else:
                    state["communication_result"] = plugins.send_email(target, "Notification from HYPER-Agent", msg)
            elif "Telegram" in service:
                state["communication_result"] = plugins.send_telegram(target, msg)
            elif "Twitter" in service or "Tweet" in service:
                state["communication_result"] = plugins.send_tweet(msg)
            else:
                state["communication_result"] = f"Unknown service: {service}"
        except Exception as e:
            state["communication_result"] = f"Error in communicator: {str(e)}"
        
        self.console.print(f"   [dim]Result: {state['communication_result']}[/dim]")
        return state

    def _evaluator_node(self, state: AgentState):
        self.console.print("\n" + "=" * 80, style="bold magenta")
        self.console.print("[bold magenta][EVALUATOR]: Synthesizing Final Intelligence...[/bold magenta]")
        self.console.print("=" * 80 + "\n", style="bold magenta")
        evaluator = AgentFactory.get_agent("evaluator")
        
        chat_history = self.memory.load_memory_variables({}).get("history", "")
        
        context = (
            f"RECENT CHAT HISTORY:\n{chat_history}\n\n"
            f"RESEARCH FINDINGS: {state['research_results']}\n\n"
            f"CODE IMPLEMENTATION: {state['code']}\n\n"
            f"EXECUTION LOGS: {state['execution_result']}\n\n"
            f"COMMUNICATION LOGS: {state['communication_result']}"
        )
        
        def stream_cb(token):
            self._safe_print(token, style="bold white", end="")
            
        plan_text = state["plan"].get("instructions", "").lower()
        if "route: conversation" in plan_text:
            sys_prompt = "You are a helpful conversational AI. Formulate a direct, warm conversational response to the user's greeting or simple inquiry. DO NOT mention anything about missing research or missing data."
        else:
            sys_prompt = "Synthesize a final response. If research is missing or states MISSING_DATA, inform the user you couldn't find real-time data for that specific term. DO NOT guess. Report communication results clearly if any."
        evaluation = evaluator.call(
            f"USER TASK: {state['input']}. {sys_prompt}", 
            context=context, 
            streaming_cb=stream_cb
        )
        self.console.print("\n")
        state["evaluation"] = {"feedback": evaluation, "score": 1.0}
        return state

    def _improvement_node(self, state: AgentState):
        self.console.print("\n[bold blue][IMPROVER]: Archiving Experience...[/bold blue]", end=" ")
        improver = AgentFactory.get_agent("improvement")
        context = f"Task: {state['input']}\nFinal Result summary: {state['evaluation']['feedback'][:100]}"
        strategy = improver.call("Distill this run into a single sentence strategy.", context=context)
        state["improvement_strategy"] = strategy
        
        self.db.add_experience(
            task_type="full_team_collaboration",
            query=state["input"],
            plan=state["plan"],
            result=state["evaluation"]["feedback"],
            score=1.0,
            feedback="Full team collaboration complete.",
            strategy=strategy
        )
        return state

    def _build_graph(self):
        from langgraph.graph import StateGraph, END
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("coder", self._coder_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("communicator", self._communicator_node)
        workflow.add_node("evaluator", self._evaluator_node)
        workflow.add_node("improvement", self._improvement_node)
        
        # Simple linear chain for "all agents working together"
        workflow.set_entry_point("planner")
        
        # Conditional routing from planner
        def router(state: AgentState):
            plan_text = state["plan"].get("instructions", "").lower()
            if "route: conversation" in plan_text:
                return "evaluator"
            return "researcher"
            
        workflow.add_conditional_edges(
            "planner", 
            router,
            {"evaluator": "evaluator", "researcher": "researcher"}
        )
        
        workflow.add_edge("researcher", "coder")
        workflow.add_edge("coder", "executor")
        workflow.add_edge("executor", "communicator")
        workflow.add_edge("communicator", "evaluator")
        workflow.add_edge("evaluator", "improvement")
        workflow.add_edge("improvement", END)
        
        return workflow.compile()

    def run(self, input_text: str):
        initial_state = {
            "input": input_text,
            "plan": {},
            "research_results": "",
            "code": "",
            "execution_result": {},
            "communication_result": "",
            "evaluation": {},
            "improvement_strategy": "",
            "current_agent": "planner",
            "messages": []
        }
        result = self.graph.invoke(initial_state)
        
        # Save to buffer memory
        final_response = result.get("evaluation", {}).get("feedback", "")
        if not final_response:
            final_response = "Execution completed without clear evaluator feedback."
        self.memory.save_context({"input": input_text}, {"output": final_response})
        
        return result
