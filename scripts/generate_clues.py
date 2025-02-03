import json
import os
import typing
import time
from datetime import datetime
import random
import argparse

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Flash 1.5 has a requestion limit of 15 RPM
GENERATE_DELAY = 5
DEFAULT_JEOPARDY_DATA = "../data/custom_jeopardy.json"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Global variable to store the current dataset path
current_dataset_path = DEFAULT_JEOPARDY_DATA

genai.configure(api_key=GOOGLE_API_KEY)


class JeopardyQuestion(typing.TypedDict):
  clue: str
  answer: str
  value: str


question_gen_model = genai.GenerativeModel(
  "gemini-1.5-flash",
  generation_config=genai.GenerationConfig(
    temperature=1,
    top_p=0.95,
    top_k=64,
    response_mime_type="application/json",
    response_schema=list[JeopardyQuestion],
  ),
)


_JEOPARDY_QUESTION_GENERATE_PROMPT = """
You are a Jeopardy! expert who specializes in crafting great questions.

Generate Jeopardy! questions for the following category: {category}.

A Jeopardy! category has 5 questions of increasing difficulty. The values are $200,
$400, $600, $800, $1000.
""".strip()


def get_existing_categories() -> set[str]:
  """Get a set of all existing categories in the dataset."""
  try:
    with open(current_dataset_path, "r") as f:
      data = json.load(f)
      return {item["category"].lower() for item in data}
  except FileNotFoundError:
    return set()
  except json.JSONDecodeError:
    print(f"Warning: Error reading {current_dataset_path}. Treating as empty file.")
    return set()


def read_custom_jeopardy_questions_dataset():
  try:
    with open(current_dataset_path, "r") as f:
      return json.load(f)
  except FileNotFoundError:
    return []


def write_custom_jeopardy_questions_dataset(data, overwrite=False):
  """Write questions to the dataset file.

  Args:
      data: List of questions to write
      overwrite: If True, replace existing data. If False, append to existing data.
  """
  # Create directory if it doesn't exist
  os.makedirs(os.path.dirname(current_dataset_path), exist_ok=True)

  if overwrite:
    # In overwrite mode, simply write the new data
    with open(current_dataset_path, "w") as f:
      json.dump(data, f, indent=2)
    return

  # In append mode
  if not os.path.exists(current_dataset_path):
    # If file doesn't exist, create it with the new data
    with open(current_dataset_path, "w") as f:
      json.dump(data, f, indent=2)
    return

  try:
    # Read existing data
    with open(current_dataset_path, "r") as f:
      existing_data = json.load(f)

    # Append new data
    existing_data.extend(data)

    # Write combined data
    with open(current_dataset_path, "w") as f:
      json.dump(existing_data, f, indent=2)
  except json.JSONDecodeError:
    # If file is empty or invalid, just write new data
    with open(current_dataset_path, "w") as f:
      json.dump(data, f, indent=2)


def generate_questions_by_category(category) -> list[dict[str, str]]:
  """Generate Jeopardy questions for a category using Gemini.

  Returns:
      Generated jeopardy data set in the expected format.
  """
  time.sleep(5)
  questions = json.loads(
    question_gen_model.generate_content(
      _JEOPARDY_QUESTION_GENERATE_PROMPT.format(category=category)
    ).text
  )
  questions_list = []
  air_date = datetime.now().strftime("%Y-%m-%d")
  show_number = str(random.randint(1, 2000))
  # Format the questions like the data set.
  for question in questions:
    questions_list.append(
      {
        "question": question["clue"],
        "answer": question["answer"],
        "value": question["value"],
        "category": category,
        "air_date": air_date,
        "show_number": show_number,
        "round": "Jeopardy!",
      }
    )
  return questions_list


def print_questions(questions: list[dict[str, str]], category: str):
  """Print the generated questions in a readable format."""
  print(f"\nCategory: {category}\n")
  print("-" * 50)

  # Sort questions by value
  sorted_questions = sorted(
    questions, key=lambda x: int(x["value"].replace("$", "").replace(",", ""))
  )

  for q in sorted_questions:
    print(f"Value: {q['value']}")
    print(f"Question: {q['question']}")
    print(f"Answer: {q['answer']}")
    print("-" * 50)


