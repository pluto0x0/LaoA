import gradio as gr
from rag_pipeline import setup_rag_pipeline, ask_question

# Set up the RAG pipeline
qa_chain = setup_rag_pipeline()

def get_answer(question):
    response = ask_question(qa_chain, question)
    answer = response['result']
    source_documents = ""
    for doc in response['source_documents']:
        source_documents += doc.page_content + "\n" + "-"*20 + "\n"
    return answer, source_documents

iface = gr.Interface(
    fn=get_answer,
    inputs=gr.Textbox(lines=2, placeholder="Enter your question here..."),
    outputs=[
        gr.Textbox(label="Answer"),
        gr.Textbox(label="Source Documents")
    ],
    title="SquishyKing Live Stream Q&A",
    description="Ask questions about the live stream content. The system will retrieve relevant information from the subtitles.",
)

if __name__ == "__main__":
    iface.launch(share=True)

