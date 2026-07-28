INSTRUCTIONS = """
You are Study Goblin, a friendly AI teaching assistant.

Answer questions only using the provided context.

If the answer is not available in the context, respond politely like this:

"I'm sorry, I couldn't find information about that in my current study materials. I can help answer questions related to the uploaded textbook or course content. Feel free to ask another question!"

Never invent information that isn't supported by the context.
"""

PROMPT_TEMPLATE = '''
QUESTION: {question}

CONTEXT:
{context}
'''.strip()


class RAGBase:

    def __init__(
        self,
        index,
        llm_client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        course='llm-zoomcamp',
        model='gpt-5.4-mini'
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.course = course
        self.prompt_template = prompt_template
        self.model = model

    def search(self, query, num_results=5):
        print("searchfunction called")
        boost_dict = {'content': 3.0, 'filename': 0.5}

        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict
        )

    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append('Content: ' + doc['content'])
            lines.append('metadata: ' + doc['metadata'])
            lines.append('')

        return '\n'.join(lines).strip()

    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )

    def llm(self, prompt):
        input_messages = [
            {'role': 'developer', 'content': self.instructions},
            {'role': 'user', 'content': prompt}
        ]

        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )
        print("tokens used: ",response.usage.input_tokens)
        return response.output_text

    def rag(self, query):
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        answer = self.llm(prompt)
        return answer
