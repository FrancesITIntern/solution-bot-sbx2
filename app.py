import os
import time
import json
import chainlit as cl
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MessageRole
from datetime import datetime

# Initialize Azure AI Project Client
client = AIProjectClient(
    endpoint=os.getenv("AIPROJECT_ENDPOINT"),
    subscription_id=os.getenv("AZ_SUBSCRIPTION_ID"),
    resource_group_name=os.getenv("AZ_RESOURCE_GROUP"),
    project_name=os.getenv("AZ_PROJECT_NAME"),
    credential=DefaultAzureCredential()
)

# Load agent ID
AGENT_ID = os.getenv("AZ_AGENT_ID")


@cl.on_chat_start
async def on_chat_start():
    try:
        # Create a new thread
        thread = client.agents.create_thread()
        cl.user_session.set("thread_id", thread.id)

        # Initial system message (optional)
        client.agents.create_message(
            thread_id=thread.id,
            role=MessageRole.USER,
            content="You are a helpful assistant named Solution Bot."
        )

        # Try to fetch agent name
        agent_name = "Solution Bot"
        try:
            agent = client.agents.get_agent(agent_id=AGENT_ID)
            if agent and agent.name:
                agent_name = agent.name
        except Exception:
            pass

        await cl.Message(f"✅ Connected to Azure Agent: **{agent_name}** (ID: {AGENT_ID})").send()

    except Exception as e:
        await cl.Message(f"❌ Failed to connect to Azure Agent.\nError: {str(e)}").send()
        if hasattr(e, "response"):
            print("Azure error response:", e.response.text)


@cl.on_message
async def on_message(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")
    msg = await cl.Message("💡 Thinking...", author="Solution Bot").send()

    try:
        # Step 1: Send the user's message
        client.agents.create_message(
            thread_id=thread_id,
            role=MessageRole.USER,
            content=message.content
        )

        # Step 2: Create and wait for run to complete
        run = client.agents.create_run(thread_id=thread_id, agent_id=AGENT_ID)
        run_id = run.id

        while run.status in ("queued", "in_progress", "requires_action"):
            time.sleep(1)
            run = client.agents.get_run(thread_id=thread_id, run_id=run_id)

        if run.status == "failed":
            raise RuntimeError(run.last_error)

        # Step 3: Retrieve messages generated during this run
        messages = client.agents.list_messages(thread_id=thread_id)

        # ✅ Step 4: Only look for AGENT replies generated during this run
        relevant_replies = [
            "".join(c.text.value for c in m.content if hasattr(c.text, "value"))
            for m in messages.data
            if m.role == MessageRole.AGENT and m.run_id == run_id and m.content
        ]

        # Grab the most recent relevant reply (should be just one)
        reply = relevant_replies[-1] if relevant_replies else None

        if not reply:
            raise RuntimeError("No reply received from agent.")

        msg.content = reply
        await msg.update()

    except Exception as e:
        await cl.Message(content=f"❌ Error: {e}").send()
        if hasattr(e, "response"):
            print("Azure error response:", e.response.text)
