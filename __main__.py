import uvicorn

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


if __name__ == '__main__':
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
        url='http://localhost:9998/',
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

    uvicorn.run(server.build(), host='0.0.0.0', port=9998)



