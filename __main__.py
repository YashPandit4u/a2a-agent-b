import uvicorn
import os

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import (
    OCIRealmFinderAgentExecutor,
)
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from starlette.requests import Request

class PrefixDispatcher:
    def __init__(self, app, prefix="/a2a"):
        self.app = app
        self.prefix = prefix

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith(self.prefix + "/"):
            # Rewrite path: /a2a/foo -> /foo
            scope = dict(scope)
            scope["path"] = scope["path"][len(self.prefix):]
            if not scope["path"]:
                scope["path"] = "/"
        await self.app(scope, receive, send)

if __name__ == '__main__':
    
    # agent_a_url = os.getenv('AGENT_A_URL')
    agent_b_url = os.getenv('AGENT_B_URL')

    skill = AgentSkill(
        id='oci_realm_finder',
        name='Returns OCI functioning realms and their status',
        description='just returns OCI functioning realms and their status',
        tags=['oci', 'realm', 'finder'],
        examples=['what are the functioning realms and their status?', 'what is the status of the OCI-1 realm?'],
    )

    public_agent_card = AgentCard(
        name='OCI Realm Finder Agent',
        description='Just a OCI realm finder agent',
        # url='http://localhost:9998/a2a/',
        # url = 'https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.amaaaaaay75uckqayzxhro3tqig45qhlv7lpeorfijnic3tw35dli6n6mbva/predict/a2a/',
        url = agent_b_url,
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
        supportsAuthenticatedExtendedCard=False,
    )

    request_handler = DefaultRequestHandler(
        agent_executor=OCIRealmFinderAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
    )

    # get underlying Starlette app
    app = server.build()

    # Wrap with PrefixDispatcher for /a2a
    prefix_app = PrefixDispatcher(app, prefix="/a2a")

    # Starlette app for /health
    starlette_app = Starlette()

    @starlette_app.route("/health")
    async def health(request: Request):
        return JSONResponse({"status": "ok"})

    # Compose both: /health handled by Starlette, everything else by prefix_app
    async def main_app(scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith("/health"):
            await starlette_app(scope, receive, send)
        else:
            await prefix_app(scope, receive, send)

    uvicorn.run(main_app, host='0.0.0.0', port=9998)



