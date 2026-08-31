"""
A curated list of common tech / AI-ML skill keywords used for lightweight
skill extraction via keyword matching (no heavy NLP model required).

This is intentionally simple and easy to extend - just add strings to
COMMON_SKILLS. Matching is case-insensitive and uses word boundaries so
"R" doesn't match inside "React", etc.
"""

COMMON_SKILLS = [
    # Languages
    "python", "java", "c++", "c#", "javascript", "typescript", "go", "rust",
    "r", "sql", "scala", "kotlin", "swift", "php", "ruby",
    # ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "reinforcement learning", "tensorflow", "pytorch",
    "keras", "scikit-learn", "sklearn", "xgboost", "lightgbm", "opencv",
    "huggingface", "transformers", "llm", "large language models",
    "generative ai", "genai", "langchain", "rag", "prompt engineering",
    "fine-tuning", "embeddings", "vector database", "pinecone", "faiss",
    "chromadb", "spacy", "nltk", "pandas", "numpy", "matplotlib", "seaborn",
    # Web / API
    "fastapi", "flask", "django", "rest api", "graphql", "react", "angular",
    "vue", "node.js", "express", "html", "css",
    # Data / infra
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "ci/cd",
    "linux", "airflow", "spark", "hadoop", "kafka", "mongodb", "postgresql",
    "mysql", "redis", "elasticsearch",
    # General SWE
    "data structures", "algorithms", "oop", "microservices", "agile", "scrum",
    "unit testing", "pytest", "system design",
]
