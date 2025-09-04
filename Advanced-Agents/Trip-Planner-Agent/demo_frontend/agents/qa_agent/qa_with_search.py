import os
from openai import OpenAI
from tavily import TavilyClient

os.environ["TAVILY_API_KEY"] = "dummy key"
os.environ["OPENAI_API_KEY"] = "dummy key"


# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def determine_if_search_needed(question):
    """Determine if the question requires an internet search."""
    messages = [
        {"role": "system", "content": "You determine if a question needs real-time information from the internet. Respond with 'yes' or 'no' only."},
        {"role": "user", "content": f"Does this question require searching the internet for up-to-date information? Question: {question}"}
    ]

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=10
    )

    answer = response.choices[0].message.content.strip().lower().rstrip(".")  # remove fullstop at the end.
    return answer == "yes"

def refine_search_term(question):
    """Refine the question into a better search term."""
    messages = [
        {"role": "system", "content": "Given a question, generate an effective search query (1-5 words if possible) that will help find the most relevant information."},
        {"role": "user", "content": f"Create a search query for: {question}"}
    ]

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=50
    )

    search_term = response.choices[0].message.content.strip()
    return search_term

def search_internet(query):
    """Search the internet using Tavily API."""
    search_results = tavily_client.search(query=query, search_depth="advanced", include_images=False)
    return search_results

def generate_response(question, search_results=None):
    """Generate a response using OpenAI's API."""
    if search_results:
        # Format search results as context
        context = ""
        for result in search_results.get('results', [])[:3]:
            title = result.get('title', 'No title')
            content = result.get('content', 'No content')
            url = result.get('url', 'No URL')
            context += f"Title: {title}\nContent: {content}\nURL: {url}\n\n"

        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the provided search results to answer the user's question accurately. Cite your sources."},
            {"role": "user", "content": f"Question: {question}\n\nSearch results:\n{context}"}
        ]
    else:
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer the user's question to the best of your knowledge."},
            {"role": "user", "content": f"Question: {question}"}
        ]

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return response.choices[0].message.content

def chat_with_search(question):
    """Main function to handle the chat with search capability."""
    print(f"User: {question}")

    # Determine if search is needed
    search_needed = determine_if_search_needed(question)

    if search_needed:
        # Refine search term
        search_term = refine_search_term(question)
        print(f"Searching for: {search_term}")

        # Search the internet
        search_results = search_internet(search_term)

        # Generate response with search results
        response = generate_response(question, search_results)
    else:
        # Generate response without search
        response = generate_response(question)

    print(f"Assistant: {response}")
    return response

def main():
    chat_with_search("What is the current status of the stock market?")

if __name__ == "__main__":
    main()
