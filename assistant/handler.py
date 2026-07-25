import json

from assistant.context_builder import build_context
from assistant.flashcard_builder import build_flashcard_prompt
from assistant.insight_builder import build_insight_prompt
from assistant.llm import generate_response
from assistant.prompt_builder import build_qa_prompt
from assistant.quiz_builder import build_quiz_prompt
from assistant.summary_builder import build_summary_prompt

from shared.embedding_generator import generate_embedding
from shared.vector_store import query_embeddings


SUPPORTED_TASKS = {
    "qa",
    "summary",
    "quiz",
    "flashcards",
    "insights",
}


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))

        task = body.get("task", "").strip().lower()
        document_id = body.get("document_id", "").strip()

        if task not in SUPPORTED_TASKS:
            return create_response(
                400,
                {
                    "error": (
                        "Invalid task. Supported tasks are: "
                        "qa, summary, quiz, flashcards, insights."
                    )
                },
            )

        if not document_id:
            return create_response(
                400,
                {"error": "document_id is required."},
            )

        search_query = get_search_query(task, body)

        query_embedding = generate_embedding(search_query)

        matches = query_embeddings(
            query_embedding=query_embedding,
            document_id=document_id,
            top_k=int(body.get("top_k", 8)),
        )

        if not matches:
            return create_response(
                404,
                {"error": "No content was found for this document."},
            )

        context_text = build_context(matches)
        prompt = build_prompt(task, context_text, body)
        result = generate_response(prompt)

        citations = sorted(list(set(
            match.get("metadata", {}).get("page_number") 
            for match in matches 
            if match.get("metadata", {}).get("page_number") is not None
        )))

        response_data = {
            "task": task,
            "document_id": document_id,
            "result": parse_json_result(task, result),
            "citations": citations,
        }

        return create_response(200, response_data)

    except json.JSONDecodeError:
        return create_response(
            400,
            {"error": "Request body must contain valid JSON."},
        )

    except Exception as error:
        print(f"Assistant error: {error}")

        return create_response(
            500,
            {
                "error": "Assistant request failed.",
                "details": str(error),
            },
        )


def get_search_query(task: str, body: dict) -> str:
    if task == "qa":
        question = body.get("question", "").strip()

        if not question:
            raise ValueError(
                "question is required when task is 'qa'."
            )

        return question

    search_queries = {
        "summary": (
            "main purpose methodology contributions findings conclusion"
        ),
        "quiz": (
            "important concepts methods findings definitions contributions"
        ),
        "flashcards": (
            "important concepts definitions methods findings"
        ),
        "insights": (
            "key findings contributions implications methodology"
        ),
    }

    return search_queries[task]


def build_prompt(
    task: str,
    context_text: str,
    body: dict,
) -> str:
    if task == "qa":
        return build_qa_prompt(
            context=context_text,
            question=body["question"],
        )

    if task == "summary":
        return build_summary_prompt(context_text)

    if task == "quiz":
        return build_quiz_prompt(
            context=context_text,
            number_of_questions=int(
                body.get("number_of_questions", 5)
            ),
        )

    if task == "flashcards":
        return build_flashcard_prompt(
            context=context_text,
            number_of_flashcards=int(
                body.get("number_of_flashcards", 5)
            ),
        )

    return build_insight_prompt(
        context=context_text,
        number_of_insights=int(
            body.get("number_of_insights", 5)
        ),
    )


def parse_json_result(task: str, result: str):
    if task in {"quiz", "flashcards", "insights"}:
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "raw_response": result,
                "warning": "Gemini did not return valid JSON.",
            }

    return result


def create_response(
    status_code: int,
    body: dict,
) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }