import json
import os
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
def get_bolna_payload(agent_config: dict, agent_prompts: dict, vector_id: str = None) -> dict:
    llm_provider = agent_config.get("llm_provider", "openai")
    payload = {
        "agent_config": {
            "agent_name": agent_config.get("agent_name"),
            "agent_type": "other",
            "agent_welcome_message": agent_config.get("agent_welcome_message"),
            "webhook_url": WEBHOOK_URL,
            "tasks": [
                {
                    "task_type": "conversation",
                    "tools_config": {
                        "llm_agent": {
                            "agent_type": "knowledgebase_agent" if vector_id else "simple_llm_agent",
                            "agent_flow_type": "streaming",
                            "llm_config": {
                                "provider": llm_provider,
                                "model": agent_config.get("llm_model", "gpt-4.1-mini"),
                                "max_tokens": agent_config.get("max_tokens", 150),
                                "temperature": agent_config.get("temperature", 0.1),
                                "agent_flow_type": "streaming",
                                "family": llm_provider,
                                "base_url": "https://api.anthropic.com" if llm_provider == "anthropic" else "https://api.openai.com/v1",
                                **({"rag_config": {
                                    "vector_store": {
                                        "provider": "LanceDB",
                                        "provider_config": {
                                            "vector_ids": [vector_id]
                                        }
                                    }
                                }} if vector_id else {})
                            }
                        },
                        "transcriber": {
                            "provider": "deepgram",
                            "model": "nova-3",
                            "language": agent_config.get("language", "hi"),
                            "stream": True
                        },
                        "synthesizer": {
                            "provider": "elevenlabs",
                            "provider_config": {
                                "voice": agent_config.get("voice", "Nila"),
                                "voice_id": agent_config.get("voice_id", "V9LCAAi4tTlqe9JadbCo"),
                                "model": "eleven_turbo_v2_5"
                            },
                            "stream": True
                        },
                        "input": {"provider": "plivo", "format": "wav"},
                        "output": {"provider": "plivo", "format": "wav"}
                    },
                    "toolchain": {
                        "execution": "parallel",
                        "pipelines": [["transcriber", "llm", "synthesizer"]]
                    },
                    "task_config": {
                        "hangup_after_silence": 10,
                        "call_terminate": 90
                    }
                }
            ]
        },
        "agent_prompts": agent_prompts
    }
    
    
    # print("VECTOR_ID:", vector_id)
    # print("AGENT_CONFIG:", agent_config)
    print("FULL BOLNA PAYLOAD:", json.dumps(payload, indent=2))
    return payload
    