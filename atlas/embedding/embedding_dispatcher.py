from atlas.embedding.openai_embedder import OpenAIEmbedder


def get_embedder(model_provider: str, model_type: str):
    if model_provider == 'openai':
        return OpenAIEmbedder(model_type)
    raise ValueError(f"No embedder implemented for model provider: {model_provider}")