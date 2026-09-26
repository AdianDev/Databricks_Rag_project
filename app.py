import os

import streamlit as st
from databricks import sql
from databricks.sdk.core import Config


# -----------------------------------------------------------------------------
# Streamlit configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Microcontroller RAG Assistant",
    page_icon="🔧",
    layout="centered",
)

st.title("🔧 Microcontroller RAG Assistant")
st.caption(
    "Ask questions about RP2040, RP2350 and related Raspberry Pi documentation."
)


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

FALLBACK_RESPONSE = (
    "The retrieved documentation does not contain enough information "
    "to answer this question."
)


# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------

with st.sidebar:
    st.header("About")

    st.write(
        "Microcontroller RAG Assistant uses Databricks Vector Search and "
        "Databricks AI Model Serving to answer questions from retrieved "
        "Raspberry Pi microcontroller documentation."
    )

    st.divider()

    if st.button(
        "Clear conversation",
        use_container_width=True,
        type="secondary",
    ):
        st.session_state.messages = []
        st.rerun()


# -----------------------------------------------------------------------------
# Databricks SQL connection
# -----------------------------------------------------------------------------

def get_databricks_connection():
    """
    Create a Databricks SQL connection using the Databricks App
    service principal and the SQL Warehouse resource.
    """

    cfg = Config()

    if not cfg.host:
        raise RuntimeError(
            "The Databricks workspace host could not be determined "
            "from the Databricks App environment."
        )

    # The SQL Warehouse resource in app.yaml provides this value.
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

    if not warehouse_id:
        raise RuntimeError(
            "DATABRICKS_WAREHOUSE_ID is not available. "
            "Make sure the SQL Warehouse resource is configured in "
            "the Databricks App and referenced correctly in app.yaml."
        )

    # Remove protocol from workspace host if present.
    server_hostname = cfg.host

    if server_hostname.startswith("https://"):
        server_hostname = server_hostname[len("https://"):]

    elif server_hostname.startswith("http://"):
        server_hostname = server_hostname[len("http://"):]

    server_hostname = server_hostname.rstrip("/")

    # Databricks SQL Warehouse HTTP path.
    http_path = f"/sql/1.0/warehouses/{warehouse_id}"

    return sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )


# -----------------------------------------------------------------------------
# RAG SQL
# -----------------------------------------------------------------------------

RAG_SQL = """
WITH retrieved_chunks AS (
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
    query_text => :question,
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

      'SOURCE CITATION FORMAT:\\n',

      'For one source, use exactly this style when appropriate:\\n',
      'Source: filename.pdf, page 9\\n\\n',

      'For multiple necessary sources, use exactly this style:\\n',
      'Sources:\\n',
      '- filename1.pdf, page 4\\n',
      '- filename2.pdf, page 9\\n\\n',

      'Only cite sources that directly support the factual claim.\\n',
      'Do not cite every retrieved chunk.\\n\\n',

      'USER QUESTION:\\n',
      :question,
      '\\n\\n',

      'RETRIEVED DOCUMENTATION:\\n',
      retrieved_context
    )
  ) AS response
FROM context
"""


# -----------------------------------------------------------------------------
# Execute RAG
# -----------------------------------------------------------------------------

def ask_rag_assistant(question: str) -> str:
    """
    Execute the RAG pipeline:

        User question
              ↓
        Vector Search
              ↓
        Top 5 chunks
              ↓
        Retrieved context
              ↓
        databricks-gpt-oss-20b
              ↓
        Grounded answer
    """

    connection = None
    cursor = None

    try:
        connection = get_databricks_connection()
        cursor = connection.cursor()

        cursor.execute(
            RAG_SQL,
            parameters={
                "question": question
            },
        )

        row = cursor.fetchone()

        if not row:
            return FALLBACK_RESPONSE

        response = row[0]

        if response is None:
            return FALLBACK_RESPONSE

        response = str(response).strip()

        if not response:
            return FALLBACK_RESPONSE

        return response

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass

        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass


# -----------------------------------------------------------------------------
# Display previous messages
# -----------------------------------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------------------------------------------------------
# Chat input
# -----------------------------------------------------------------------------

question = st.chat_input(
    "Ask a question about RP2040, RP2350, or the documentation..."
)


# -----------------------------------------------------------------------------
# Process question
# -----------------------------------------------------------------------------

if question:

    question = question.strip()

    if question:

        # Display user question
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        # Generate answer
        with st.chat_message("assistant"):

            with st.spinner(
                "Searching the documentation and generating an answer..."
            ):

                try:
                    answer = ask_rag_assistant(question)

                    st.markdown(answer)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                except Exception as exc:

                    user_message = (
                        "An error occurred while processing your question."
                    )

                    st.error(user_message)

                    with st.expander("Show technical details"):
                        st.exception(exc)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": user_message,
                        }
                    )
