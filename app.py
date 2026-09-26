import streamlit as st
from databricks import sql
import os

st.set_page_config(
page_title="Microcontroller RAG Assistant",
page_icon="🔧",
layout="centered"
)

st.title("🔧 Microcontroller RAG Assistant")
st.caption(
"Ask questions about RP2040, RP2350 and related Raspberry Pi documentation."
)

def get_connection():
  return sql.connect(
  server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
  http_path=os.environ["DATABRICKS_HTTP_PATH"],
  access_token=os.environ["DATABRICKS_TOKEN"]
)

def ask_rag(question):
  query = """
  WITH params AS (
  SELECT :question AS question
  ),

  retrieved_chunks AS (
    SELECT
      file_name,
      page_number,
      product,
      document_type,
      chunk_id,
      text,
      search_score
    FROM VECTOR_SEARCH(
      index => 'microcontrollers.rag_project.document_search',
      query_text => (SELECT question FROM params),
      num_results => 5
    )
  ),

  context AS (
    SELECT
      CONCAT_WS(
        '\\n\\n--- SOURCE ---\\n',
        COLLECT_LIST(
          CONCAT(
            'Document: ', file_name,
            '\\nPage: ', CAST(page_number AS STRING),
            '\\nProduct: ', product,
            '\\nDocument type: ', document_type,
            '\\nContent:\\n', text
          )
        )
      ) AS retrieved_context
    FROM retrieved_chunks
  )

  SELECT
    ai_query(
      'databricks-gpt-oss-20b',
      CONCAT(
        'You are a technical documentation question-answering assistant.\\n\\n',
        'Answer the user question using ONLY the retrieved documentation.\\n\\n',
        'STRICT GROUNDING RULES:\\n',
        '1. A retrieved chunk is not automatically evidence for the answer.\\n',
        '2. Only use information that directly answers the user question.\\n',
        '3. Do not use outside knowledge.\\n',
        '4. Do not infer or invent technical details.\\n',
        '5. Do not interpret unexplained numbers or identifiers.\\n',
        '6. Every factual claim must be supported by the retrieved documentation.\\n',
        '7. Use the minimum number of source citations necessary to support the answer.\\n',
        '8. Prefer the most directly relevant page or pages over redundant citations.\\n',
        '9. Cite the document filename and page number for factual claims.\\n',
        '10. If the retrieved documentation does not contain enough information, ',
        'respond exactly: The retrieved documentation does not contain enough ',
        'information to answer this question.\\n',
        '11. Keep the answer concise and technically accurate.\\n\\n',
        'USER QUESTION:\\n',
        (SELECT question FROM params),
        '\\n\\n',
        'RETRIEVED DOCUMENTATION:\\n',
        retrieved_context
      )
    ) AS response
  FROM context
  """

connection = get_connection()

try:
    with connection.cursor() as cursor:
        cursor.execute(
            query,
            parameters={
                "question": question
            }
        )

        result = cursor.fetchone()

        if result:
            return result[0]

        return "The retrieved documentation does not contain enough information to answer this question."

finally:
    connection.close()


if "messages" not in st.session_state:
  st.session_state.messages = []

for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

question = st.chat_input(
"Ask a question about the documentation..."
)

if question:
  st.session_state.messages.append(
  {
  "role": "user",
  "content": question
  }
  )

with st.chat_message("user"):
    st.markdown(question)

with st.chat_message("assistant"):
    with st.spinner("Searching the documentation..."):
        try:
            answer = ask_rag(question)

            st.markdown(answer)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

        except Exception as e:
            error_message = (
                "Sorry, I couldn't process the question. "
                "Please check the application configuration."
            )

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message
                }
            )