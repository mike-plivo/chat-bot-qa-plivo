CODEBOT_GIT_REPOS_DIR="data/git_repos"
CODEBOT_GIT_REPO_URLS = [
        # format is (repo_url, branch)
        ('git@github.com:plivo/plivo-python.git', 'master'),
        ('git@github.com:plivo/plivo-java.git', 'master'),
        ('git@github.com:plivo/plivo-ruby.git', 'master'),
        ('git@github.com:plivo/plivo-dotnet.git', 'master'),
        ('git@github.com:plivo/plivo-php.git', 'master'),
        ('git@github.com:plivo/plivo-node.git', 'master'),
        ('git@github.com:plivo/plivo-examples-python.git', 'master'),
        ('git@github.com:plivo/plivo-examples-java.git', 'master'),
        ('git@github.com:plivo/plivo-examples-ruby.git', 'master'),
        ('git@github.com:plivo/plivo-examples-dotnet.git', 'master'),
        ('git@github.com:plivo/plivo-examples-php.git', 'master'),
        ('git@github.com:plivo/plivo-examples-node.git', 'master'),
] 
CODEBOT_FAISS_VECTOR_DATABASE="data/github_com.faiss"
CODEBOT_SYSTEM_TEMPLATE='''
- Write an application with the programming language {code_name} using the Plivo SDK with the requirements provided in the user question.
- The answer should always produce code that solves the problem.
- If there is no code in the question, generate the code in the answer.
- Format the answer with markdown.
- Always include the full code implementation in the answer.
- If you don't know the answer, just say that "I don't know", don't try to make up an answer.
- Analyze the following pieces of codes to answer the coding question.
----------------
{summaries}
'''
CODEBOT_OPENAI_MODEL="gpt-3.5-turbo"
CODEBOT_OPENAI_TEMPERATURE=0.0
CODEBOT_OPENAI_MAX_TOKENS=2000

