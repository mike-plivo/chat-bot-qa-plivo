import sys
import pickle
import traceback
import argparse
import json
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


class BaseCodeBot(object):
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

    @classmethod
    def get_available_languages(cls):
        return cls.available_languages.keys()

    @classmethod
    def is_language_supported(cls, code):
        return code.lower() in cls.get_available_languages()

    @classmethod
    def get_language_name(cls, code):
        try:
            return cls.available_languages[code.lower()]
        except Exception:
            return code

    def is_active_language(self, code):
        return self._code == code.lower()

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
        q.append('Use the programming language {}.\n'.format(self._code_name))
        return '- '.join(q)

    @classmethod
    def perror(cls, error):
        print_formatted_text(HTML('<p fg="ansired">ERROR: {}</p>'.format(error)))
        print('\n')

    def ask(self, code, question):
        if not self.is_language_supported(code):
            return json.dumps({"status": "error",
                               "error": "Language {} is not supported".format(code)})
        if not question:
            return json.dumps({"status": "error",
                               "error": "Question is required"})
        if not self.is_active_language(code):
            del self._chain
            self._chain = None
            self.set_language(code)
        data = self.query_as_dict(question)
        return json.dumps({"status": "success",
                           'response': data})

    def _query(self, question):
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

    def query_as_dict(self, question):
        result = self._query(question)
        data_sources = list(set([doc.metadata['source'] for doc in result['source_documents']]))
        response = {'question': question,
                    'answer': result['answer'], 
                    'language': self._code, 
                    'language_name': self._code_name,
                    'sources': data_sources,
                    }
        if self.is_debug_enabled():
            response['stats'] = result['stats']
            response['raw_response'] = str(result)
        return response

    def query_as_text(self, question):
        result = self._query(question)
        data_sources = set(['- '+doc.metadata['source'] for doc in result['source_documents']])
        data_sources = '\n'.join(tuple(data_sources))
        output_text = f"""
# Question
{question}

# Answer
{result['answer']}

# Sources 
{data_sources}

"""
        if self.is_debug_enabled():
            msg = f'\n\n# Cost\n{result["stats"]}\n'
            msg += f'\n\n# Raw response\n{result}\n'
            output_text += msg

        return output_text

    def query_and_print_result(self, question):
        print(self.query_as_text(question))




class CodeBot(BaseCodeBot):
    def __init__(self, code="python", banner='CodeBot'):
        self._banner = f'<p fg="ansiwhite">{banner}</p><p fg="ansired"> ("/help" for help)</p>'
        super().__init__(code)
        self._set_cost = True

    @classmethod
    def cli(cls, code="python", banner='CodeBot'):
        parser = argparse.ArgumentParser(description="CodeBot")
        parser.add_argument("-a", "--ask", type=str, default="", help="Question to ask (required in CLI mode)")
        parser.add_argument("-c", "--code", type=str, choices=cls.get_available_languages(), default=code, help=f"Programming language to use - default: {code}")
        parser.add_argument("-m", "--mode", type=str, choices=['prompt', 'cli'], default="prompt", help="CLI mode or Prompt mode - default: prompt")
        parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode (show OpenAI API cost and response)")
        parser.add_argument("-b", "--banner", type=str, default="CodeBot", help=f"Banner text (only used in prompt mode) - default {banner}")
        args = parser.parse_args()
        _code = args.code.lower()
        debug = args.debug
        banner = args.banner
        mode = args.mode
        ask = args.ask
        if ask and mode == 'prompt':
            cls.perror("-a/--ask cannot be use in Prompt mode")
            parser.print_help()
            sys.exit(1)
        if mode == 'cli' and not ask:
            cls.perror("-a/--ask is required in CLI mode")
            parser.print_help()
            sys.exit(1)
        bot = cls(code=_code, banner=banner)
        debug is True and bot.set_debug(True)
        if mode == 'prompt':
            bot.run()
            return
        elif mode == 'cli':
            bot.cli_run(ask)
            return

        parser.print_help()
        sys.exit(1)

    def cli_run(self, question):
        self.query_and_print_result(question)
        sys.exit(0)

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

    def _cmd_exit(self, msg='Bye!'):
        print(msg)
        sys.exit(0)

    def _cmd_clear(self):
        print("\033c")

    def _cmd_banner(self):
        print_formatted_text(HTML(self._banner))
        print('\n')

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
        print("\tType '/ask [QUESTION]' to ask a question")
        print("\tType '/banner' show banner")
        print("\tType '/clear' to clear the screen")
        print("\tType '/code [LANGUAGE]' to change the language")
        print("\tType '/code' to see the supported languages and the current active laguage")
        print("\tType '/debug' show if debug mode is enabled or disabled")
        print("\tType '/debug [true|false]' debug info including cost")
        print("\tType '/quit' to exit")
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
        elif query == "/banner":
            self._cmd_banner()
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
            if query.strip() == "":
                return
            self.perror("Unknown command, type '/help' for help")


if __name__ == "__main__":
    # API style
    #bot = CodeBot(code=settings.GIT_BOT_DEFAULT_LANGUAGE, banner=settings.GIT_BOT_BANNER)
    #bot.set_debug(True)
    # result = bot.ask(code="ruby", question="send an SMS")

    # CLI style
    CodeBot.cli(code=settings.GIT_BOT_DEFAULT_LANGUAGE, banner=settings.GIT_BOT_BANNER)

    # Prompt style
    #bot = CodeBot(code=settings.GIT_BOT_DEFAULT_LANGUAGE, banner=settings.GIT_BOT_BANNER)
    #bot.run()

