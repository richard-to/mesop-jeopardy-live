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

## Screenshots

Here are some screenshots of the UI.

### Jeopardy board

<img width="1312" alt="Jeopardy" src="https://github.com/richard-to/mesop-jeopardy/assets/539889/bc27447d-129f-47ae-b0b1-8f5c546762ed">

### Jeopardy answer

<img width="1312" alt="Jeopardy Answer Modal" src="https://github.com/richard-to/mesop-jeopardy/assets/539889/46bbe312-8cf3-4ff7-8271-49692bd75dec">
