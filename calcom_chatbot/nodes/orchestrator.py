from langchain_openai import ChatOpenAI
from calcom_chatbot.state import AgentState
from calcom_chatbot.utils.config import get_openai_api_key
from calcom_chatbot.prompts.templates import ORCHESTRATOR_PROMPT, SOLVER_PROMPT
from datetime import datetime, timezone
import logging
import re

logger = logging.getLogger(__name__)


async def orchestrator_node(state: AgentState) -> AgentState:
    """
    Plan-and-Execute agent for multi-step tasks.
    
    Architecture:
    1. Planner: LLM generates task DAG with variable references
    2. Executor: Executes tasks, saves results in variables
    3. Solver: LLM integrates all results into final answer
    """
    user_query = state["user_query"]
    messages = state.get("messages", [])
    
    llm = ChatOpenAI(
        api_key=get_openai_api_key(),
        model="gpt-4",
        temperature=0
    )
    
    conversation_history = "\n".join(messages[-5:]) if messages else ""
    
    try:
        # ============ PLANNER ============
        planner_prompt = ORCHESTRATOR_PROMPT.format(
            conversation_history=conversation_history,
            user_query=user_query,
            current_time=datetime.now(timezone.utc).isoformat()
        )
        
        plan_response = llm.invoke(planner_prompt)
        plan_text = plan_response.content.strip()
        
        logger.info(f"Planner Output: {plan_text[:200]}...")
        
        # Check if plan was generated
        if not plan_text.startswith("PLAN:"):
            # Planner is asking for more info
            state["final_response"] = plan_text
            return state
        
        # Parse plan into tasks
        tasks = parse_plan(plan_text.replace("PLAN:", "").strip())
        
        if not tasks:
            state["final_response"] = "I couldn't create a valid execution plan. Could you be more specific?"
            return state
        
        logger.info(f"Plan parsed: {len(tasks)} tasks")
        
        # ============ EXECUTOR ============
        # Execute tasks and save results in variables (like ReWOO)
        variables = {}  # E1, E2, E3 etc.
        
        for i, task in enumerate(tasks, 1):
            task_id = f"E{i}"
            logger.info(f"Executing {task_id}: {task['action']} {task['params']}")
            
            # Execute task
            result = await execute_task(task, state, variables)
            variables[task_id] = result
            
            logger.info(f"{task_id} completed: {result[:100]}...")
        
        # ============ SOLVER ============
        # Use LLM to integrate all results into final answer
        solver_prompt = SOLVER_PROMPT.format(
            user_query=user_query,
            task_results=format_task_results(tasks, variables)
        )
        
        solver_response = llm.invoke(solver_prompt)
        state["final_response"] = solver_response.content.strip()
        
    except Exception as e:
        logger.error(f"❌ Orchestrator error: {e}")
        state["final_response"] = f"Error processing multi-step request: {str(e)}"
    
    return state


def parse_plan(plan_text: str) -> list:
    """Parse LLM plan into task list (supports E1:/1. formats)."""
    tasks = []
    for line in plan_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Remove "E1:" or "1." prefix
        line = re.sub(r'^(E\d+:|[\d]+\.)\s*', '', line)
        
        # Parse action(params) or just action
        if '(' in line:
            action = line.split('(')[0].strip()
            params_str = line.split('(')[1].split(')')[0]
            params = parse_params(params_str)
        else:
            action = line.strip()
            params = {}
        
        tasks.append({"action": action, "params": params})
    
    return tasks


def parse_params(params_str: str) -> dict:
    """Parse 'key=value, key2=value2' string into dict."""
    params = {}
    for param in params_str.split(','):
        param = param.strip()
        if '=' in param:
            key, value = param.split('=', 1)
            params[key.strip()] = value.strip()
    return params


def replace_variables(params: dict, variables: dict) -> dict:
    """Replace #E1 references with actual values."""
    resolved = {}
    for key, value in params.items():
        if isinstance(value, str) and value.startswith('#E'):
            var_name = value[1:]  # Remove '#' prefix
            resolved[key] = variables.get(var_name, value)
        else:
            resolved[key] = value
    return resolved


async def execute_task(task: dict, state: AgentState, variables: dict) -> str:
    """Execute a single task using the appropriate node."""
    from calcom_chatbot.nodes.list_events import list_events_node
    from calcom_chatbot.nodes.get_slots import get_slots_node
    from calcom_chatbot.nodes.book_meeting import book_meeting_node
    from calcom_chatbot.nodes.cancel_meeting import cancel_meeting_node
    from calcom_chatbot.nodes.reschedule_meeting import reschedule_meeting_node
    
    # Map actions to node functions
    node_map = {
        "list_events": list_events_node,
        "get_slots": get_slots_node,
        "book_meeting": book_meeting_node,
        "cancel_meeting": cancel_meeting_node,
        "reschedule_meeting": reschedule_meeting_node
    }
    
    action = task['action']
    params = replace_variables(task['params'], variables)
    
    if action not in node_map:
        return f"Unknown action: {action}"
    
    # Create task state and execute
    task_state = AgentState(
        user_query=format_task_query(action, params),
        messages=state.get("messages", []),
        intent=action,
        confidence=1.0,
        booking_details=None,
        api_response=None,
        final_response=""
    )
    
    result_state = await node_map[action](task_state)
    return result_state.get("final_response", "No result")


def format_task_query(action: str, params: dict) -> str:
    """Format task into a natural language query for the node."""
    if action == "list_events":
        return "show my events"
    elif action == "get_slots":
        date = params.get("date", "tomorrow")
        return f"what times are available on {date}"
    elif action == "book_meeting":
        date = params.get("date", "")
        time = params.get("time", "")
        name = params.get("name", "")
        email = params.get("email", "")
        notes = params.get("notes", "")
        
        # Format as explicit BOOKING_READY to skip LLM parsing in book_meeting_node
        query = f"BOOKING_READY: date={date}, time={time}, name={name}, email={email}"
        if notes:
            query += f", notes={notes}"
        return query
    elif action == "cancel_meeting":
        return "cancel my meeting"
    elif action == "reschedule_meeting":
        return "reschedule my meeting"
    else:
        return action


def format_task_results(tasks: list, variables: dict) -> str:
    """Format task results for Solver LLM."""
    results = []
    for i, task in enumerate(tasks, 1):
        task_id = f"E{i}"
        action = task['action']
        params = task.get('params', {})
        result = variables.get(task_id, "No result")
        results.append(f"{task_id}: {action}({params})\nResult: {result}\n")
    return "\n".join(results)

