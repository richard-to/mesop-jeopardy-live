---
title: Mesop Jeopardy Live
emoji: 🤓
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# Mesop Jeopardy Live

Simple jeopardy game built using [Mesop](https://google.github.io/mesop/) and the
[Gemini Multimodal Live API](https://ai.google.dev/api/multimodal-live).

This version is based on the [Mesop Jeopardy](https://github.com/richard-to/mesop-jeopardy)
which used the regular Gemini 1.5 Pro API.

The difference is that this version uses audio input and output to play the game. You
can still select clues by clicking on the boxes and typing your answers. But now you can
use your voice to do the same thing.

One thing to note is that you should use headphones since noise cancellation from
speakers does not work well.

It should also be noted that the system instructions still need a lot of work. Gemini
does not consistently use the custom tool calls correctly.

In order to run the app, you will need a Google API Key Pro. You can create
one using the instructions at https://ai.google.dev/gemini-api/docs/api-key.

```
git clone git@github.com:richard-to/mesop-jeopardy-live.git
cd mesop-jeopardy-live
pip install -r requirements.txt
GOOGLE_API_KEY=<your-api-key> mesop main.py
```

You can try out a demo here on [Hugging Face Spaces](https://huggingface.co/spaces/richard-to/mesop-jeopardy-live).

## Notes on the Jeopardy questions dataset

One thing to note is I haven't included the jeopardy.json file. I'm using an old dataset
of 200K questions that's about 10 years old now. You can find it with a quick Google
search.

The file needs to be added to the data folder and named jeopardy.json. The format is
like this

```
{
  "category": "HISTORY",
  "air_date": "2004-12-31",
  "question": "'For the last 8 years of his life, Galileo was...",
  "value": "$200",
  "answer": "Copernicus",
  "round": "Jeopardy!",
  "show_number": "4680"
}
```

### LLM Generated questions

You can also use LLMs to generate a question set using `scripts/generate_clues.py`. It
will generate a file called `sample_data/custom_jeopardy.json`.

Here is a basic example using some LLM-generated categories that I copy and pasted into
`scripts/categories.txt`. The script is a bit slow since it generates questions for one
category at a time and throttles itself to 15 RPM to stay within the limits of Gemini
1.5 Flash. A future improvement could be to generate batches of questions.

```
cd scripts
python generate_clues.py --file categories.txt --dataset ../data/custom_jeopardy.json --overwrite
```

If you're using a custom dataset, you can an environment variable to specify the
location of the file.

```
JEOPARDY_DATASET_PATH=data/custom_jeopardy.json
```

## Screenshots

Here are some screenshots of the UI.

### Initial game board

<img width="1312" alt="Screenshot 2025-01-26 at 2 03 35 PM" src="https://github.com/user-attachments/assets/329b07c9-7695-4e7a-92be-54f5f6948be2" />

### Jeopardy answer

<img width="1312" alt="Screenshot 2025-01-26 at 2 04 05 PM" src="https://github.com/user-attachments/assets/97d704e1-6df6-4a05-8a77-8e91363295fa" />
