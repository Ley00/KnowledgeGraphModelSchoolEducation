
import pandas as pd

from llama_index.core import SimpleDirectoryReader
from llama_index.core import KnowledgeGraphIndex
from llama_index.core import Settings
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core import StorageContext
from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

from llama_index.embeddings.langchain import LangchainEmbedding
from pyvis.network import Network

import os
import logging
import sys

from pyvis.network import Network
from IPython.display import display

#
import IPython


def rag(foldercsv, namecsv):
    """
    Loads data, creates RAG, and trains a model on the RAG.

    Args:
        foldercsv (str): Path to the folder containing the CSV file.
        namecsv (str): Name of the CSV file containing student grades data.
    """

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    HF_TOKEN = "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"
    llm = HuggingFaceInferenceAPI(
        model_name="HuggingFaceH4/zephyr-7b-beta", 
        token=HF_TOKEN
    )
    # embed_model = LangchainEmbedding(llm)
    embed_model = LangchainEmbedding(
        HuggingFaceInferenceAPIEmbeddings(
            api_key=HF_TOKEN,
            model_name="thenlper/gte-large"
    ))


    # documents = SimpleDirectoryReader("../{foldercsv}/{namecsv}").load_data()
    documents = SimpleDirectoryReader(
        input_files=["Result/media_nota_aluno.csv", "Result/pagamento_aluno.csv"]
    ).load_data()
    print(documents)


    #setup the service context (global setting of LLM)
    Settings.llm = llm
    Settings.chunk_size = 512

    #setup the storage context
    graph_store = SimpleGraphStore()
    storage_context = StorageContext.from_defaults(graph_store=graph_store)

    #Construct the Knowlege Graph Undex
    index = KnowledgeGraphIndex.from_documents(documents=documents,
                                            max_triplets_per_chunk=3,
                                            storage_context=storage_context,
                                            embed_model=embed_model,
                                            include_embeddings=True)


    g = index.get_networkx_graph()
    net = Network(notebook=True,cdn_resources="in_line",directed=True)
    net.from_nx(g)
    net.show("graph.html")
    net.save_graph("Result/Knowledge_graph.html")
    IPython.display.HTML(filename="Result/Knowledge_graph.html")


    query = "Did Ana Cecilia pay her August monthly fee?"
    query_engine = index.as_query_engine(include_text=True,
                                        response_mode ="tree_summarize",
                                        embedding_mode="hybrid",
                                        similarity_top_k=5,)
    #
    message_template =f"""<|system|>Please check if the following pieces of context has any mention of the  keywords provided in the Question.If not then don't know the answer, just say that you don't know.Stop there.Please donot try to make up an answer.</s>
    <|user|>
    Question: {query}
    Helpful Answer:
    </s>"""
    #
    response = query_engine.query(message_template)
    #
    print(response.response.split("<|assistant|>")[-1].strip())
