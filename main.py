import http.client
import urllib.parse
import json
import requests

# Constants
OPENROUTER_API_KEY = ""
YOUR_SITE_URL = "https://jeezai.com"
YOUR_APP_NAME = "JeezAI"


def get_linkedin_user_details(linkedin_url):
    encoded_url = urllib.parse.quote(linkedin_url, safe="")
    conn = http.client.HTTPSConnection("fresh-linkedin-profile-data.p.rapidapi.com")
    headers = {
        "X-RapidAPI-Key": "",
        "X-RapidAPI-Host": "fresh-linkedin-profile-data.p.rapidapi.com",
    }
    conn.request(
        "GET",
        f"/get-linkedin-profile?linkedin_url={encoded_url}&include_skills=false",
        headers=headers,
    )
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    return json.loads(data)


def get_linkedin_posts(linkedin_url):
    encoded_url = urllib.parse.quote(linkedin_url, safe="")
    conn = http.client.HTTPSConnection("fresh-linkedin-profile-data.p.rapidapi.com")
    headers = {
        "X-RapidAPI-Key": "",
        "X-RapidAPI-Host": "fresh-linkedin-profile-data.p.rapidapi.com",
    }
    conn.request(
        "GET",
        f"/get-profile-posts?linkedin_url={encoded_url}&type=posts",
        headers=headers,
    )
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    return json.loads(data)


def generate_text(prompt):
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
    return response.json()


def main():
    linkedin_url = input("Please enter the LinkedIn profile URL: ")
    user_details = get_linkedin_user_details(linkedin_url)
    posts_data = get_linkedin_posts(linkedin_url)
    posts = posts_data.get("data", [])

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
        if "choices" in analysis_results:
            print("\nAnalysis Results:\n")
            for choice in analysis_results["choices"]:
                print(choice["message"]["content"])
        else:
            print("Failed to generate analysis results.")
    else:
        print("No posts found or no text available in posts.")


if __name__ == "__main__":
    main()
