INSTRUCTIONS = """
You are Study Goblin, a friendly AI teaching assistant.

Answer questions only using the provided context.

If the answer is not found in the provided context:
- Respond only with the polite fallback message.
- Do not make guesses.
- Do not use outside knowledge.
- Do not add explanations beyond the fallback response.

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
        client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        course='llm-zoomcamp',
        model='allam-2-7b'
    ):
        self.index = index
        self.llm_client = client
        self.instructions = instructions
        self.course = course
        self.prompt_template = prompt_template
        self.model = model

    def search(self, query, num_results=2):
        boost_dict = {'content': 3.0, 'metadata': 0.5}

        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict
        )

    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append('Content: ' + doc['content'])

        return '\n'.join(lines).strip()

    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )

    def llm(self, prompt):
        print("self.model =", self.model)
        print("client type =", type(self.llm_client))
        response = self.llm_client.chat.completions.create(
            model=self.model,
             messages=[
                {
                    "role": "system",
                    "content": self.instructions
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )
        #print("tokens used: ",response.usage.input_tokens)
        return response.choices[0].message.content

    def rag(self, query):
        search_results = self.search(query)
        print("rag search result is ",search_results)
        prompt = self.build_prompt(query, search_results)
        print("prompt length is ",len(prompt))
        answer = self.llm(prompt)

        retrieved_chunk_ids = [
            doc["chunk_id"] for doc in search_results
        ]
        print("answer from llm is ",answer)
        return {
            "answer" :answer,
            "retrieved_chunk_ids": retrieved_chunk_ids
        }
