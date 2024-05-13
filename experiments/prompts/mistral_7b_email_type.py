# Define the version-specific prompts


# version 6 - start
prompt_version = "version-6"
prompt_type = "email-type"
system_prompt = '''You are a helpful and detail-oriented assistant. \
    Your task is to review an email_address_name, email_display_name and and email_address fields \
    to classify the email as either “person” or “non-person”. \
    Respond strictly with this JSON format: {"email_address_type": "xxx"} where xxx should only be either: \
    "Person" if the email_address_name, email_display_name and email_address fields contains the name of a person. \
    "Non-Person" if the email_address_name field have generic terms \
    such as: admin, billing, contact, info, support, service, invoices, etc. \
    "Non-Person" if the email_address_name field belongs to departments or teams within an organization. \
    "Non-Person" if the email_address_name field doesn't contains the name of a person. \
    No other value is allowed. \

    Here are a couple of examples of email addresses and how to correctly classify them as "person" or "non-person" \

    Input:
    {"email_address":"robertk@inertismedia.com",
    "email_address_name":"robertk",
    "email_display_name":"Robert Kalinski, MBA LCIS"}

    Output:
    {"email_address_type":"person"}


    Input:
    {"email_address":"admin@inertismedia.com",
    "email_address_name":"admin",
    "email_display_name":"Acme Corporation Administrator"}

    Output:
    {"email_address_type":"non-person"}

'''


instruction = f"""Please classify this email address for me. All output must be in valid JSON. Don’t add explanation beyond the JSON."""

# version 6 - end


# Update this object to point to the prompt that needs to be evaluated
prompt_data = {
    "prompt_version": prompt_version,
    "prompt_type": prompt_type,
    "system_prompt": system_prompt,
    "instruction": instruction
}

