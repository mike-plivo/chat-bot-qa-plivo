import sys
import pickle
import traceback
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit import prompt
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.callbacks import get_openai_callback

import settings


class CodeBot(object):
    available_languages = {"python": "Python",
                           "java": "Java",
                           "node": "Node.js",
                           "csharp": "CSharp",
                           "php": "PHP",
                           "ruby": "Ruby",
                           'go': 'Go',
                           'c': 'C',
                           'cpp': 'C++',
                           }
    def __init__(self, code="python"):
        self._db = None
        self._debug = False
        self.set_language(code)
        self.get_db()

    def set_debug(self, flag):
        if flag is True or flag in ['1', 'true', 'True', 'TRUE']:
            self._debug = True
            return True
        elif flag is False or flag in ['0', 'false', 'False', 'FALSE']:
            self._debug = False
            return False
        return None

    def is_debug_enabled(self):
        return self._debug

    def get_cost(self):
        return self._set_cost

    def set_language(self, code):
        if not self.is_language_supported(code):
            raise Exception("Language {} is not supported".format(code))
        self._code = code.lower()
        self._code_name = self.get_language_name(self._code)
        self._chain = None
        return True

    def get_db(self):
        if self._db is None:
            with open(settings.GIT_FAISS_VECTOR_DATABASE, "rb") as f:
                self._db = pickle.load(f)
        return self._db

    def get_available_languages(self):
        return self.available_languages.keys()

    def is_language_supported(self, code):
        return code.lower() in self.get_available_languages()

    def is_active_language(self, code):
        return self._code == code.lower()

    def get_language_name(self, code):
        try:
            return self.available_languages[code.lower()]
        except Exception:
            return code

    def _get_llm_chain(self):
        if self._chain is None:
            git_system_template = settings.GIT_SYSTEM_TEMPLATE.replace('{code_name}', self._code_name)
            messages = [
                SystemMessagePromptTemplate.from_template(git_system_template),
                HumanMessagePromptTemplate.from_template("{question}")
            ]
            chat_prompt = ChatPromptTemplate.from_messages(messages)
            chain_type_kwargs = {"prompt": chat_prompt}
            llm = ChatOpenAI(model_name=settings.GIT_OPENAI_MODEL, 
                             temperature=settings.GIT_OPENAI_TEMPERATURE, 
                             max_tokens=settings.GIT_OPENAI_MAX_TOKENS)
            self._chain = RetrievalQAWithSourcesChain.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.get_db().as_retriever(),
                return_source_documents=True,
                chain_type_kwargs=chain_type_kwargs
            )
        return self._chain

    def parse_question(self, question):
        q = []
        for line in question.splitlines():
            for l in line.split('. '):
                q.append(l.strip()+'.\n')
        return '- '.join(q)

    def query(self, question):
        question = self.parse_question(question)
        result = {}
        if self.is_debug_enabled():
            with get_openai_callback() as cb:
                result = self._get_llm_chain()(question)
                result["stats"] = {'total_tokens': cb.total_tokens,
                            'prompt_tokens': cb.prompt_tokens,
                            'completion_tokens': cb.completion_tokens,
                            'successful_requests': cb.successful_requests,
                            'total_cost': cb.total_cost}
        else:
            result = self._get_llm_chain()(question)
        return result

    def query_and_print_result(self, question):
        result = self.query(question)
        cr = "\n"
        output_text = f"""
## Question
{question}

## Answer
{result['answer']}

## References
{cr.join(list(set([doc.metadata['source'] for doc in result['source_documents']])))}
"""
        if self.is_debug_enabled():
            msg = f'\n\n## Cost\n{result["stats"]}\n'
            msg += f'\n\n## Debug\n{result}\n'
            output_text += msg

        print(output_text)



class PlivoCodeBot(CodeBot):
    def __init__(self, code="python"):
        self._banner = '<p fg="ansiwhite">Plivo Code Bot</p><p fg="ansired"> ("/help" for help)</p>'
        super().__init__(code)
        self._set_cost = True

    def perror(self, error):
        print_formatted_text(HTML('<p fg="ansired">{}</p>'.format(error)))
        print('\n')

    def run(self):
        print_formatted_text(HTML(self._banner))
        while True:
            try:
                self._wait_for_input()
            except (KeyboardInterrupt, EOFError):
                print("Bye!")
                sys.exit(0)
            except Exception as e:
                self.perror(f"Oops: {e}")
                traceback.print_exc()
                continue

    def _cmd_exit(self, msg):
        print(msg)
        sys.exit(0)

    def _cmd_clear(self):
        print("\033c")

    def _cmd_code(self):
        print("Supported languages:")
        for _code in self.get_available_languages():
            if _code == self._code:
                print("\t{} (current)".format(_code))
            else:
                print("\t{}".format(_code))
        print('\n')

    def _cmd_code_change(self, code):
        if not code:
            self.perror("Please specify a language")
            return
        code = code.strip()
        if not self.is_language_supported(code):
            self.perror("Language {} is not supported".format(code))
            return
        if self.is_active_language(code):
            self.perror("Language {} is already set".format(code))
            return
        self.set_language(code)
        print("Language changed to {}".format(self._code_name))
        print('\n')

    def _cmd_ask(self, query):
        query = query.replace("/ask ", "")
        if not query:
            self.perror("You must enter a question to ask")
            return
        self.query_and_print_result(query)
        print('\n')

    def _cmd_help(self):
        print("\tType '/quit' to exit")
        print("\tType '/clear' to clear the screen")
        print("\tType '/code [LANGUAGE]' to change the language")
        print("\tType '/code' to see the supported languages and the current active laguage")
        print("\tType '/ask [QUESTION]' to ask a question")
        print("\tType '/debug' show if debug mode is enabled or disabled")
        print("\tType '/debug [true|false]' debug info including cost")
        print('\n')

    def _cmd_debug(self):
        if self.is_debug_enabled():
            print("Debug enabled")
        else:
            print("Debug disabled")
        print('\n')

    def _cmd_debug_change(self, debug):
        debug = debug.strip()
        res = self.set_debug(debug)
        if res is True:
            print(f"Debug enabled")
        elif res is False:
            print(f"Debug disabled")
        else:
            self.perror("Please specify true or false")
        print('\n')

    def _wait_for_input(self):
        query = prompt(">>> ")
        if query == "/quit":
            self._cmd_exit('Bye!')
        elif query == "/clear":
            self._cmd_clear()
        elif query == "/code":
            self._cmd_code()
        elif query.startswith("/code "):
            try:
                _cmd, _code = query.split(" ", 1)
            except ValueError:
                self.perror("Please specify a language")
                return
            self._cmd_code_change(_code)
        elif query.startswith("/ask"):
            self._cmd_ask(query)
        elif query == "/help":
            self._cmd_help()
        elif query == "/debug":
            self._cmd_debug()
        elif query.startswith("/debug"):
            try:
                _cmd, _debug = query.split(" ", 1)
            except ValueError:
                self.perror("Please specify true or false")
                return
            self._cmd_debug_change(_debug)
        else:
            self.perror("Unknown command, type '/help' for help")


if __name__ == "__main__":
    bot = PlivoCodeBot()
    bot.run()

