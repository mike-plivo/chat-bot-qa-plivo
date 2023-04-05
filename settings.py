GIT_REPOS_DIR="data/git_repos"
GIT_REPO_URLS = [
        'git@github.com:plivo/plivo-python.git',
        'git@github.com:plivo/plivo-java.git',
        'git@github.com:plivo/plivo-ruby.git',
        'git@github.com:plivo/plivo-dotnet.git',
        'git@github.com:plivo/plivo-php.git',
        'git@github.com:plivo/plivo-node.git',
        'git@github.com:plivo/plivo-examples-python.git',
        'git@github.com:plivo/plivo-examples-java.git',
        'git@github.com:plivo/plivo-examples-ruby.git',
        'git@github.com:plivo/plivo-examples-dotnet.git',
        'git@github.com:plivo/plivo-examples-php.git',
        'git@github.com:plivo/plivo-examples-node.git',
] 
GIT_DEFAULT_BRANCH="master"
GIT_FAISS_VECTOR_DATABASE="data/github_com.faiss"
GIT_SYSTEM_TEMPLATE='''Language {code_name}.
- Format the response with markdown.
- Write an application in {code_name} using the Plivo SDK with the requirements provided in the user question.
- The answer should always produce code that solves the problem.
- If there is no code in the question, generate the code in the answer.
- Analyze the following pieces of codes to answer the coding question.
- Include the sources in the answer in the format: "SOURCES: source1 source2".
- Include the programming language in the answer in the format: "LANGUAGE: language".
- If you don't know the answer, just say that "I don't know", don't try to make up an answer.
----------------
{summaries}
'''
GIT_OPENAI_MODEL="gpt-3.5-turbo"
GIT_OPENAI_TEMPERATURE=0.0
GIT_OPENAI_MAX_TOKENS=2000




SITEMAP_URL="https://plivo.com/sitemap.xml"
SITEMAP_FAISS_VECTOR_DATABASE="data/plivo_com.faiss"
CHAT_SYSTEM_TEMPLATE="""Use the following pieces of context to answer the users question.
Take note of the sources and include them in the answer in the format: "SOURCES: source1 source2", use "SOURCES" in capital letters regardless of the number of sources.
If you don't know the answer, just say that "I don't know", don't try to make up an answer.
----------------
{summaries}"""
CHAT_OPENAI_MODEL="gpt-3.5-turbo"
CHAT_OPENAI_TEMPERATURE=0.0
CHAT_OPENAI_MAX_TOKENS=1000

