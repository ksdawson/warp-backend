import json
import random
from openai import OpenAI
from datetime import datetime

def generate_response(prompt, context):
    format = '{ monthYear: { roleCity: count } }'
    full_prompt = (
        f'Generate a headcount hiring plan for this user prompt and context. '
        f'Output should be in JSON in the given format. '
        f'Prompt: {prompt}. '
        f'Context: {context}. '
        f'Format: {format}'
    )

    client = OpenAI()
    response = client.responses.create(
        model="gpt-5.2",
        input=full_prompt
    )

    return response.output_text


def generate_debug_response(context):
    """
    Generate a random but valid hiring plan from context.
    Context shape (from frontend):
    {
      startDate: "2026-01",
      endDate: "2026-06",
      roles: [{ role: "developer", city: "NYC" }, ...]
    }
    """

    def parse_month(date_str):
        return datetime.strptime(date_str[:7], "%Y-%m")

    start = parse_month(context["startDate"])
    end = parse_month(context["endDate"])

    months = []
    current = start
    while current <= end:
        months.append(current.strftime("%b %Y"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    plan = {}

    for month in months:
        month_plan = {}

        # randomly decide how many roles appear this month
        num_roles = random.randint(0, len(context["roles"]))

        for role_entry in random.sample(context["roles"], k=num_roles):
            role_city = f'{role_entry["role"]}-{role_entry["city"]}'
            month_plan[role_city] = random.randint(1, 3)

        if month_plan:
            plan[month] = month_plan

    return json.dumps(plan)


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
    except Exception:
        return {
            "statusCode": 400,
            "body": "Invalid JSON"
        }

    if "prompt" not in body:
        return {
            "statusCode": 400,
            "body": "Missing prompt"
        }

    if "context" not in body:
        return {
            "statusCode": 400,
            "body": "Missing context"
        }

    prompt = body["prompt"]
    user_context = body["context"]
    debug = body.get("debug", False)

    try:
        if debug:
            response = generate_debug_response(user_context)
        else:
            response = generate_response(prompt, user_context)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": response
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": "Request failed"
        }
