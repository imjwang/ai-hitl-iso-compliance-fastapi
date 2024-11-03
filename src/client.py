import os
from restack_ai import Restack

connection_options = {
    "engine_id": os.getenv("RESTACK_ENGINE_ID"),
    "address": os.getenv("RESTACK_ENGINE_ADDRESS"),
    "api_key": os.getenv("RESTACK_ENGINE_API_KEY"),
}

client = Restack(connection_options)
