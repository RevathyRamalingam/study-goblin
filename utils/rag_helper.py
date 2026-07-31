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
        vector_index,
        embedder,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        course='llm-zoomcamp',
        model='llama-3.3-70b-versatile'
    ):
        self.index = index
        self.vector_index = vector_index
        self.embedder = embedder
        self.llm_client = client
        self.instructions = instructions
        self.course = course
        self.prompt_template = prompt_template
        self.model = model

    def rrf(result_lists, k=60, num_results=2):
        scores = {}
        docs = {}
    
        for results in result_lists:
            for rank, doc in enumerate(results):
                key = (doc["chunk_id"], doc["start"])
                scores[key] = scores.get(key, 0) + 1 / (k + rank)
                docs[key] = doc
    
        ranked = sorted(scores, key=scores.get, reverse=True)
        return [docs[key] for key in ranked[:num_results]]

    def search(self, query, num_results=10):
        boost_dict = {'content': 3.0, 'metadata': 0.5}

        text_search_result =self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict
        )
        vector_search_result = self.vector_index.search(
            self.embedder.encode(query),
            num_results=num_results
        )
       
        rrf = RAGBase.rrf([vector_search_result,text_search_result])
        return rrf

    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append('Content: ' + doc['content'])

        return '\n'.join(lines).strip()

    def build_prompt(self, query, search_results):
        print("prompt_template type:", type(self.prompt_template))
        print("embedder type:", type(self.embedder))
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