def get_categories_from_input() -> list[str]:
  """Get multiple categories from user input."""
  categories = []
  print("Enter categories (one per line). Press Enter twice when done:")

  while True:
    category = input().strip()
    if not category:
      break
    categories.append(category)

  return categories


def read_categories_from_file(filename: str) -> list[str]:
  """Read categories from a text file, one category per line."""
  try:
    with open(filename, "r") as f:
      # Read lines and remove empty lines and whitespace
      categories = [line.strip() for line in f if line.strip()]
      return categories
  except FileNotFoundError:
    print(f"Error: File '{filename}' not found")
    return []
  except Exception as e:
    print(f"Error reading file: {e}")
    return []


def filter_existing_categories(categories: list[str]) -> list[str]:
  """Filter out categories that already exist in the dataset."""
  existing_categories = get_existing_categories()
  new_categories = []
  skipped_categories = []

  for category in categories:
    if category.lower() in existing_categories:
      skipped_categories.append(category)
    else:
      new_categories.append(category)

  if skipped_categories:
    print("\nSkipping the following existing categories:")
    for category in skipped_categories:
      print(f"- {category}")

  return new_categories


def main():
  parser = argparse.ArgumentParser(
    description="Generate Jeopardy questions for multiple categories"
  )
  group = parser.add_mutually_exclusive_group()
  group.add_argument(
    "--categories", nargs="+", type=str, help="List of Jeopardy categories to generate questions"
  )
  group.add_argument(
    "--file", type=str, help="Path to text file containing categories (one per line)"
  )
  parser.add_argument(
    "--overwrite", action="store_true", help="Overwrite existing questions instead of appending"
  )
  parser.add_argument(
    "--dataset", type=str, help=f"Path to the dataset file (default: {DEFAULT_JEOPARDY_DATA})"
  )
  args = parser.parse_args()

  # Set the dataset path
  global current_dataset_path
  if args.dataset:
    current_dataset_path = args.dataset
    print(f"Using custom dataset path: {current_dataset_path}")

  # Determine which source to use for categories
  if args.file:
    categories = read_categories_from_file(args.file)
    if not categories:
      print("No valid categories found in file. Exiting.")
      return
  elif args.categories:
    categories = args.categories
  else:
    categories = get_categories_from_input()

  if not categories:
    print("No categories provided. Exiting.")
    return

  # Filter out existing categories
  if not args.overwrite:
    categories = filter_existing_categories(categories)
    if not categories:
      print("\nAll categories already exist in the dataset. Nothing to do.")
      return

  print(f"\nPreparing to generate questions for {len(categories)} categories:")
  for i, category in enumerate(categories, 1):
    print(f"{i}. {category}")
  print()

  if args.overwrite:
    print("Warning: This will overwrite all existing questions!")
    confirm = input("Do you want to continue? (y/N): ")
    if confirm.lower() != "y":
      print("Operation cancelled.")
      return

  # If overwrite mode, initialize empty dataset
  if args.overwrite:
    write_custom_jeopardy_questions_dataset([], overwrite=True)
    print("Initialized empty dataset for overwrite mode")

  for i, category in enumerate(categories, 1):
    print(f"\nGenerating questions for category: {category} ({i}/{len(categories)})")
    try:
      questions = generate_questions_by_category(category)
      print_questions(questions, category)

      # Save after each category
      write_custom_jeopardy_questions_dataset(questions, overwrite=False)
      print(f"✓ Saved questions for {category}")

    except Exception as e:
      print(f"Error generating questions for {category}: {str(e)}")
      print("Skipping to next category...")
      continue

  print(f"\nCompleted processing {len(categories)} categories.")
  print(f"All generated questions have been saved to {current_dataset_path}")


if __name__ == "__main__":
  main()
