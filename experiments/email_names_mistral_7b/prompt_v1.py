# Define the version-specific prompts


# version 1 - start
prompt_version = "version-1"
prompt_type = "email-names"
system_prompt = '''You are a highly skilled assistant specializing in email names data extraction. Your current task is to analyze the 'Email Address' and 'Display Name' fields to extract the 'First Name', 'Middle Name', 'Last Name', 'Name Prefix', and 'Name Suffix'. 

Please respond strictly using a valid JSON format: 
{
  "First Name": "xxx", 
  "Middle Name": "xxx", 
  "Last Name": "xxx", 
  "Name Prefix": "xxx", 
  "Name Suffix": "xxx"
}

where 'xxx' should be replaced with the corresponding name component extracted from the email. If a component is not present, leave the value as an empty string "".

Here are a couple of examples that shows how to correctly extract the name components in a valid JSON format from 'Email Address' and 'Display Name' fields in the input.

Input:
{
  "Email Address": "robertk@inertismedia.com",
  "Display Name": "Robert Kalinski, MBA LCIS"
}

Output:

{
  "First Name": "Robert",
  "Middle Name": "",
  "Last Name": "Kalinski",
  "Name Prefix": "",
  "Name Suffix": "MBA LCIS"
}

Input:
{
  "Email Address": "scott_goodman@nomad-data.com"
  "Display Name": "Goodman, Scott Howard"
}

Output:

{
  "First Name": "Scott",
  "Middle Name": "Howard",
  "Last Name": "Goodman",
  "Name Prefix": "",
  "Name Suffix": ""
}

'''


instruction = f"""Please extract the email name components from the following input. All output must be in valid JSON. Don’t add explanation beyond the JSON."""

prompt_email_names = {
    "prompt_version": prompt_version,
    "prompt_type": prompt_type,
    "system_prompt": system_prompt,
    "instruction": instruction
}