import json

from openai import OpenAI

from app.config.settings import settings
from app.extraction.schema import ExtractedApplicationData


_client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)


SYSTEM_PROMPT = """
You extract structured job-application information from emails.

Your job is to identify only information that is explicitly supported by
the email. Never invent, guess, or infer missing company names, roles,
dates, locations, or other fields.

OUTPUT FORMAT IS STRICT:

Return exactly ONE JSON OBJECT representing ONE email.

The JSON object MUST contain these fields:

{
  "company": string or null,
  "role": string or null,
  "location": string or null,
  "employment_type": string or null,
  "event_type": string or null,
  "event_date": "YYYY-MM-DD" or null,
  "deadline": "YYYY-MM-DD" or null,
  "application_status": string or null,
  "source": string or null,
  "confidence": number
}

Do NOT return:
- an array
- {"jobs": [...]}
- {"applications": [...]}
- {"results": [...]}
- multiple objects
- markdown
- explanations
- any wrapper object

The response must represent ONLY the single email provided by the user.

Event types:

- APPLICATION_SUBMITTED:
  Use only when the email itself provides evidence that the candidate
  actually submitted an application at that point in the conversation.

  Do NOT use APPLICATION_SUBMITTED merely because:
  - the email discusses an application,
  - the email refers to a previous application,
  - the candidate is following up about an application,
  - the sender asks the candidate to apply or resubmit,
  - the subject contains "Application",
  - the email discusses application problems or verification.

  If the email discusses an existing application without confirming that
  a new application was actually submitted, use FOLLOW_UP instead.

- APPLICATION_RECEIVED:
  Use when an employer or recruiting system explicitly confirms that an
  application was received or successfully submitted.

  This should represent a confirmation of receipt, not merely a request
  to submit or resubmit an application.

- ASSESSMENT_REQUESTED:
  Use when the candidate is asked to complete an assessment, test, coding
  challenge, or similar evaluation.

- INTERVIEW_INVITED:
  Use when the candidate is invited to an interview.

- INTERVIEW_COMPLETED:
  Use when the email clearly indicates that an interview has taken place.

- REJECTION:
  Use when the candidate is informed that they were rejected or will not
  continue in the hiring process.

- OFFER:
  Use when the candidate receives a job offer.

- WITHDRAWN:
  Use when the candidate withdraws their application.

- FOLLOW_UP:
  Use when the email concerns an existing application or hiring process
  but does not itself confirm a new application submission, application
  receipt, assessment request, interview, rejection, offer, or withdrawal.

  Examples include:
  - asking about application status
  - discussing phone verification
  - troubleshooting an existing application
  - recruiter communication about an existing application
  - asking the candidate to resubmit an application
  - discussing an application without confirming a new submission

- JOB_ALERT:
  Use when the email is a job posting, job recommendation, hiring alert,
  or job opportunity notification and there is no evidence that the
  candidate applied for the position.

- OTHER:
  Use when the email is job-related but does not fit the categories above.

Important rules:

1. Do not classify a job advertisement or LinkedIn job alert as
   APPLICATION_SUBMITTED or APPLICATION_RECEIVED merely because it contains
   words such as "hiring", "apply", or "application".

2. A job alert should normally have event_type = JOB_ALERT.

3. Do not classify an email as APPLICATION_SUBMITTED just because the email
   mentions that an application exists or discusses a previous submission.

4. A request to apply or resubmit is NOT proof that the candidate actually
   submitted the application. Use FOLLOW_UP unless the email explicitly
   confirms that the candidate completed the submission.

5. If an email is a follow-up about an existing application, prefer
   FOLLOW_UP unless there is explicit evidence for a more specific event.

6. Do not invent a company name. If the company is not explicitly
   identifiable from the email, return null.

7. Do not invent a role. If the role is not explicitly identifiable,
   return null.

8. The source should only be populated when the email explicitly identifies
   a platform, job board, recruiting system, or company system, such as
   Mercor, Greenhouse, LinkedIn, Indeed, or a clearly identified domain.

9. Do not use "email" as the source.

10. For dates, only extract a date when the email provides enough
    information to identify it reliably.

11. event_date and deadline MUST use the format YYYY-MM-DD.
    Do not return timestamps or datetime strings.

12. Confidence must be between 0.0 and 1.0.

13. Return ONLY the single JSON object for this email.
"""


def extract_application_data(
    sender: str,
    subject: str,
    body_text: str,
    received_at: str | None = None,
) -> ExtractedApplicationData:
    user_prompt = f"""
Extract job-related information from this single email.

Return exactly ONE JSON object matching the required schema.

For event_date and deadline, use YYYY-MM-DD only.
Never return a timestamp for these fields.

Sender:
{sender}

Subject:
{subject}

Received at:
{received_at}

Body:
{body_text}
"""

    response = _client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("LLM returned an empty response")

    data = json.loads(content)

    # Normalize datetime strings to plain dates before Pydantic validation.
    for field in ("event_date", "deadline"):
        value = data.get(field)

        if isinstance(value, str) and "T" in value:
            data[field] = value.split("T")[0]

    return ExtractedApplicationData.model_validate(data)