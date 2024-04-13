import os
import json
import logging
import requests
import http.client
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
YOUR_SITE_URL = "https://jaredkirby.me"
YOUR_APP_NAME = "LinkedIn_JPK"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_linkedin_user_details(linkedin_url):
    """
    Retrieve user details from a LinkedIn profile.

    Args:
        linkedin_url (str): The URL of the LinkedIn profile.

    Returns:
        dict: The user details retrieved from the API.
    """
    try:
        encoded_url = urllib.parse.quote(linkedin_url, safe="")
        conn = http.client.HTTPSConnection("fresh-linkedin-profile-data.p.rapidapi.com")
        headers = {
            "X-RapidAPI-Key": os.environ.get("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": "fresh-linkedin-profile-data.p.rapidapi.com",
        }
        conn.request(
            "GET",
            f"/get-linkedin-profile?linkedin_url={encoded_url}&include_skills=false",
            headers=headers,
        )
        res = conn.getresponse()
        if res.status == 200:
            data = res.read().decode("utf-8")
            return json.loads(data)
        else:
            logging.error(f"Failed to retrieve user details. Status code: {res.status}")
            return None
    except Exception as e:
        logging.error(f"An error occurred while retrieving user details: {str(e)}")
        return None


def get_linkedin_posts(linkedin_url, max_posts=10):
    """
    Retrieve posts from a LinkedIn profile.

    Args:
        linkedin_url (str): The URL of the LinkedIn profile.
        max_posts (int): The maximum number of posts to retrieve (default: 10).

    Returns:
        list: The list of posts retrieved from the API.
    """
    try:
        encoded_url = urllib.parse.quote(linkedin_url, safe="")
        conn = http.client.HTTPSConnection("fresh-linkedin-profile-data.p.rapidapi.com")
        headers = {
            "X-RapidAPI-Key": os.environ.get("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": "fresh-linkedin-profile-data.p.rapidapi.com",
        }
        conn.request(
            "GET",
            f"/get-profile-posts?linkedin_url={encoded_url}&type=posts&max={max_posts}",
            headers=headers,
        )
        res = conn.getresponse()
        if res.status == 200:
            data = res.read().decode("utf-8")
            posts_data = json.loads(data)
            return posts_data.get("data", [])
        else:
            logging.error(f"Failed to retrieve posts. Status code: {res.status}")
            return []
    except Exception as e:
        logging.error(f"An error occurred while retrieving posts: {str(e)}")
        return []


def generate_text(prompt):
    """
    Generate text using the OpenRouter AI API.

    Args:
        prompt (str): The prompt for generating the text.

    Returns:
        dict: The generated text response from the API.
    """
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Referer": YOUR_SITE_URL,
            "X-Title": YOUR_APP_NAME,
            "Content-Type": "application/json",
        }
        data = {
            "model": "cohere/command-r-plus",
            "max_tokens": 4000,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data
        )
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(
                f"Failed to generate text. Status code: {response.status_code}"
            )
            return None
    except Exception as e:
        logging.error(f"An error occurred while generating text: {str(e)}")
        return None


def validate_linkedin_url(linkedin_url):
    """
    Validate the format of a LinkedIn profile URL.

    Args:
        linkedin_url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    # Add your validation logic here
    # Example: Check if the URL starts with "https://www.linkedin.com/in/"
    return linkedin_url.startswith("https://www.linkedin.com/in/")


def main():
    linkedin_url = input("Please enter the LinkedIn profile URL: ")
    if not validate_linkedin_url(linkedin_url):
        logging.error("Invalid LinkedIn profile URL.")
        return

    user_details = get_linkedin_user_details(linkedin_url)
    if user_details is None:
        logging.error("Failed to retrieve user details.")
        return

    posts = get_linkedin_posts(linkedin_url)
    if posts is None:
        logging.error("Failed to retrieve posts.")
        return

    # Display the user details
    print("\nUser Details Extracted:")
    print(
        f"- Name: {user_details.get('first_name', 'No first name available')} {user_details.get('last_name', 'No last name available')}"
    )
    print(f"- Summary: {user_details.get('about', 'No summary available')}")
    print(
        f"- Current Role: {user_details.get('job_title', 'No current role specified')} at {user_details.get('company', 'No company information available')}"
    )
    print(f"- LinkedIn URL: {linkedin_url}")

    # Display the posts
    print("\nExtracted Posts:")
    for i, post in enumerate(posts, 1):
        print(f"Post {i}: {post['text']}")

    if posts:
        prompt = f"""
        LinkedIn Profile Analysis
        User Summary:
        - Name: {user_details.get('first_name', 'No first name available')} {user_details.get('last_name', 'No last name available')}
        - Profile Summary: {user_details.get('about', 'No summary available')}
        - Current Role: {user_details.get('job_title', 'No current role specified')} at {user_details.get('company', 'No company information available')}
        - Profile URL: {linkedin_url}
        Detailed Analysis Request:
        1. Analyze the technical content of the user's posts. Highlight any innovative ideas or significant contributions to the field of AI.
        2. Extract key phrases or important sentences that showcase the user's expertise and thought leadership.
        3. Assess the engagement levels of the posts (likes, comments, shares) to gauge influence and reach within the professional network.
        4. Identify any trends in the topics discussed over time and how they align with current industry trends.
        5. Evaluate the user's network growth and interactions to understand their community impact and collaborative efforts.
        Professional Interests:
        - List specific areas of AI and technology the user is interested in, based on post content and interactions.
        Skills & Expertise:
        - Detail technical skills, tools, and methodologies mentioned or implied in the user's posts.
        Professional Goals:
        - Infer potential career aspirations and professional development goals from the user's content and interactions.
        Recommendations for Growth:
        - Offer tailored advice for enhancing visibility, increasing engagement, and expanding technical expertise based on the user's current LinkedIn activity.
        Please structure your response with clear headings and bullet points for each section.
        """
        for i, post in enumerate(posts, 1):
            prompt += f"\nPost {i}: {post['text']}"

        analysis_results = generate_text(prompt)
        if analysis_results and "choices" in analysis_results:
            print("\nAnalysis Results:\n")
            for choice in analysis_results["choices"]:
                print(choice["message"]["content"])
        else:
            logging.error("Failed to generate analysis results.")
    else:
        logging.info("No posts found or no text available in posts.")


if __name__ == "__main__":
    main()
